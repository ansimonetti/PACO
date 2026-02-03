import dash_bootstrap_components as dbc
from dash import html

def render_table(headers, rows, include_button=False, button_prefix="", sort_by=None, sort_order="asc", table=None):
	table_rows = []

	indexed_rows = list(enumerate(rows))

	if sort_by in headers:
		idx = headers.index(sort_by)
		indexed_rows.sort(key=lambda r: r[1][idx], reverse=(sort_order == "desc"))

	for visible_index, (original_index, row) in enumerate(indexed_rows):
		cells = [html.Td(value) for value in row]
		if include_button:
			button_id = {"type": button_prefix, "index": visible_index, "table": table}

			button_value = list(row)

			cells.append(
				html.Td(
					dbc.Button(
						"Select",
						id=button_id,
						value=button_value,
						color="primary",
						size="sm"
					),
					style={"width": "70px", "textAlign": "center"}
				)
			)
		table_rows.append(html.Tr(cells))

	header_row = []
	for h in headers:
		arrow = "▲" if h == sort_by and sort_order == "asc" else "▼" if h == sort_by else ""
		header_row.append(
			html.Th(
				f"{h} {arrow}",
				id={"type": "sort-header", "column": h, "table": table},
				style={"cursor": "pointer", "userSelect": "none"}
			)
		)

	if include_button:
		header_row.append(html.Th())

	return html.Div(
		dbc.Table([
			html.Thead(html.Tr(header_row)),
			html.Tbody(table_rows)
		],
			bordered=True,
			hover=True,
			responsive=True,
			striped=True,
			className="mt-2"
		),
		style={"maxHeight": "400px", "overflowY": "auto"}
	)
