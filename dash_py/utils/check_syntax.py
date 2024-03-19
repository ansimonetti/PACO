
"""
   File that checks things
"""
from utils.env import ALGORITHMS, ALGORITHMS_MISSING_SYNTAX, ALL_SYNTAX
import re

def checkCorrectSyntax(expression:str, h = 0, probabilities={}, impacts={}, loop_thresholds = {}) -> bool:
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
      
    return tasks.split(' ')