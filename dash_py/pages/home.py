import base64
import io
import dash
from dash import html, dcc, Input, Output,State, callback
import pandas as pd
import plotly.express as px
import plotly.subplots as sb
from utils import check_syntax as cs
from utils import automa as at
from utils.env import ALGORITHMS, TASK_SEQ, IMPACTS, PATH_IMAGE_BPMN_LARK
from utils.print_sese_diagram import print_sese_diagram
import dash_bootstrap_components as dbc
dash.register_page(__name__, path='/')
# SimpleTask1, Task1 || Task, rjfgkn ^ Task9
bpmn_lark = {
    TASK_SEQ: 'SimpleTask',
    'h': {},
    IMPACTS: {},
}
# data= {
#             'Task': bpmn_lark[TASK_SEQ],
#             'Duration': dcc.RangeSlider(
#                 id=f'range-slider-',
#                 min=0,
#                 max=1e10,
#                 value=[0, 10],
#                 marks={j: str(j) for j in range(0, 11, 1) if j != 0}
#             )
#         }
img = print_sese_diagram(**bpmn_lark) 
fig = px.imshow(img=img) 
fig.update_layout(width=500, height=250, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
def layout():
    return html.Div([   

    html.Div([
        ############################
        ### DEFINING THE BPMN + DCPI
        ##############################
        html.H1('Insert your BPMN file here:'),
        #dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select Files')]), multiple=False), # Drag and drop per file ma da usapre più avanti
        html.P("""Here is an example of a BPMN complete diagram with impacts and duration: {
            'expression':'Task1, Task2,Task3',
            'h':2,
            'impacts': {'Task1': [1,0,1], 'Task3':[1,2,3]},
        }"""),
        # html.Div(id='task-duration'
        #          ,children=[
        #     html.H4("Tasks duration:"),
        #     dcc.Checklist(#id='taks-duration-choose',
        #         ['New York City', 'Montréal', 'San Francisco'],
        #         ['New York City', 'Montréal']),
        #     dcc.RangeSlider(
        #         id='range-slider',
        #         min=0,
        #         max=1e10,
        #         value=[0, 1e10],
        #         marks={i: str(i) for i in range(0, 11, 1) if i != 0}
        #     ),
        # ]
        # ),
        html.Br(),
        dcc.Textarea(value='SimpleTask', id = 'input-bpmn'), # persistance è obbligatoria altrimenti quando ricarica la pagina (cioè ogni valta che aggiorna il graph lark-diagram)
        html.P('Insert the duration of the tasks:'),
        html.Div(id='task-duration'), 
        # dbc.Table.from_dataframe(        
        #     pd.DataFrame(data),
        #     id = 'durations-task-table',
        # ),       
        #dcc.Textarea(value='', id = 'input-duration', persistence=True),
        
        html.P('Insert the impacts of the tasks in the following format: {"Task1": 1, "Task3":3}'),
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
            dcc.Textarea(value='', id='input-bound'),
            html.Br(),
            html.Br(),
            html.Button('Find strategy', id='find-strategy-button'),
            html.Div(id='strategy-founded')
            
        ]),
    ]),
])

#######################

## UPDATE THE STRATEGY
## find one 
 
#########################
@callback(
    Output('strategy-founded', 'children'),
    Input('find-strategy-button', 'n_clicks'),
    State('choose-strategy', 'value'),
    State('input-bound', 'value'),
    prevent_initial_call=True
)
def find_strategy(n_clicks, algo:str, bound:dict):
    """This function is when the user update the syntax."""
    print(bpmn_lark[TASK_SEQ],algo)
    if bound == {} or bound == '' or bound == None:
        return html.P(f'Insert a bound dictionary to find the strategy.')
    if cs.checkCorrectSyntax(**bpmn_lark) and cs.check_algo_is_usable(bpmn_lark[TASK_SEQ],algo):
        finded_strategies = at.calc_strat(bpmn_lark, {})
        if finded_strategies == {}: 
            return html.P(f'No strategies found')
        else:
           return html.P(f'Strategies founded: {finded_strategies}') 
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
    #State('durations-task-table', 'value'),
    prevent_initial_call=True
)
def create_sese_diagram(nclick, task , impacts, duration=9):
    
    #check the syntax of the input if correct print the diagram otherwise an error message 
    try:
        if task == '' or task == None:
            return None
        bpmn_lark[TASK_SEQ] = task
        bpmn_lark['h'] = duration
        bpmn_lark[IMPACTS] = impacts
    except:
        return None
    if cs.checkCorrectSyntax(**bpmn_lark):
        tasks = cs.extract_tasks(bpmn_lark[TASK_SEQ])
        print(tasks)
        # Create a new SESE Diagram from the input
        img = print_sese_diagram(**bpmn_lark) 
        fig = px.imshow(img=img) 
        fig.update_layout(width=500, height=100, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)  
        return  fig 
    else:
        return  None

#######################
## ADD TASK durations
#######################

@callback(
    Output('task-duration', 'children'),#Output('durations-task-table', 'value'),
    Input('input-bpmn', 'value')
)
def add_task(tasks):
    if not tasks:
        return []
    
    tasks_list = cs.extract_tasks(tasks)
    task_data = []
    for i, task in enumerate(tasks_list):
        task_data.append({
            'Task': task,
            'Duration': dcc.RangeSlider(
                id=f'range-slider-{i}',
                min=0,
                max=1e10,
                value=[0, 10],
                marks={j: str(j) for j in range(0, 11, 1) if j != 0}
            )
        })
    #return task_data
    return dbc.Table.from_dataframe(        
        pd.DataFrame(task_data),
        id = 'durations-task-table',
    )


# when not using  the button
# @callback(
#     Output('lark-diagram', 'figure'),
#     #Input('create-diagram-button', 'n_clicks'),
#     Input('input-bpmn', 'value'),
#     Input('input-impacts', 'value'),
#     Input('input-duration', 'value'),
#     #prevent_initial_call=True
# )
# def create_sese_diagram(task , impacts, duration):
#     #check the syntax of the input if correct print the diagram otherwise an error message 
#     try:
#         if task == '' or task == None:
#             return None
#         bpmn_lark[TASK_SEQ] = task
#         bpmn_lark['h'] = duration
#         bpmn_lark[IMPACTS] = impacts
#     except:
#         return None
#     if cs.checkCorrectSyntax(**bpmn_lark):
#         # Create a new SESE Diagram from the input
#         img = print_sese_diagram(**bpmn_lark) 
#         fig = px.imshow(img=img) 
#         fig.update_layout(width=500, height=100, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
#         fig.update_xaxes(showticklabels=False)
#         fig.update_yaxes(showticklabels=False)  
#         return  fig 
#     else:
#         return  None
    
# @callback(
#     Output('lark-diagram', 'figure'),
#  #   Output('img-lark', 'src'),
#     Input('create-diagram-button', 'n_clicks'),
#     Input('input-bpmn', 'value'),
#     Input('input-impacts', 'value'),
#     Input('input-duration', 'value'),
#     prevent_initial_call=True
# )
# def create_sese_diagram(n_clicks,task, impacts, duration):
#     #check the syntax of the input if correct print the diagram otherwise an error message 
#     try:
#         bpmn_lark[TASK_SEQ] = task
#         bpmn_lark['h'] = duration
#         bpmn_lark[IMPACTS] = impacts
#     except:
#         return None
#     if cs.checkCorrectSyntax(**bpmn_lark):
#         # Create a new SESE Diagram from the input
#         img = print_sese_diagram(**bpmn_lark) 
#         fig = px.imshow(img=img) 
#         #fig.add_trace(fig, row=1, col=1)
#         fig.update_layout(width=500, height=500, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
#         fig.update_xaxes(showticklabels=False)
#         fig.update_yaxes(showticklabels=False)  
#         return fig #, cs.b64_image(PATH_IMAGE_BPMN_LARK)
#     else:
#         return  None
    
# @callback(
#     Output('lark-diagram', 'children'),
#     Input('create-diagram-button', 'n_clicks'),
#     State('input-bpmn', 'value'),
#     State('input-impacts', 'value'),
#     State('input-duration', 'value'),
#     prevent_initial_call=True
# )
# def create_sese_diagram(n_clicks,task, impacts, duration):
#     #check the syntax of the input if correct print the diagram otherwise an error message 
#     try:
#         bpmn_lark[TASK_SEQ] = task
#         bpmn_lark['h'] = duration
#         bpmn_lark[IMPACTS] = impacts
#     except:
#         return html.Div([            
#                 html.H3("Your diagram could not be created. Check your syntax.")
#             ])
#     if cs.checkCorrectSyntax(**bpmn_lark):
#         # Create a new SESE Diagram from the input
#         img = print_sese_diagram(**bpmn_lark) 
#         fig = px.imshow(img=img) 
#         #fig.add_trace(go.Imshow(z=img, zmin=0, zmax=1), row=1, col=1)
#         fig.update_layout(width=500, height=500, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
#         fig.update_xaxes(showticklabels=False)
#         fig.update_yaxes(showticklabels=False)     
#         return html.Div([            
#                 html.H3("Your diagram is:"),
#                 dcc.Graph(id='img-diagram', figure=fig),
#                 #html.Img(src=cs.b64_image(PATH_IMAGE_BPMN_LARK)),
#                 #html.Img(src=dash.get_asset_url('d.png')),   
                         
#             ])
#     else:
#         return  html.Div([            
#                 html.H3("Your diagram could not be created. Check your syntax.")
#             ])
