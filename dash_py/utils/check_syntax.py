
"""
   File that checks things and useful things 
"""
from utils.env import ALGORITHMS, ALGORITHMS_MISSING_SYNTAX, ALL_SYNTAX
import re
import json
def checkCorrectSyntax(expression:str, h = 0, probabilities={}, impacts={}, loop_thresholds = {}, durations = {}) -> bool:
    """
    Check if the syntax of the BPMN file is correct.
    """
    print('checking syntax in progress...')
    return True


def check_algo_is_usable(expression: str, algo: str) -> bool:
    """
    Check if the costructs in the BPMN is suitable fro the algo.
    """
    if expression == '' or algo == '' or algo not in ALGORITHMS.keys():
        return False
    if algo in ALGORITHMS_MISSING_SYNTAX.keys() and list(ALGORITHMS_MISSING_SYNTAX.get(algo)) != []:
        #print(list(ALGORITHMS_MISSING_SYNTAX.get(algo)))
        for element in list(ALGORITHMS_MISSING_SYNTAX.get(algo)):
            #print(element)
            if element in expression:
                return False               
    print('checking expression within algo in progress...')
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

def extract_tasks(expression: str) -> list[str]:
    """
        Function that extracts the tasks from the  BPMN expression.
    """
    if expression == '' or expression is None:
        return []
    #print(expression)
    if check_ONLY_1_taks(expression):
        print('only 1 task')
        return expression
    
    try: 
       # Create a pattern that matches any of the syntax elements
        pattern = '|'.join(map(re.escape, ALL_SYNTAX))
        
        # Use re.sub to replace all occurrences of the pattern with an empty string
        tasks = re.sub(pattern, '', expression)
        
    except Exception as e:
        print(f'Error while parsing the expression: {e}')
        return []
    
    return  [ t for t in tasks.split() if t  != ' ']

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
    print(values)
    # Check if all values are integers
    if all(isinstance(v, int) for v in values):
        # If all values are integers, return the list
        return values
    # If not all values are integers, return an empty list
    return []

# This function takes a string representation of a dictionary as input,
# converts it to a dictionary, and maps each key to a list of its integer values.
# If a key has non-integer values, it maps the key to an empty list.
def extract_impacts_dict(impacts):
    """
    Convert a string representation of a dictionary to a dictionary and map each key to a list of its integer values.
    If a key has non-integer values, it maps the key to an empty list.

    Parameters:
    impacts (str): A string representation of a dictionary.

    Returns:
    dict: A dictionary where each key is mapped to a list of its integer values or an empty list if it has non-integer values.
    """
    # Convert the string to a dictionary
    impacts = string_to_dict(impacts)
    # Initialize an empty dictionary
    impacts_dict = {}
    # Iterate over the items of the dictionary
    for key, value in impacts.items():
        # Map the key to a list of its integer values or an empty list
        impacts_dict[key] = impacts_from_dict_to_list(value)
    # Return the new dictionary
    return impacts_dict
        

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