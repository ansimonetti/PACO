import dash_bootstrap_components as dbc
from dash import html

from gui.src.env import IMPACTS_NAMES
from gui.src.view.example.first_example.strategy_example import get_strategy_example, get_losing_strategy_example, \
	get_winning_strategy_example
from gui.src.view.example.standard_layout import get_download_layout, get_description, get_render_example


def get_first_example(id, bpmn, bpmn_dot, example_key=None):
	return dbc.Card([
		dbc.CardHeader("Example of BPMN+CPI"),
		dbc.CardBody([
			dbc.Container([
				dbc.Row([
					dbc.Col([
						html.Div([
							get_description(bpmn, '''The BPMN diagram (shown in figure) depicts a metal manufacturing process that involves cutting, milling, bending, polishing, deposition, and painting a metal piece.''', warning=True, impacts=True)
						], style={'width': '100%', 'textAlign': 'left'}
						)
					], width=4),
					dbc.Col(get_render_example(bpmn_dot, id), width=8)
				], class_name="mb-4"),

				dbc.Row([
					dbc.Col([
						get_strategy_example(),
						get_losing_strategy_example(),
						get_winning_strategy_example(),
						get_download_layout(id + "-download",
							f'''Now it’s your turn!
								Download the BPMN JSON file and try to find a winning strategy that respects the expected impact bound [135, 15],
								respectively for [{', '.join(bpmn[IMPACTS_NAMES])}].
							''',
							example_key=example_key)
					], width=12)
				])

			], fluid=True)
		])])


