import dash_bootstrap_components as dbc
from dash import html
from gui.src.env import IMPACTS_NAMES
from gui.src.view.home.sidebar.bpmn_tab.table.new_impact_button import get_new_impact_button
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import get_duration_table_header, get_duration_table_row
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import get_impacts_table_header, get_impacts_table_row

# Old table with duration and impacts

def create_tasks_table(bpmn_store, tasks):
	if len(tasks) == 0:
		return html.Div()

	rows = []
	for task in sorted(tasks):
		rows.append(
			html.Tr(get_duration_table_row(task, bpmn_store) + get_impacts_table_row(task, bpmn_store))
		)

	header_rows = [
		html.Tr([
			html.Th(html.H3("Tasks"), rowSpan=2, style={'verticalAlign': 'middle'}),
			html.Th("Duration", colSpan=2, style={'verticalAlign': 'middle', 'textAlign': 'center'}),
		] + ([html.Th("Impacts", colSpan=len(bpmn_store[IMPACTS_NAMES]), style={'verticalAlign': 'middle', 'textAlign': 'center'})]))
	]

	if bpmn_store[IMPACTS_NAMES]:
		header_rows.append(
			html.Tr(get_duration_table_header() + get_impacts_table_header(bpmn_store))
		)
	else:
		header_rows.append(
			html.Tr(get_duration_table_header())
		)

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
		"display": "inline-block",
		"padding": "10px",
		"border": "1px solid #ccc",
		"borderRadius": "10px",
		"marginTop": "20px"
	})])

	return html.Div([table, html.Br(),
					 get_new_impact_button(),
					 html.Br(),])
