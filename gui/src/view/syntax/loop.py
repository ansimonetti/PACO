import json
import dash_bootstrap_components as dbc
from dash import html
from gui.src.controller.example.render import render_example
from gui.src.env import IMPACTS, PROBABILITIES, LOOP_PROBABILITY
from gui.src.view.example.standard_layout import get_description


def get_loop_layout():
	with open("gui/src/assets/bpmn_loop.json", "r") as file:
		data = json.load(file)
	bpmn, bpmn_svg_base64 = render_example(data)

	return dbc.Card([
		dbc.CardHeader("Loop"),
		dbc.CardBody([
			dbc.Container([
				dbc.Row([
					dbc.Col(
						html.Div(
							get_description(bpmn,f'''
                            Is an Exclusive Gateway, that repeat a task until a nature randomly choose the outgoing path.
                            For instance, {list(bpmn[IMPACTS].keys())[0]} will be execute with an impacts of {str(list(bpmn[IMPACTS].values())[0]).strip("{}").replace("'", "")} and will be repeated with a probability of {list(bpmn[LOOP_PROBABILITY].values())[0]}.
                            ''', warning=True), style={'width': '100%', 'textAlign': 'left'}, className="mb-3"
						), width=5),
					dbc.Col(
						html.Div(
							html.Iframe(
								src=bpmn_svg_base64,
								style={"width": "100%", "height": "100%", "border": "none"}
							),
							style={
								"height": "300px",
								"border": "1px solid #eee"
							}
						)
						, width=7),
				], class_name="mb-4")
			], fluid=True)
		])
	], className="mb-3")
