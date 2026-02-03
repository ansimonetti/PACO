import json
import dash_bootstrap_components as dbc
from dash import html
from gui.src.controller.example.render import render_example
from gui.src.view.example.standard_layout import get_description


def get_parallel_layout():
	with open("gui/src/assets/bpmn_two_parallel_tasks.json", "r") as file:
		data = json.load(file)
	bpmn, bpmn_svg_base64 = render_example(data)

	return dbc.Card([
		dbc.CardHeader("Parallel"),
		dbc.CardBody([
			dbc.Container([
				dbc.Row([
					dbc.Col(
						html.Div(
							get_description(bpmn,'''
                            Tasks can be done in parallel. All the outgoing flows are followed and in the merging all the activities of the incoming flows must be completed before continuing with the process.
                            For instance, in the example we have two parallel tasks, when both are completed, the process continues.
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
