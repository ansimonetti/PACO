import dash_bootstrap_components as dbc
from dash import html
from gui.src.env import APP_NAME

def navbar(pathname):
	nav_items = [
		dbc.NavItem(dbc.Button("☰", id="toggle-sidebar", color="secondary", className="me-2")) if pathname == '/' else None,
		dbc.NavItem(dbc.NavLink("Home", href="/")),
		dbc.NavItem(dbc.NavLink("Syntax", href="/syntax")),
		dbc.NavItem(dbc.NavLink("Example", href="/example")),
		dbc.NavItem(dbc.NavLink("About", href="/about")),
		dbc.NavItem(dbc.NavLink("Installation and Usage", href="/installation_and_usage")),
	]

	nav_items = [item for item in nav_items if item is not None]

	return dbc.Navbar(
		dbc.Container([
			dbc.Nav(nav_items, navbar=True, className="me-auto"),
			html.Div(APP_NAME, style={"color": "white", "fontWeight": "bold", "fontSize": "20px"}),
		], fluid=True),
		color="primary",
		dark=True,	)