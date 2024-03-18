import dash
from dash import Dash, html, dcc
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
# SimpleTask1, Task1 || Task, rjfgkn ^ Task9
app = Dash(__name__)
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
        # html.H1('BPMN+CPI APP!', style={'textAlign': 'center'}),
        # html.Div([
        #     html.Div(
        #         dcc.Link(f"{page['name']}", href=page["relative_path"])
        #     ) for page in dash.page_registry.values()
        # ]),
        # dash.page_container,
        dcc.Textarea(value='SimpleTask', id = 'input-bpmn'), # persistance è obbligatoria altrimenti quando ricarica la pagina (cioè ogni valta che aggiorna il graph lark-diagram)
        html.Button('Create diagram', id='create-diagram-button'),
        html.Div([
            html.H3("BPMN diagram in lark:"),
            dcc.Graph(id='lark-diagram', figure=fig),
        ]),
        
    ])

@callback(
    Output('lark-diagram', 'figure'),
    Input('create-diagram-button', 'n_clicks'),
    State('input-bpmn', 'value'),
    #State('input-impacts', 'value'),
    #State('durations-task-table', 'value'),
    prevent_initial_call=True
)
def create_sese_diagram(nclick, task):
    
    #check the syntax of the input if correct print the diagram otherwise an error message 
    # try:
    #     if task == '' or task == None:
    #         return None
    #     bpmn_lark[TASK_SEQ] = task
    #     bpmn_lark['h'] = duration
    #     bpmn_lark[IMPACTS] = impacts
    # except:
    #     return None
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

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port="8050")

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


