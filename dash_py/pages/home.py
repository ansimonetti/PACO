from datetime import datetime
import dash
from dash import html, dcc, Input, Output,State, callback
import dash_bootstrap_components as dbc
import dash_svg as svg
import pandas as pd
import plotly.express as px
from utils import check_syntax as cs
from utils import automa as at
from utils.env import ALGORITHMS, IMPACTS_NAMES, PATH_AUTOMATON_IMAGE_SVG, PATH_IMAGE_BPMN_LARK_SVG, RESOLUTION, TASK_SEQ, IMPACTS, H, DURATIONS, PROBABILITIES, NAMES, DELAYS
from utils.print_sese_diagram import print_sese_diagram
#from solver.tree_lib import print_sese_custom_tree

dash.register_page(__name__, path='/')
# SimpleTask1, Task1 || Task, Task3 ^ Task9
bpmn_lark = {
    TASK_SEQ: 'SimpleTask1, Task1 || Task, Task3 ^ [C1] Task9',
    H: 0, # indicates the index of splitting to separate non-cumulative and cumulative impacts impact_vector[0:H] for cumulative impacts and impact_vector[H+1:] otherwise
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

img = print_sese_diagram(**bpmn_lark)

spinner = dbc.Spinner(color="primary", type="grow", fullscreen=True)
def layout():
    return html.Div([
        html.Div(id='logging'),
        html.Div(id='logging-strategy'),
        dbc.Alert("Disclaimer: This is not a definitive app! There may be some bugs or placeholders. Please be careful! Moreover, the BPMN dimension supported varies among machines. So for big BPMN choose a powerful PC. ", color="warning"),
        ################################
        ### DEFINING THE BPMN + DCPI ###
        ################################
        html.H1('Insert your BPMN here:'),
        #dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select Files')]), multiple=False), # Drag and drop per file ma da usapre più avanti
        html.P("""Here is an example of a BPMN complete diagram: Task0, (Task1 || Task4), (Task3 ^ [C1] Task9, Task8 / [C2] Task2)"""),
        html.Br(),
        dcc.Textarea(value=bpmn_lark[TASK_SEQ], id = 'input-bpmn', style={'width': '100%'}, persistence = True), # persistence è obbligatoria altrimenti quando ricarica la pagina (cioè ogni valta che aggiorna il graph )
        html.P('Insert the duration of the tasks:'),
        html.Div(id='task-duration'),
        dbc.Table.from_dataframe(
            pd.DataFrame(data),
            id = 'durations-task-table',
            style = {'width': '100%', 'textAlign': 'center'}
        ),
        html.P('Insert the impacts list of the tasks in the following format: cost, hours. IF for some task the impacts are not defined they will be put 0 by default.'),
        dcc.Textarea(value='',  id = 'input-impacts', persistence=True, style={'width': '100%'}),
        html.Div(id='impacts-table'),
        html.Br(),
        html.P('Insert the probabilities for each natural choise. The values have to be between 0 and 1.'),
        html.Div(id= 'probabilities'),
        html.Br(),
        html.P('Insert the delays for each natural choise. The values have to be between 0 and 100.'),
        html.Div(id= 'delays'),
        html.Br(),
        dbc.Button('Create diagram', id='create-diagram-button'),
        ###############################
        ### BPMN DIAGRAM USING LARK ###
        ###############################
        html.Div([
            html.H3("BPMN diagram in lark:"),
            #html.Img(id='lark-diagram1', src= 'assets/graph.svg', style={'height': '500', 'width': '1000'}),
            html.Iframe(id="lark-frame",src=PATH_IMAGE_BPMN_LARK_SVG, style={'height': '100%', 'width': '100%'}),
            # download diagram as svg
            html.A('Download diagram as SVG', id='download-diagram', download='diagram.svg', href=PATH_IMAGE_BPMN_LARK_SVG, target='_blank'),
        ]),
        html.Br(),
        ################
        ### STRATEGY ###
        ################
        html.Div(id="strategy", children=[
            html.H1("Choose the algorithm to use:"),
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
            dbc.Button('Find strategy', id='find-strategy-button'),
            html.Div(
                    children = [
                        dcc.Loading(
                            id="loading-strategy",
                            children=[html.Div([html.Div(id="strategy-founded")])],
                            type="circle", #'graph', 'cube', 'circle', 'dot', 'default'
                            fullscreen=True,
                        )
                    ]
            )
        ]),
        html.Br(),
        html.Br(),      
        ################
        ### EXPLAINER ##
        ################
        # html.Div(id="explainer", children=[
        #     html.H1("here the explainer:"),            
        # ]),
        # html.Br(),
        # html.Br(),   
    ]
)


#######################

## FIND THE STRATEGY

#########################
@callback(
    [Output('strategy-founded', 'children'), Output('logging-strategy', 'children')],
    Input('find-strategy-button', 'n_clicks'),
    State('choose-strategy', 'value'),
    State('choose-bound-dict', 'children'),
    State('input-impacts', 'value'),
    prevent_initial_call=True
)
def find_strategy(n_clicks, algo:str, bound:dict, impacts):
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
    if cs.checkCorrectSyntax(bpmn_lark) and cs.check_algo_is_usable(bpmn_lark[TASK_SEQ],algo):        
        impacts = cs.string_to_dict(impacts)
        all_keys = cs.order_keys(impacts)
        bpmn_lark[IMPACTS_NAMES] = all_keys
        #print(bpmn_lark)
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
            return [
                html.Div([
                    html.P(f"Strategies: {finded_strategies['strat1']}"),
                    html.Iframe(src=PATH_AUTOMATON_IMAGE_SVG, style={'height': '100%', 'width': '100%'}),
                    # download diagram as svg
                    html.A('Download strategy diagram as SVG', id='download-diagram', download='strategy.svg', href=PATH_AUTOMATON_IMAGE_SVG, target='_blank'),
                    html.Img(src="assets/out.png"),
                ]), None]
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
    [Output('logging', 'children'), Output('lark-frame', 'src')],
    Input('create-diagram-button', 'n_clicks'),
    State('input-bpmn', 'value'),
    State('input-impacts', 'value'),
    State('durations-task-table', 'children'),
    State('probabilities', 'children'),
    State('delays', 'children'),
    prevent_initial_call=True,
)
def create_sese_diagram(n_clicks, task , impacts= {}, durations = {}, probabilities = {}, delays = {}):
    #check the syntax of the input if correct print the diagram otherwise an error message
    try:
        bpmn_lark[TASK_SEQ] = task
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN tasks sequence: {e}')
        return [  # dbc.Alert(f'Error while parsing the bpmn: {e}', color="danger")]
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None
            ]
    try:
        bpmn_lark[IMPACTS] = cs.extract_impacts_dict(impacts, task)
        impacts = cs.string_to_dict(impacts)
        all_keys = cs.order_keys(impacts)
        bpmn_lark[IMPACTS_NAMES] = all_keys
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN impacts: {e}')
        return [  # dbc.Alert(f'Error while parsing the bpmn: {e}', color="danger")]
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None
            ]
    try:
        bpmn_lark[DURATIONS] = cs.create_duration_dict(task=task, durations=durations)
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN durations: {e}')
        return [  
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None
            ]
    try:
        list_choises = cs.extract_choises(task)
        bpmn_lark[PROBABILITIES] = cs.create_probabilities_dict(cs.extract_choises_nat(task), probabilities)
        bpmn_lark[NAMES] = cs.create_probabilities_names(list_choises)
        bpmn_lark[DELAYS] = cs.create_probabilities_dict(cs.extract_choises_user(task), delays)
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN choises: {e}')
        return [
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None
            ]
    if cs.checkCorrectSyntax(bpmn_lark):
        #print(bpmn_lark)
        try:
            # Create a new SESE Diagram from the input
            name_svg =  "assets/bpmnSvg/bpmn_"+ str(datetime.timestamp(datetime.now())) +".svg"
            print_sese_diagram(**bpmn_lark, outfile_svg=name_svg) 
            return [None, name_svg]
        except Exception as e:
            return [ #dbc.Alert(f'Error while creating the diagram: {e}', color="danger")
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                            dbc.ModalBody(f'Error while creating the diagram: {e}'),
                        ],
                        id="modal",
                        is_open=True,
                    ),
                    None
                ]
    else:
        return  [#dbc.Alert(f'Error in the syntax! Please check the syntax of the BPMN diagram.', color="danger")
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody("Error in the syntax! Please check the syntax of the BPMN diagram."),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None
                ]

#######################

## ADD TASK durations

#######################

@callback(
    Output('durations-task-table', 'children'), 
    Input('input-bpmn', 'value'),
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
    #########
    ### TODO
    ### CHECK WHY IT ADDS/APPENDS SPACES TO THE TABLE
    #########
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []

    # Extract the tasks from the input
    tasks_list = cs.extract_tasks(tasks_)

    # Initialize an empty list to store the task data
    task_data = []
    # print(f"task list {tasks_list}")
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
                # tooltip={
                #     "placement": "bottom",
                #     "always_visible": True,
                # }
            )
        })
    # print(task_data)
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
    all_keys = cs.order_keys(impacts)
    # Initialize an empty list to store the task data
    task_data = []

    # Iterate over the impacts
    for i, task in enumerate(all_keys):
        # For each impact, append a dictionary to the task data list
        # The dictionary contains the impact and an input field for the impact
        task_data.append({
            'Impacts': task,
            'Set Bound': dcc.Input(
                id=f'range-slider-{i}',
                type='number',
                value=20,
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


#######################

## ADD PROBABILITIES

#######################

@callback(
    Output('probabilities', 'children'),
    Input('input-bpmn', 'value'),
)
def add_probabilities(tasks_):
    """
    This function takes the bpmn, extract the choises and assign them with a probability.
    Then, it creates a list of unique impacts and generates a table where each row contains an impact and an input field.
    The function is decorated with a callback that updates the 'choose-bound-dict' component
    whenever the 'create-diagram-button' is clicked and the 'input-impacts' value changes.

    Parameters:
    bpmn (str): The string of bpmn.

    Returns:
    dbc.Table: A table where each row contains an impact and an input field.
    """
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []

    # Extract the tasks from the input
    tasks_list = cs.extract_choises_nat(tasks_)

    # Initialize an empty list to store the task data
    task_data = []

    # Iterate over the impacts
    for i, task in enumerate(tasks_list):
        # For each impact, append a dictionary to the task data list
        # The dictionary contains the impact and an input field for the impact
        task_data.append({
            'Impacts': task,
            'Set Probabilities': dcc.Input(
                id=f'range-slider-{i}',
                type='number',
                value=0.5,
                step="0.01",
                min= 0,
                max=1
            )
        })

    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the 'choose-bound-dict' component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-prob',
        style = {'width': '100%', 'textalign': 'center'}
    )


#######################

## ADD DELAYS

#######################

@callback(
    Output('delays', 'children'),
    Input('input-bpmn', 'value'),
)
def add_delays(tasks_):
    """
    This function takes the bpmn, extract the choises and assign them with a delay.
    Then, it creates a list of unique impacts and generates a table where each row contains an impact and an input field.
    The function is decorated with a callback that updates the 'choose-bound-dict' component
    whenever the 'create-diagram-button' is clicked and the 'input-impacts' value changes.

    Parameters:
    bpmn (str): The string of bpmn.

    Returns:
    dbc.Table: A table where each row contains an impact and an input field.
    """
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []

    # Extract the tasks from the input
    tasks_list = cs.extract_choises_user(tasks_)

    # Initialize an empty list to store the task data
    task_data = []

    # Iterate over the impacts
    for i, task in enumerate(tasks_list):
        # For each impact, append a dictionary to the task data list
        # The dictionary contains the impact and an input field for the impact
        task_data.append({
            'Impacts': task,
            'Set Delays': dcc.Input(
                id=f'range-slider-{i}',
                type='number',
                value=0,
                min= 0,
                max=100
            )
        })

    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the 'choose-bound-dict' component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-prob',
        style = {'width': '100%', 'textalign': 'center'}
    )


#######################

## ADD IMPACTS

#######################

@callback(
    Output('impacts-table', 'children'),
    Input('input-bpmn', 'value'),
    Input('input-impacts', 'value'),
)
def add_impacts(tasks_, impacts):
    """
    """
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []

    # Extract the tasks from the input
    
    if not tasks_:
        return []
    impacts = impacts.split(sep=',')
    # Extract the tasks from the input
    tasks_list = cs.extract_tasks(tasks_)
    # Initialize an empty list to store the task data
    task_data = []

    # Iterate over the tasks
    for i, task in enumerate(tasks_list):
        # Initialize an empty dictionary to store the task data
        task_dict = {'Task': task}

        # Iterate over the impacts
        for j, impact in enumerate(impacts):
            # For each impact, add a slider to the task data dictionary
            task_dict[impact] = dcc.Input(
                id=f'range-slider-{i}-{j}',
                type='number',
                value=0,
                min=0,
            )

        # Append the task data dictionary to the task data list
        task_data.append(task_dict)
    print(task_data)
    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the 'choose-bound-dict' component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-prob',
        style = {'width': '100%', 'textalign': 'center'}
    )