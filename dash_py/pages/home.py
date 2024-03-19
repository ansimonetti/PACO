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
    TASK_SEQ: 'SimpleTask',
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
        ############################
        ### DEFINING THE BPMN + DCPI
        ##############################
        html.H1('Insert your BPMN file here:'),
        #dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select Files')]), multiple=False), # Drag and drop per file ma da usapre più avanti
        html.P("""Here is an example of a BPMN complete diagram with impacts and duration: {
            'expression':'Task1, Task2,Task3',
            'impacts': {'Task1': [1,0,1], 'Task3':[1,2,3]},
        }"""),
        html.Br(),
        dcc.Textarea(value=bpmn_lark[TASK_SEQ], id = 'input-bpmn'), # persistance è obbligatoria altrimenti quando ricarica la pagina (cioè ogni valta che aggiorna il graph lark-diagram)
        html.P('Insert the duration of the tasks:'),
        html.Div(id='task-duration'), 
        dbc.Table.from_dataframe(        
            pd.DataFrame(data),
            id = 'durations-task-table',
            style = {'width': '100%', 'textAlign': 'center'}
        ),        
        html.P('Insert the impacts of the tasks in the following format: {"SimpleTask":  {"cost": 10, "working_hours": 12}, "Task3":  {"cost": 18, "working_hours": 5} }'),
        html.Div(id='impacts'),
        dcc.Textarea(value='',  id = 'input-impacts', persistence=True),
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
            #dcc.Textarea(value='', id='input-bound'),
            html.Div(id= 'choose-bound-dict'),
            html.Br(),
            html.Br(),
            html.Button('Find strategy', id='find-strategy-button'),
            html.Div(id='strategy-founded')            
        ]),
    ])


#######################

## FIND THE STRATEGY
 
#########################
@callback(
    Output('strategy-founded', 'children'),
    Input('find-strategy-button', 'n_clicks'),
    State('choose-strategy', 'value'),
    State('input-bound', 'value'),    
    prevent_initial_call=True
)
def find_strategy(n_clicks, algo:str, bound:dict):
    """This function is when the user search a str."""
    bound = {"cost": 10, "working_hours": 12}
    if bound == {} or bound == '' or bound == None:
        return html.P(f'Insert a bound dictionary to find the strategy.')
    if cs.checkCorrectSyntax(**bpmn_lark) and cs.check_algo_is_usable(bpmn_lark[TASK_SEQ],algo):
        finded_strategies = at.calc_strat(bpmn_lark, bound, algo)
        if finded_strategies == {}: 
            return html.P(f'No strategies found')
        else:
           return html.P(f'Strategies: {finded_strategies[list(finded_strategies.keys())[0]]}') 
    else:
        return html.P(f'Ops! Seems that your diagram is too complex for this algorithm. Please check your syntax or try with another algorithm.')


#######################

## UPDATE THE BPMN DIAGRAM
 
#########################

@callback(
    Output('lark-diagram', 'figure'),
    Input('create-diagram-button', 'n_clicks'),
    State('input-bpmn', 'value'),
    State('input-impacts', 'value'),
    #State('task-duration', 'children'),
    State('durations-task-table', 'children'),
    prevent_initial_call=True
)
def create_sese_diagram(nclick, task , impacts= {}, durations = {}):
    #print(durations)
    #check the syntax of the input if correct print the diagram otherwise an error message 
    try:
        if task == '' or task == None:
            return None
        bpmn_lark[TASK_SEQ] = task
        bpmn_lark[H] = durations
        bpmn_lark[IMPACTS] = impacts
    except:
        return None
    if cs.checkCorrectSyntax(**bpmn_lark):
        tasks = cs.extract_tasks(bpmn_lark[TASK_SEQ])
        print(tasks)
        # Create a new SESE Diagram from the input
        img = print_sese_diagram(**bpmn_lark) 
        fig = px.imshow(img=img) 
        fig.update_layout(width=width, height=height, margin=margin, paper_bgcolor=color)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)  
        return fig 
    else:
        return  None

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
    # task_data = dbc.Table.from_dataframe(        
    #     pd.DataFrame(task_data),
    #     id = 'durations-task-table',
    #     style = {'width': '100%', 'textalign': 'center'}
    # )
    # return task_data
    return dbc.Table.from_dataframe(        
        pd.DataFrame(task_data),
        id = 'durations-task-table',
        style = {'width': '100%', 'textalign': 'center'}
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
                min= min_duration,
            )
        })
    return dbc.Table.from_dataframe(        
        pd.DataFrame(task_data),
        id = 'choose-bound-dict-df',
        style = {'width': '100%', 'textalign': 'center'}
    )