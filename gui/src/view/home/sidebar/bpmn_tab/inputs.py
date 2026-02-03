from dash import html, dcc
import dash_bootstrap_components as dbc
from gui.src.view.home.sidebar.bpmn_tab.table.new_impact_button import get_new_impact_button

def get_bpmn_view():
	return html.Div([
		dbc.Card(
			[
				dbc.CardHeader(
					html.Div([
						html.H5("Expression", className="mb-0"),
					], style={"textAlign": "left"})
				),
				dbc.CardBody([
					dcc.Input(type="text", debounce=True, id='expression-bpmn', style={'width': '100%', 'height': '48px', 'marginBottom': '10px'}, value=''),
					dbc.Button("Generate BPMN", id="generate-bpmn-btn", color="primary", size="sm", style={"width": "100%"})
				])
			],
			style={"width": "100%", "marginBottom": "1rem"}
		),
		html.Div(id='task-impacts-table'),
		html.Div(id='task-durations-table'),
		html.Div(id='choice-table'),
		html.Div(id='nature-table'),
		html.Div(id='loop-table'),
	], style={
		"display": "flex",
		"gap": "20px",
		"flexWrap": "wrap",
		"justifyContent": "center"
	})

