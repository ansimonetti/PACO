import dash_bootstrap_components as dbc
from dash import html, dcc
from gui.src.env import sese_diagram_grammar


def get_syntax_layout():
    return dbc.Card([
        dbc.CardHeader("Syntax and Basic Components"),
        dbc.CardBody([
            dbc.Container([
                dbc.Row([
                    dbc.Col(
                        html.Div(
                            dcc.Markdown(
'''In the following section, you can check the syntax of an BPMN+CPI expression and the basic components of the language together with useful examples. 
The BPMN+CPI language is transformed in a lark grammar and the syntax is checked using the lark parser.
The tasks is the atomix element of the BPMN+CPI language, and it is used to represent the work that needs to be done.
Is possible to concatenate the tasks or to use a gateway to control the flow of the process.
The gateways are used to control the flow of the process. They are used to merge or split the flow of the process.
A Gateway represents an intersection where multiple paths converge or diverge. Type of gateway:
- Exclusive: splits the flow in different paths and only one is chosen given a certain condition. There are more than one type:
  - Choice: free choice between the outgoing flows. We want to determine which path to take.
  - Nature: used to choose a path with a certain probability.
  - Loops: used to repeat a task until a nature randomly choose the outgoing path.
- Parallel (+) : all the outgoing flows are followed and in the merging all the activities of the incoming flows must be completed before continuing with the process.
                                ''', style={"marginBottom": "5px"}
                            ), style={'width': '100%', 'textAlign': 'left'}, className="mb-3"
                        ), width=6),
                    dbc.Col(
                        html.Div(
							dbc.Card([
								dbc.CardHeader("Grammar"),
								dbc.CardBody(
									dcc.Markdown(
										str(sese_diagram_grammar),
										style={"marginBottom": "5px"}
									)
								)
							])
							, style={'width': '100%', 'textAlign': 'left'}, className="mb-3"
                        ), width=6),
                ], class_name="mb-4")
            ], fluid=True)
        ])], className="mb-3")