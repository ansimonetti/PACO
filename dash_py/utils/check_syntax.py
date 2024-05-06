
"""
   File that checks things and useful things 
"""
from utils.print_sese_tree import print_sese_tree
from utils.env import ALGORITHMS, ALGORITHMS_MISSING_SYNTAX, ALL_SYNTAX, DURATIONS, IMPACTS, SESE_PARSER, TASK_SEQ
import re
import json
from datetime import datetime
def checkCorrectSyntax(bpmn:dict) -> bool:
    """
    Check if the syntax of the BPMN file is correct.
    """
    print(f'{datetime.now()}: checking syntax in progress... ')
    if bpmn[TASK_SEQ] == '' or bpmn[TASK_SEQ] is None:
        return False
    if not isinstance(bpmn[DURATIONS], dict):
        return False
    if not isinstance(bpmn[IMPACTS], dict):
        return False
    # tree = SESE_PARSER.parse(bpmn[TASK_SEQ])
    # print((tree).pretty())
    return True


def check_algo_is_usable(expression: str, algo: str) -> bool:
    """
    Check if the costructs in the BPMN is suitable fro the algo.
    """
    print('checking expression within algo in progress...')
    if expression == '' or algo == '' or algo not in ALGORITHMS.keys():
        return False
    if algo in ALGORITHMS_MISSING_SYNTAX.keys() and list(ALGORITHMS_MISSING_SYNTAX.get(algo)) != []:
        #print(list(ALGORITHMS_MISSING_SYNTAX.get(algo)))
        for element in list(ALGORITHMS_MISSING_SYNTAX.get(algo)):
            #print(element)
            if element in expression:
                return False        
    return True

def check_ONLY_1_taks(string: str) -> bool:
    """
        This function checks if a given string contains all elements from the ALL_SYNTAX list.
        If it does, returns true; otherwise false

    """
    for element in ALL_SYNTAX:
        if element not in string:
            return False
    return True

def extract_tasks_recursively(lark_tree) -> list[str]:
    tasks = []
    if lark_tree.data == 'task':
        tasks.append(lark_tree.children[0].value)
    elif (lark_tree.data in {'choice', 'natural'}):
        tasks.extend(extract_tasks_recursively(lark_tree.children[0]))
        tasks.extend(extract_tasks_recursively(lark_tree.children[2]))
    elif (lark_tree.data in {'sequential', 'parallel'}):
        tasks.extend(extract_tasks_recursively(lark_tree.children[0]))
        tasks.extend(extract_tasks_recursively(lark_tree.children[1]))
    elif (lark_tree.data == 'loop'):
        tasks.extend(extract_tasks_recursively(lark_tree.children[0]))
    elif (lark_tree.data == 'loop_probability'):
        tasks.extend(extract_tasks_recursively(lark_tree.children[1]))
    return tasks

def extract_tasks(expression: str) -> list[str]:
    """
        Function that extracts the tasks from the  BPMN expression.
    """
    if expression == '' or expression is None:
        return []
    #print(expression)
    # if check_ONLY_1_taks(expression):
    #     print('only 1 task')
    #     return expression
    
    try: 
        tree = SESE_PARSER.parse(expression) # parsing the expression to obtain the related tree

        tasks = extract_tasks_recursively(tree) # recursively extracting task names from the lark tree
        
    except Exception as e:
        #print(f'Error while parsing the expression: {e}') # May it be better to suppress this print?
        return []
    
    return tasks

def string_to_dict(string) -> dict:
    """
    Convert a JSON string to a dictionary.

    Parameters:
    string (str): A JSON string.

    Returns:
    dict: The dictionary obtained from the JSON string.
    """
    return json.loads(string)

#######################

## DURATIONS

########################
def extract_value_durations(data):
    """
    Recursively extract 'value' from nested lists and dictionaries.

    Parameters:
    data (list or dict): The data to extract values from.

    Yields:
    The extracted values.
    """
    # If data is a list, recursively call the function on each item
    if isinstance(data, list):
        for item in data:
            yield from extract_value_durations(item)
    # If data is a dictionary
    elif isinstance(data, dict):
        # If 'value' is a key in the dictionary, yield its value
        if 'value' in data:
            yield data['value']
        # Otherwise, recursively call the function on each value in the dictionary
        else:
            for value in data.values():
                yield from extract_value_durations(value)


def create_duration_dict(task:str, durations):
    """
    Create a dictionary mapping tasks to durations.

    Parameters:
    task (str): A string representing tasks.
    durations: The durations of the tasks.

    Returns:
    dict: A dictionary mapping tasks to durations.
    """
    # Extract 'value' from durations
    durations = list(extract_value_durations(durations))
    # Initialize an empty dictionary
    durations_dict = {}
    # If task is empty or None, return the empty dictionary
    if task == '' or task == None:
        return durations_dict
    try:
        # Extract tasks from the task string
        tasks = extract_tasks(task)        
        # If the number of tasks equals the number of durations
        if len(tasks) == len(durations):
            # Map each task to its duration
            for i, t in enumerate(tasks):
                durations_dict[t] = durations[i]
        # Return the dictionary
        return durations_dict
    # If an error occurs while parsing the task string
    except Exception as e:
        # Print the error message
        print(f'Error while parsing the expression: {e}')
        # Return the empty dictionary
        return durations_dict


###############
    
## IMPACTS
    
################


# This function takes a dictionary as input, converts its values to a list,
# and checks if all values are integers. If all values are integers, it returns the list.
# Otherwise, it returns an empty list.
def impacts_from_dict_to_list(dictionary:dict):
    """
    Convert the values of a dictionary to a list and check if all values are integers.

    Parameters:
    dictionary (dict): The dictionary to process.

    Returns:
    list: A list of the dictionary's values if all values are integers, otherwise an empty list.
    """
    # Convert the dictionary values to a list
    values = list(dictionary.values())
    # Print the list of values
    #print(values)
    # Check if all values are integers
    if all(isinstance(v, int) for v in values):
        # If all values are integers, return the list
        return values
    # If not all values are integers, return an empty list
    return []

# This function takes a string representation of a dictionary as input,
# converts it to a dictionary, and maps each key to a list of its integer values.
# If a key has non-integer values, it maps the key to an empty list.
def extract_impacts_dict(impacts, table):
    """
    Convert a string representation of a dictionary to a dictionary and map each key to a list of its integer values.
    If a key has non-integer values, it maps the key to an empty list.

    Parameters:
    impacts (str): A string representation of a dictionary.

    Returns:
    dict: A dictionary where each key is mapped to a list of its integer values or an empty list if it has non-integer values.
    """
    impacts_dict = {}
    # Iterate over the rows in the 'Tbody' section of the table
    for row in table['props']['children'][1]['props']['children']:
        # Extract the task name
        task = row['props']['children'][0]['props']['children']
        # Initialize an empty dictionary to store the impacts
        impacts_tmp = {}

        # Iterate over the columns of the row, skipping the first one
        for i , col in enumerate(row['props']['children'][1:]):
            # Extract the impact name and value
            impact_name = impacts[i]
            impact_value = int(col['props']['children']['props']['value'])

            # Add the impact to the impacts dictionary
            impacts_tmp[impact_name] = impact_value

        # Add the task and its impacts to the results dictionary
        impacts_dict[task] = impacts_tmp
    return impacts_dict
        
def normalize_dict_impacts(input_dict:dict):
    """
    This function takes a dictionary where the value is another dictionary.
    It checks if for all the values the dictionary is composed by the same keys.
    If a key is missing from a value then it adds it with value 0.

    Parameters:
    input_dict (dict): The input dictionary.

    Returns:
    dict: The dictionary with for each value has a list of all the costs.
    """
    #######################
    ### TODO!!! 
    ## MIGLIORA USANDO MATRICI
    #######################
    # Get all unique keys in the sub-dictionaries
    all_keys = order_keys(input_dict)
    new_dict = {}

    # Iterate over the original dictionary
    for key, sub_dict in input_dict.items():
        # Create a new sub-dictionary for each key in the original dictionary
        new_sub_dict = {}
        for k in all_keys:
            # If the key is in the original sub-dictionary, use its value
            # Otherwise, use 0 as the value
            new_sub_dict[k] = sub_dict.get(k, 0)
        # Add the new sub-dictionary to the new dictionary
        new_dict[key] = new_sub_dict

    return new_dict

def order_keys(impacts:dict):
    all_keys = set().union(*(sub_dict.keys() for sub_dict in impacts.values()))
    # sorting the keys
    all_keys = sorted(list(all_keys))
    return all_keys

#######################

## BOUNDS

########################


def extract_values_bound(input_dict):
    """
    Extract values from a nested dictionary or list.

    Parameters:
    input_dict (dict or list): The dictionary or list to extract values from.
    key (str): The key to look for.

    Returns:
    list: A list of values associated with the key.
    """
    if isinstance(input_dict, dict):
        for k, v in input_dict.items():
            if k == 'value':
                yield v
            if isinstance(v, (dict, list)):
                yield from extract_values_bound(v)
    elif isinstance(input_dict, list):
        for item in input_dict:
            yield from extract_values_bound(item)


def set_max_duration(durations:dict):
    """
    This function takes a dictionary where the value is a list of 2 elements.
    It replaces each list with its last element.

    Parameters:
    durations (dict): The input dictionary where each value is a list of 2 elements.

    Returns:
    dict: The modified dictionary where each list value has been replaced with its last element.
    """
    # Iterate over the items in the dictionary
    for key, value in durations.items():
        #print(key, value)
        # If the value is a list with 2 elements, replace it with its last element
        if isinstance(value, list) and len(value) == 2:
            durations[key] = value[-1]
    return durations


#######################

## PROBABILITIES

########################
def extract_choises_nat(input_string):
    """
    This function takes a string and extracts all non-empty substrings that are inserted as ^ [...] simbolising the natural choises.

    Parameters:
    input_string (str): The input string.

    Returns:
    list: A list of substrings found between square brackets.
    """
    # Use a regular expression to find all substrings between square brackets
    choises = re.findall(r'\^\s*\[(.*?)\]', input_string)

    # Filter out empty strings
    choises = [c for c in choises if c]

    return choises
def extract_choises_user(input_string):
    """
    This function takes a string and extracts all non-empty substrings that are inserted as / [...] simbolising the natural choises.

    Parameters:
    input_string (str): The input string.

    Returns:
    list: A list of substrings found between square brackets.
    """
    # Use a regular expression to find all substrings between square brackets
    choises = re.findall(r'\/\s*\[(.*?)\]', input_string)

    # Filter out empty strings
    choises = [c for c in choises if c]

    return choises
def extract_choises(input_string):
    """
    This function takes a string and extracts all non-empty substrings that are inserted between square brackets.

    Parameters:
    input_string (str): The input string.

    Returns:
    list: A list of substrings found between square brackets.
    """
    # Use a regular expression to find all substrings between square brackets
    choises = re.findall(r'\[(.*?)\]', input_string)

    # Filter out empty strings
    choises = [c for c in choises if c]

    return choises

def create_probabilities_dict(list_choises, prob:dict):
    """
    Create a dictionary mapping choices to probabilities.

    Args:
        list_choises (list): A list of choices.
        prob (dict): A dictionary containing probabilities.

    Returns:
        dict: A dictionary mapping choices to probabilities.
    """
    prob = list(extract_value_durations(prob))
    dict_prob = {}
    for i, c in enumerate(list_choises):
        dict_prob[c] = prob[i]
    return dict_prob


def create_probabilities_names(list_choises):    
    """
    Create a dictionary of probabilities with the given list of choices.

    Args:
        list_choises (list): A list of choices.

    Returns:
        dict: A dictionary of probabilities where each choice is mapped to itself.

    Example:
        >>> choices = ['A', 'B', 'C']
        >>> create_probabilities_names(choices)
        {'A': 'A', 'B': 'B', 'C': 'C'}
    """
    dict_prob = {}
    for c in list_choises:
        dict_prob[c] = c
    return dict_prob

def impacts_dict_to_list(impacts: dict):
    return {key: list(inner_dict.values()) for key, inner_dict in impacts.items()}