import dash
from dash import html, dcc, Input, Output,State, callback
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.express as px

from utils import check_syntax as cs
from utils import automa as at
from utils.env import ALGORITHMS, TASK_SEQ, IMPACTS, H, DURATIONS
from utils.print_sese_diagram import print_sese_diagram

dash.register_page(__name__, path='/')
# SimpleTask1, Task1 || Task, rjfgkn ^ Task9
bpmn_lark = {
    TASK_SEQ: 'SimpleTask, hello',
    H: 0,
    IMPACTS: {},
}
min_duration = 0
max_duration = 100
value_interval = [min_duration, max_duration]
marks = {j: str(j) for j in range(min_duration, int(max_duration), 10) if j != 0}
data = {
    'Task': bpmn_lark[TASK_SEQ],
    'Duration': dcc.RangeSlider(
        id=f'range-slider-',
        min=min_duration,
        max=max_duration,
        value=value_interval,
        marks=marks
    )
}

width = 500
height  = 250
margin = dict(l=0, r=0, t=0, b=0)
color = "rgba(0,0,0,0)"
img = print_sese_diagram(**bpmn_lark)
fig = px.imshow(img=img)
fig.update_layout(width=width, height=height, margin=margin, paper_bgcolor=color)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)

def layout():
    return html.Div([
        html.Div(id='logging'),
        html.Div(id='logging-strategy'),
        ############################
        ### DEFINING THE BPMN + DCPI
        ##############################
        html.H1('Insert your BPMN file here:'),
        #dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select Files')]), multiple=False), # Drag and drop per file ma da usapre più avanti
        html.P("""Here is an example of a BPMN complete diagram with impacts and duration: {
            'expression':'Task1, Task2,Task3',
            'impacts': {"Task1":  {"cost": 10, "working_hours": 12}, "Task2":  {"cost": 8, "working_hours": 6}, "Task3":  {"cost": 18, "working_hours": 5} },
        }"""),
        html.Br(),
        dcc.Textarea(value=bpmn_lark[TASK_SEQ], id = 'input-bpmn', style={'width': '100%'}), # persistance è obbligatoria altrimenti quando ricarica la pagina (cioè ogni valta che aggiorna il graph lark-diagram)
        html.P('Insert the duration of the tasks:'),
        html.Div(id='task-duration'),
        dbc.Table.from_dataframe(
            pd.DataFrame(data),
            id = 'durations-task-table',
            style = {'width': '100%', 'textAlign': 'center'}
        ),
        html.P('Insert the impacts of the tasks in the following format: {"SimpleTask":  {"cost": 10, "working_hours": 12}, "Task3":  {"cost": 18, "working_hours": 5} }. The values have to be integeres and only 1 value is allowed.'),
        html.Div(id='impacts'),
        dcc.Textarea(value='',  id = 'input-impacts', persistence=True, style={'width': '100%'}),
        html.Br(),
        html.Button('Create diagram', id='create-diagram-button'),
        #####################
        ### BPMN DIAGRAM USING LARK
        ########################
        html.Div([
            html.H3("BPMN diagram in lark:"),
            dcc.Graph(id='lark-diagram', figure=fig),
        ]),
        html.Br(),
        ############################
        ### STRATEGY
        ##############################
        html.Div(id="strategy", children=[
            html.H1("Choose the strategy to use:"),
            dcc.Dropdown(
                id='choose-strategy',
                options=[
                    {'label': value, 'value': key}
                    for key, value in ALGORITHMS.items()
                ],
                value= list(ALGORITHMS.keys())[0] # default value
            ),
            html.P('Insert the bound dictionary -it has to correspond to the impact dictionary- : {"cost": 10, "working_hours": 12}'),                        
            html.Div(id= 'choose-bound-dict'),
            html.Br(),
            html.Br(),
            html.Button('Find strategy', id='find-strategy-button'),
            html.Div(id='strategy-founded')
        ]),
        html.Br(),
        html.Br(),
    ])
                


#######################

## FIND THE STRATEGY

#########################
@callback(
    [Output('strategy-founded', 'children'), Output('logging-strategy', 'children')],
    Input('find-strategy-button', 'n_clicks'),
    State('choose-strategy', 'value'),
    State('choose-bound-dict', 'children'),
    prevent_initial_call=True
)
def find_strategy(n_clicks, algo:str, bound:dict):
    """This function is when the user search a str."""
    if bound == {} or bound == None:
        return [html.P(f'Insert a bound dictionary to find the strategy.'),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody("Insert a bound dictionary to find the strategy."),
                    ],
                    id="modal",
                    is_open=True,
                ),
            ]
    if cs.checkCorrectSyntax(**bpmn_lark) and cs.check_algo_is_usable(bpmn_lark[TASK_SEQ],algo):
        finded_strategies = at.calc_strat(bpmn_lark, bound, algo)
        if finded_strategies == {}:
            return [None,
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Strategy not found"),  class_name="bg-info"),
                        dbc.ModalBody("No strategy found for the given bound. Try with another bound."),
                    ],
                    id="modal",
                    is_open=True,
                ),
            ]
        elif finded_strategies.get('error') != None:
            return [None,
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody(f"Error while calculating the strategy: {finded_strategies.get('error')}"),
                    ],
                    id="modal",
                    is_open=True,
                ),
            ]
        else:
           return html.P(f'Strategies: {finded_strategies[list(finded_strategies.keys())[0]]},,,,,, ')
    else:
        return [None,
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody("Seems that your diagram is too complex for this algorithm. Please check your syntax or try with another algorithm."),
                    ],
                    id="modal",
                    is_open=True,
                ),
            ]


#######################

## UPDATE THE BPMN DIAGRAM

#########################

@callback(
    [Output('lark-diagram', 'figure'), Output('logging', 'children')],
    Input('create-diagram-button', 'n_clicks'),
    State('input-bpmn', 'value'),
    State('input-impacts', 'value'),
    State('durations-task-table', 'children'),
    prevent_initial_call=True,
)
def create_sese_diagram(n_clicks, task , impacts= {}, durations = {}):
    #check the syntax of the input if correct print the diagram otherwise an error message
    try:
        bpmn_lark[TASK_SEQ] = task
        # bpmn_lark[H] = 0
        bpmn_lark[IMPACTS] = cs.extract_impacts_dict(impacts)
        bpmn_lark[DURATIONS] = cs.create_duration_dict(task=task, durations=durations)
    except Exception as e:
        print(f'Error while parsing the bpmn: {e}')
        return [ None,# dbc.Alert(f'Error while parsing the bpmn: {e}', color="danger")]
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
            ]
    if cs.checkCorrectSyntax(**bpmn_lark):

        print(bpmn_lark[IMPACTS])
        try:
            # Create a new SESE Diagram from the input
            img = print_sese_diagram(**bpmn_lark)
            fig = px.imshow(img=img)
            fig.update_layout(width=width, height=height, margin=margin, paper_bgcolor=color)
            fig.update_xaxes(showticklabels=False)
            fig.update_yaxes(showticklabels=False)
            return [fig , None]
        except Exception as e:
            return [None, #dbc.Alert(f'Error while creating the diagram: {e}', color="danger")
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                            dbc.ModalBody(f'Error while creating the diagram: {e}'),
                        ],
                        id="modal",
                        is_open=True,
                    ),
                ]
    else:
        return  [None, #dbc.Alert(f'Error in the syntax! Please check the syntax of the BPMN diagram.', color="danger")
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody("Error in the syntax! Please check the syntax of the BPMN diagram."),
                    ],
                    id="modal",
                    is_open=True,
                ),
                ]

#######################

## ADD TASK durations

#######################

@callback(
    Output('durations-task-table', 'children'), 
    Input('input-bpmn', 'value')
)
def add_task(tasks_):
    """
    This function takes a list of tasks and adds a range slider for each task's duration.
    The range slider allows the user to select a duration for each task.
    The function is decorated with a callback that updates the 'durations-task-table' component
    whenever the 'input-bpmn' value changes.

    Parameters:
    tasks_ (list): The list of tasks.

    Returns:
    list: A list of dictionaries, where each dictionary represents a task and its associated range slider.
    """
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []

    # Extract the tasks from the input
    tasks_list = cs.extract_tasks(tasks_)

    # Initialize an empty list to store the task data
    task_data = []

    # Iterate over the tasks
    for i, task in enumerate(tasks_list):
        # For each task, append a dictionary to the task data list
        # The dictionary contains the task name and a range slider for the task's duration
        task_data.append({
            'Task': task,
            'Duration': dcc.RangeSlider(
                id=f'range-slider-{i}',
                min=min_duration,
                max=max_duration,
                value=value_interval,
                marks=marks,
                tooltip={
                    "placement": "bottom",
                    "always_visible": True,
                }
            )
        })

    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the 'durations-task-table' component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'durations-task-table',
        style = {'width': '100%', }
    )


#######################

## ADD BOUND

#######################

@callback(
    Output('choose-bound-dict', 'children'),
    Input('create-diagram-button', 'n_clicks'),
    State('input-impacts', 'value'),
)
def add_task(n_clicks, impacts):
    """
    This function takes the number of button clicks and a string of impacts.
    It converts the string of impacts into a dictionary and normalizes it.
    Then, it creates a list of unique impacts and generates a table where each row contains an impact and an input field.
    The function is decorated with a callback that updates the 'choose-bound-dict' component
    whenever the 'create-diagram-button' is clicked and the 'input-impacts' value changes.

    Parameters:
    n_clicks (int): The number of button clicks.
    impacts (str): The string of impacts.

    Returns:
    dbc.Table: A table where each row contains an impact and an input field.
    """
    # If no impacts are provided, return None
    if impacts == '' or impacts == None:
        return None

    # Convert the string of impacts into a dictionary and normalize it
    impacts = cs.string_to_dict(impacts)
    impacts = cs.normalize_dict_impacts(impacts)

    # Create a list of unique impacts
    impacts_list = list(set(impact for impact in list(impacts.values())[0]))

    # Initialize an empty list to store the task data
    task_data = []

    # Iterate over the impacts
    for i, task in enumerate(impacts_list):
        # For each impact, append a dictionary to the task data list
        # The dictionary contains the impact and an input field for the impact
        task_data.append({
            'Impacts': task,
            'Set Input': dcc.Input(
                id=f'range-slider-{i}',
                type='number',
                value=10,
                min= min_duration,
            )
        })

    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the 'choose-bound-dict' component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-bound-dict-df',
        style = {'width': '100%', 'textalign': 'center'}
    )