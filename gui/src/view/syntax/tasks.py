import json

import dash_bootstrap_components as dbc
from dash import html

from gui.src.controller.example.render import render_example
from gui.src.view.example.standard_layout import get_description


def get_tasks_layout():
    with open("gui/src/assets/bpmn_two_sequential_tasks.json", "r") as file:
        data = json.load(file)
    bpmn, bpmn_svg_base64 = render_example(data)

    return dbc.Card([
        dbc.CardHeader("Tasks"),
        dbc.CardBody([
            dbc.Container([
                dbc.Row([
                    dbc.Col(
                        html.Div(
                            get_description(bpmn,'''
                            The tasks are the most basic element of a BPMN diagram. They represent the work that needs to be done.
                            To define a simple task it is sufficient to digit the name. In the example we have two sequential tasks, when the first one is completed, the second one starts.
                            Each task has also a duration and an impact factor.
							Duration is an interval that can be between two positive number.
							Impacts factors can be only positive and are cumulative.
                            ''', impacts=True), style={'width': '100%', 'textAlign': 'left'}, className="mb-3"
                        ), width=5),
                    dbc.Col(
                        html.Div(
                            html.Iframe(
                                src=bpmn_svg_base64,
                                style={"width": "100%", "height": "100%", "border": "none"}
                            ),
                            style={
                                "height": "180px",
                                "border": "1px solid #eee"
                            }
                        )
                    , width=7),
                ], class_name="mb-4")
            ], fluid=True)
        ])
    ], className="mb-3")
