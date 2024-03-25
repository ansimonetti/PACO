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
    return dbc.Row(
            [
                dbc.Col(
                    
                    html.Div([
                    html.Div(id='logging'),
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
                    ]
                    )
                #, width=9
                ),
                # dbc.Col(
                #     html.Div(
                #         # [
                #         #     dbc.Button(
                #         #         "Open Logging",
                #         #         id="horizontal-collapse-button",
                #         #         className="mb-3",
                #         #         color="primary",
                #         #         n_clicks=0,
                #         #     ),
                #         #     html.Div(
                #         #         dbc.Collapse(
                #         #             dbc.Card(
                #         #                 dbc.CardBody(
                #         #                     "This content appeared horizontally due to the "
                #         #                     "`dimension` attribute"
                #         #                 ),
                #         #             ),
                #         #             id="horizontal-collapse",
                #         #             is_open=False,
                #         #             dimension="width",
                #         #         ),
                #         #         style={"minHeight": "100px"},
                #         #     ),
                #         # ]
                #         id='logging'
                #     ),
                #     width=3
                # ),
            ]
        ),

        # html.Div(id='logging'),
        # html.Div([
        #     dcc.Tabs(id="tabs-example", value='tab-1', children=[
        #         dcc.Tab(label='First Tab', value='tab-1', children=[
        #             html.H3('This is the content of the first tab'),
        #             html.Div('Some information here')
        #         ]),
        #         dcc.Tab(label='Second Tab', value='tab-2', children=[
        #             html.H3('This is the content of the second tab'),
        #             html.Div('Some information here')
        #         ])
        #     ]),
        #     html.Br(),
        #     html.Div(id='tabs-content-1')
        # ]),



#######################

## FIND THE STRATEGY

#########################
@callback(
    Output('strategy-founded', 'children'),
    Input('find-strategy-button', 'n_clicks'),
    State('choose-strategy', 'value'),
    State('choose-bound-dict', 'children'),
    prevent_initial_call=True
)
def find_strategy(n_clicks, algo:str, bound:dict):
    """This function is when the user search a str."""
    if bound == {} or bound == None:
        return html.P(f'Insert a bound dictionary to find the strategy.')
    #bound = {"cost": 10, "working_hours": 12}
    if cs.checkCorrectSyntax(**bpmn_lark) and cs.check_algo_is_usable(bpmn_lark[TASK_SEQ],algo):
        finded_strategies = at.calc_strat(bpmn_lark, bound, algo)
        if finded_strategies == {}:
            return html.P(f'No strategies found')
        else:
           return html.P(f'Strategies: {finded_strategies[list(finded_strategies.keys())[0]]},,,,,, ')
    else:
        return html.P(f'Ops! Seems that your diagram is too complex for this algorithm. Please check your syntax or try with another algorithm.')


#######################

## UPDATE THE BPMN DIAGRAM

#########################

@callback(
    [Output('lark-diagram', 'figure'), Output('logging', 'children')],
    Input('create-diagram-button', 'n_clicks'),
    State('input-bpmn', 'value'),
    State('input-impacts', 'value'),
    #State('task-duration', 'children'),
    State('durations-task-table', 'children'),
    prevent_initial_call=True,
    log = True
)
def create_sese_diagram(n_clicks, task , impacts= {}, durations = {}):


    #check the syntax of the input if correct print the diagram otherwise an error message
    try:
        bpmn_lark[TASK_SEQ] = task
        # bpmn_lark[H] = {}
        bpmn_lark[IMPACTS] = cs.extract_impacts_dict(impacts)
        bpmn_lark[DURATIONS] = cs.create_duration_dict(task=task, durations=durations)
    except Exception as e:
        print(f'Error while parsing the bpmn: {e}')
        return [ None, dbc.Alert(f'Error while parsing the bpmn: {e}', color="danger")]
    if cs.checkCorrectSyntax(**bpmn_lark):

        print(bpmn_lark[TASK_SEQ])
        # Create a new SESE Diagram from the input
        img = print_sese_diagram(**bpmn_lark)
        fig = px.imshow(img=img)
        fig.update_layout(width=width, height=height, margin=margin, paper_bgcolor=color)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        return [fig , dbc.Alert('The diagram has been created successfully!', color="info")]
    else:
        return  [None, dbc.Alert(f'Error in the syntax! Please check the syntax of the BPMN diagram.', color="danger")]

#######################

## ADD TASK durations

#######################

@callback(
    Output('durations-task-table', 'children'), #Output('task-duration', 'children'),
    Input('input-bpmn', 'value')
)
def add_task(tasks_):
    if not tasks_:
        return []

    tasks_list = cs.extract_tasks(tasks_)
    #tasks_list = tasks_list.filter(lambda x: x != ' ' and x != '')
    task_data = []
    for i, task in enumerate(tasks_list):
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
    if impacts == '' or impacts == None:
        return None
    impacts = cs.string_to_dict(impacts)
    #print(impacts)
    impacts_list = []
    for impact in list(impacts.values())[0]:
        impacts_list.append(impact)
    task_data = []
    #print(impacts_list)
    for i, task in enumerate(impacts_list):
        task_data.append({
            'Impacts': task,
            'Set Input': dcc.Input(
                id=f'range-slider-{i}',
                type='number',
                value=10,
                min= min_duration,
            )
        })
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-bound-dict-df',
        style = {'width': '100%', 'textalign': 'center'}
    )



#######################

## Logging

#######################

# @callback(
#     Output("horizontal-collapse", "is_open"),
#     [Input("horizontal-collapse-button", "n_clicks")],
#     [State("horizontal-collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open