import dash_bootstrap_components as dbc
from dash import html, dcc
from gui.src.env import IMPACTS_NAMES, IMPACTS
from gui.src.view.home.sidebar.bpmn_tab.table.new_impact_button import get_new_impact_button


def get_impacts_table_header(bpmn_store):
	no_delete_button = len(bpmn_store[IMPACTS_NAMES]) < 2

	return [
		html.Th(html.Div([
			html.Span(
				name,
				style={
					"whiteSpace": "nowrap",
					"overflow": "hidden",
					"textOverflow": "ellipsis",
					"maxWidth": "80px",
					"display": "inline-block"
				}
			),
			dbc.Button(
				"×",
				id={'type': 'remove-impact', 'index': name},
				n_clicks=0,
				color="danger",
				size="sm",
				className="ms-1",
				style={"padding": "2px 6px"}
			) if not no_delete_button else None
		], style={
			'display': 'flex',
			'alignItems': 'center',
			'justifyContent': 'space-between'
		}))
		for name in sorted(bpmn_store[IMPACTS_NAMES])
	]


def get_impacts_table_row(task, bpmn_store):
	sorted_impacts_names = sorted(bpmn_store[IMPACTS_NAMES])

	if task not in bpmn_store[IMPACTS]:
		bpmn_store[IMPACTS][task] = {impact_name : 0.0 for impact_name in sorted_impacts_names}

	for s in sorted_impacts_names:
		if s not in bpmn_store[IMPACTS][task]:
			bpmn_store[IMPACTS][task][s] = 0.0

	return [
		html.Td(html.Span(task,
				style={"whiteSpace": "nowrap", "overflow": "hidden",
						"textOverflow": "ellipsis", "minWidth": "100px",
						"display": "inline-block"}))
		] + [
		html.Td(dcc.Input(
			value=bpmn_store[IMPACTS][task][impact_name],
			type='number', min=0.0, step=0.001, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"},
			id={'type': f'impact-{impact_name}', 'index': task}
		)) for impact_name in sorted_impacts_names]



def create_tasks_impacts_table(bpmn_store, tasks):
	if len(tasks) == 0:
		return html.Div()

	rows = []
	for task in sorted(tasks):
		rows.append(html.Tr(get_impacts_table_row(task, bpmn_store)))

	header_rows = [html.Tr([
		html.Th(html.H3("Tasks"), rowSpan=2, style={'verticalAlign': 'middle'}),
		html.Th("Impacts", colSpan=len(bpmn_store[IMPACTS_NAMES]),
				style={'verticalAlign': 'middle', 'textAlign': 'center'})
	]), html.Tr(get_impacts_table_header(bpmn_store))]

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

	return html.Div([table, html.Br(),
					 get_new_impact_button(),
					 html.Br(),])
