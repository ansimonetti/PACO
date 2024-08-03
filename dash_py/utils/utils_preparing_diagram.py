import pandas as pd
import utils.check_syntax as cs
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
def prepare_task_duration(tasks_
                        , min_duration=0
                        , max_duration=100
                        , value_interval=[0, 100]
                        , marks={0: '0', 100: '100'}
                        , durations = {}):
    """
    Prepare the task duration sliders for the input tasks
    :param tasks_: The input tasks
    :param min_duration: The minimum duration for the range slider
    :param max_duration: The maximum duration for the range slider
    :param value_interval: The initial value interval for the range slider
    :param marks: The marks for the range slider
    :return: The task data
    """
    # Extract the tasks from the input
    tasks_list = cs.extract_tasks(tasks_)
    # Initialize an empty list to store the task data
    task_data = []
    # print(f"task list {tasks_list}")
    # Iterate over the tasks
    if durations:
        for i, task in enumerate(tasks_list):
            # For each task, append a dictionary to the task data list
            # The dictionary contains the task name and a range slider for the task's duration
            if isinstance(durations[task], list):
                task_data.append({
                    'Task': task,
                    'Duration': dcc.RangeSlider(
                        id=f'range-slider-{i}',
                        min=min_duration,
                        max=max_duration,
                        value=durations[task],
                        marks=marks,
                        tooltip={
                            "placement": "bottom",
                            "always_visible": True,
                        }
                    )
                })
            else:
                task_data.append({
                    'Task': task,
                    'Duration': dcc.RangeSlider(
                        id=f'range-slider-{i}',
                        min=min_duration,
                        max=max_duration,
                        value=[0, durations[task]],
                        marks=marks,
                        tooltip={
                            "placement": "bottom",
                            "always_visible": True,
                        }
                    )})
    else:
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
    # print(task_data)
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'durations-task-table',
        style = {'width': '100%', }
    )


def prepare_task_impacts(tasks_,impacts, impacts_dict = {}):
    impacts = impacts.split(sep=',')
    # Extract the tasks from the input
    tasks_list = cs.extract_tasks(tasks_)
    # Initialize an empty list to store the task data
    task_data = []
    if impacts_dict:
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
                    value=impacts_dict[task][j],
                    min=0,
                )

            # Append the task data dictionary to the task data list
            task_data.append(task_dict)
    else:
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
    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the 'impacts-table' component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'impacts-tab',
        style = {'width': '100%', 'textalign': 'center'}
    )

def prepare_task_probabilities(tasks_, prob = {}):
    # Extract the tasks from the input
    tasks_list = cs.extract_choises_nat(tasks_)
    tasks_list += cs.extract_loops(tasks_)
    # Initialize an empty list to store the task data
    task_data = []
    if prob:
        # Iterate over the tasks
        for i, task in enumerate(tasks_list):
            # For each task, append a dictionary to the task data list
            # The dictionary contains the task name and a range slider for the task's duration
            task_data.append({
                'Natural & Loops': task,
                'Probability': dcc.Input(
                    id=f'range-slider-{i}',
                    type='number',
                    value=prob[task],
                    min=0,
                    max=1,
                    step=0.01
                )
            })
    else:
        # Iterate over the tasks
        for i, task in enumerate(tasks_list):
            # For each task, append a dictionary to the task data list
            # The dictionary contains the task name and a range slider for the task's duration
            task_data.append({
                'Natural & Loops': task,
                'Probability': dcc.Input(
                    id=f'range-slider-{i}',
                    type='number',
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.01
                )
            })
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-prob',
        style = {'width': '100%', 'textalign': 'center'}
    )

def prepare_task_delays(tasks_, delays = {}):
    # Extract the tasks from the input
    tasks_list =  cs.extract_choises_user(tasks_)
    # Initialize an empty list to store the task data
    task_data = []
    if delays:
        # Iterate over the tasks
        for i, task in enumerate(tasks_list):
            # For each task, append a dictionary to the task data list
            # The dictionary contains the task name and a range slider for the task's duration
            task_data.append({
                'Choices': task,
                'Set Delay': dcc.Input(
                    id=f'range-slider-{i}',
                    type='number',
                    value=delays[task],
                    min=0,
                )
            })
    else:
        # Iterate over the tasks
        for i, task in enumerate(tasks_list):
            # For each task, append a dictionary to the task data list
            # The dictionary contains the task name and a range slider for the task's duration
            task_data.append({
                'Choices': task,
                'Set Delay': dcc.Input(
                    id=f'range-slider-{i}',
                    type='number',
                    value=0,
                    min=0,
                )
            })
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-prob',
        style = {'width': '100%', 'textalign': 'center'}
    )

def prepare_task_loops(tasks_, loops={}):
    # Extract the tasks from the input
    tasks_list = cs.extract_loops(tasks_)
    # Initialize an empty list to store the task data
    task_data = []
    if loops:
        # Iterate over the impacts
        for i, task in enumerate(tasks_list):
            # For each impact, append a dictionary to the task data list
            # The dictionary contains the impact and an input field for the impact
            task_data.append({
                'Loops': task,
                'Allowed iterations': dcc.Input(
                    id=f'range-slider-{i}',
                    type='number',
                    value=loops[task],
                    min= 1,
                    max=100
                )
            })
    else:
        # Iterate over the impacts
        for i, task in enumerate(tasks_list):
            # For each impact, append a dictionary to the task data list
            # The dictionary contains the impact and an input field for the impact
            task_data.append({
                'Loops': task,
                'Allowed iterations': dcc.Input(
                    id=f'range-slider-{i}',
                    type='number',
                    value=1,
                    min= 1,
                    max=100
                )
            })
    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the probabilities component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-loop-round',
        style = {'width': '100%', 'textalign': 'center'}
    )