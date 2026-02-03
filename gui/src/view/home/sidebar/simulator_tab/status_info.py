import dash_bootstrap_components as dbc
from dash import html


def status_info():
        return dbc.Card([
                dbc.CardHeader(html.H5('Status Info')),
                dbc.CardBody(
                        html.Div(id="status-info-content", style={
                                "maxHeight": "250px",
                                "overflowY": "auto",
                                "overflowX": "hidden",
                                "padding": "0.5rem"
                        })
                )
        ], className="mb-3", style={
                "minWidth": "370px",
                "width": "100%"
        })


def make_table_card(title, dictionary):
	names = sorted(dictionary.keys())

	header_row = html.Tr([
		html.Th(name, style={
			"whiteSpace": "nowrap",
			"overflow": "hidden",
			"textOverflow": "ellipsis",
			"maxWidth": "80px"
		}) for name in names
	])
	data_row = html.Tr([
		html.Td(str(dictionary[name])) for name in names
	])
	return dbc.Card([
		dbc.CardHeader(html.H6(title), style={"padding": "0.5rem 1rem", "marginBottom": "0px"}),
		dbc.CardBody([
			dbc.Table([
				html.Thead(header_row),
				html.Tbody([data_row])
			],
				bordered=True,
				striped=True,
				responsive=True,
				className="table-sm",
				style={"borderCollapse": "collapse", "marginBottom": "0px"})
		], style={"padding": "0.5rem 1rem"})
	], style={
		"minWidth": "250px",
		"marginBottom": "10px"
	})


def update_status_info(impacts, expected_impacts, time, probability):
	# Build unified impacts table
	impact_names = sorted(impacts.keys())
	header_row = html.Tr([html.Th("")] + [html.Th(name) for name in impact_names])
	impacts_row = html.Tr([html.Td(html.Strong("Impacts"))] + [html.Td(str(impacts.get(name, ""))) for name in impact_names])
	expected_row = html.Tr([html.Td(html.Strong("Expected"))] + [html.Td(str(expected_impacts.get(name, ""))) for name in impact_names])
	
	elements = [
		dbc.Row([
			dbc.Col(html.Div([
				html.Strong("Time: "),
				html.Span(id="execution-time", children=str(time))
			]), width=6),
			dbc.Col(html.Div([
				html.Strong("Probability: "),
				html.Span(id="execution-probability", children=str(round(probability * 100, ndigits=3)) + "%")
			]), width=6),
		], className="mb-3"),
		dbc.Row([
			dbc.Col(
				dbc.Table([
					html.Thead(header_row),
					html.Tbody([impacts_row, expected_row])
				], bordered=True, striped=True, size="sm", style={"marginBottom": "0", "width": "100%"}),
				width=12
			)
		], className="mb-2")
	]

	return html.Div(elements, style={"width": "100%"})


def task_status_table():
	"""Placeholder for the task status table, rendered outside Status Info card."""
	return html.Div(id="task-status-content", className="mb-3")


def update_task_status_table(task_statuses):
	"""Build the task status table content."""
	if not task_statuses:
		return html.Div()
	
	status_colors = {
		"Waiting": "secondary",
		"Active": "danger",
		"Completed": "success",
		"Skipped": "warning"
	}
	rows = []
	for task_name, status in sorted(task_statuses.items()):
		badge_color = status_colors.get(status, "info")
		rows.append(html.Tr([
			html.Td(task_name),
			html.Td(dbc.Badge(status, color=badge_color, className="ms-1"))
		]))
	
	return dbc.Table([
		html.Thead(html.Tr([html.Th("Task"), html.Th("Status")])),
		html.Tbody(rows)
	], bordered=True, striped=True, size="sm", style={"marginBottom": "0", "width": "100%"})