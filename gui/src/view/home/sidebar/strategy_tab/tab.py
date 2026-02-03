import dash_bootstrap_components as dbc
from dash import dcc, html
from gui.src.env import ALGORITHMS

def get_strategy_tab():
	return dcc.Tab(label='Strategy', value='tab-strategy', style={'flex': 1, 'textAlign': 'center'}, children=[
		html.Div([
			dcc.Store(id="sort_store_guaranteed", data={"sort_by": None, "sort_order": "asc"}),
			dcc.Store(id="sort_store_possible_min", data={"sort_by": None, "sort_order": "asc"}),
			html.Div(id='strategy-alert'),
			get_strategy_input(),
			html.Div(id='strategy_output')
		], className="p-3 sidebar-box")
	])

def get_strategy_input():
	return html.Div([
		html.Div(children=[
				dbc.Card([
					dbc.CardHeader(
						html.Div([
							html.H5('Insert bound'),
							dbc.Button('Find strategy', id='find-strategy-button')],
							style={
								"display": "flex",
								"gap": "20px",
								"justifyContent": "space-between",
								"alignItems": "center"
							}
						)
					),
					dbc.CardBody([
						html.Div([
							html.H5("Algorithm:", style={"marginRight": "10px"}),
							dcc.Dropdown(
								id='choose-strategy',
								options=[
									{'label': value, 'value': key}
									for key, value in ALGORITHMS.items()
								],
								value=list(ALGORITHMS.keys())[0],
								style={"minWidth": "200px"}
							)
						],
							style={
								"display": "flex",
								"gap": "10px",
								"alignItems": "center",
								"flexWrap": "wrap"
							}),
						html.Div(id='bound-table')
					])
				], className="mb-3", style={"minWidth": "370px", "width": "100%"}),
				html.Br(),
			])
		], style={
		"display": "flex",
		"gap": "20px",
		"flexWrap": "wrap",
		"justifyContent": "center"
	})
