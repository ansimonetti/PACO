import dash_bootstrap_components as dbc
from dash import html, dcc
from gui.src.env import DURATIONS


def get_duration_table_header():
	return [
		html.Th("Min", style={'width': '80px', 'verticalAlign': 'middle'}),
		html.Th("Max", style={'width': '80px', 'verticalAlign': 'middle'}),
	]


def get_duration_table_row(task, bpmn_store):
	if task not in bpmn_store[DURATIONS]:
		bpmn_store[DURATIONS][task] = (0, 1)

	(min_d, max_d) = bpmn_store[DURATIONS][task]

	return [
		html.Td(html.Span(task, style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "minWidth": "100px", "display": "inline-block"})),
		html.Td(dcc.Input(value=min_d, type='number', min=0, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"}, id={'type': 'min-duration', 'index': task})),
		html.Td(dcc.Input(value=max_d, type='number', min=0, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"}, id={'type': 'max-duration', 'index': task})),
	]


def create_tasks_duration_table(bpmn_store, tasks):
	if len(tasks) == 0:
		return html.Div()

	rows = []
	for task in sorted(tasks):
		rows.append(
			html.Tr(get_duration_table_row(task, bpmn_store))
		)

	header_rows = [html.Tr([
		html.Th(html.H3("Tasks"), rowSpan=2, style={'verticalAlign': 'middle'}),
		html.Th("Duration", colSpan=2, style={'verticalAlign': 'middle', 'textAlign': 'center'}),
	]), html.Tr(get_duration_table_header())]

	table = html.Div([html.Div([
		dbc.Table(
			[html.Thead(header_rows)] + rows,
			bordered=True,
			hover=True,
			responsive=True,
			striped=True,
			style={"width": "auto", "margin": "auto", "borderCollapse": "collapse"},
			className="table-sm"
		)
	], style={
		"padding": "10px",
		"border": "1px solid #ccc",
		"borderRadius": "10px",
		"marginTop": "20px",
		"maxHeight": "500px",
		"overflowY": "auto",
		"display": "block"
	})])

	return html.Div([table, html.Br()])
