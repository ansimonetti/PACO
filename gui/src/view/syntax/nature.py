import json
import dash_bootstrap_components as dbc
from dash import html
from gui.src.controller.example.render import render_example
from gui.src.env import IMPACTS, PROBABILITIES
from gui.src.view.example.standard_layout import get_description


def get_nature_layout():
	with open("gui/src/assets/bpmn_nature.json", "r") as file:
		data = json.load(file)
	bpmn, bpmn_svg_base64 = render_example(data)

	return dbc.Card([
		dbc.CardHeader("Nature"),
		dbc.CardBody([
			dbc.Container([
				dbc.Row([
					dbc.Col(
						html.Div(
							get_description(bpmn,f'''
                            Is an Exclusive Gateway, which means that only one of the outgoing flows is followed, in the case of the nature with a specific probability.
                            For instance, {list(bpmn[IMPACTS].keys())[0]} can be execute with a probability of {list(bpmn[PROBABILITIES].values())[0]} and an impacts of {str(list(bpmn[IMPACTS].values())[0]).strip("{}").replace("'", "")} or {list(bpmn[IMPACTS].keys())[1]} with a probability of {1-list(bpmn[PROBABILITIES].values())[0]} an impacts of {str(list(bpmn[IMPACTS].values())[1]).strip("{}").replace("'", "")}.
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
