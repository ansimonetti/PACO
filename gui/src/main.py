import logging
from functools import lru_cache
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

from .env import APP_NAME, GUI_HOST, GUI_PORT
from .view.navbar import navbar
from .view.home.layout import layout as home_layout
from .view.syntax.layout import layout as syntax_layout
from .view.example.layout import layout as example_layout


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _discover_docs_dir() -> Path | None:
    start = Path(__file__).resolve()
    for ancestor in (start.parent, *start.parents):
        candidate = ancestor / "docs"
        if candidate.is_dir():
            logger.debug("Discovered docs directory at %s", candidate)
            return candidate

    logger.error("Unable to locate docs directory relative to %s", start)
    return None


def load_doc(name: str) -> dbc.Card | None:
    logger.debug("load_doc called with name=%r", name)
    slug = name.strip("/")
    logger.debug("Normalized slug=%r", slug)

    if slug == "about":
        slug = "index"
        logger.debug("Alias 'about' mapped to slug=%r", slug)

    if not slug:
        logger.info("Empty slug derived from name=%r; skipping markdown lookup", name)
        return None

    docs_dir = _discover_docs_dir()
    if docs_dir is None:
        logger.error("Docs directory could not be determined; unable to render markdown")
        return None

    doc_path = docs_dir / f"{slug}.md"
    logger.info("Looking for markdown document at %s", doc_path)

    if not doc_path.exists():
        logger.warning("Markdown document not found for slug=%r at %s", slug, doc_path)
        return None

    text = doc_path.read_text(encoding="utf-8")
    logger.info("Loaded markdown document for slug=%r", slug)

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]

    text = text.replace("{% include navbar.html %}", "")
    markdown = dcc.Markdown(text, dangerously_allow_html=True)
    return dbc.Card(dbc.CardBody(markdown))


app = dash.Dash(
    __name__,
    use_pages=False,
    pages_folder="",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

server = app.server
app.title = APP_NAME

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="navbar-container"),
        html.Div(id="page-content"),
    ]
)


@app.callback(
    Output("navbar-container", "children"),
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    original_pathname = pathname
    if not pathname:
        pathname = "/"

    if pathname != "/":
        normalized_path = pathname.rstrip("/")
        if normalized_path != pathname:
            logger.debug(
                "Trimmed trailing slash from pathname %r -> %r", pathname, normalized_path
            )
        pathname = normalized_path

    logger.info(
        "display_page handling request original=%r normalized=%r",
        original_pathname,
        pathname,
    )

    nav = navbar(pathname)

    if pathname == "/syntax":
        logger.info("Rendering syntax interactive layout for pathname=%r", pathname)
        return nav, syntax_layout()
    elif pathname == "/example":
        logger.info("Rendering example interactive layout for pathname=%r", pathname)
        return nav, example_layout()
    elif pathname == "/":
        logger.info("Rendering home layout for pathname=%r", pathname)
        return nav, home_layout()

    page = load_doc(pathname)
    if page is not None:
        logger.info("Rendering markdown page for pathname=%r", pathname)
        return nav, page

    logger.info("Markdown document not found; returning 404 for pathname=%r", pathname)
    return nav, html.Div(
        [
            html.H1("404 - Page not found"),
        ]
    )


if __name__ == "__main__":
    app.run(host=GUI_HOST, port=GUI_PORT)
