from random import randint

from utils.env import ALGORITHMS
from solver.test_aalpy import automata_search_strategy
from utils import check_syntax as cs
" Here the automata is called to calculate the strategies for the process "
def calc_strat(bpmn:dict, bound:dict, algo:str) -> dict:
    print('calc_strat...')
    # check if the bound is empty
    strategies = {}
    if bpmn['expression'] == '':
        return strategies
    bound_list = []
    try:
        bound_list = list(cs.extract_values_bound(bound))
    except Exception as e:
        print(f'Error while parsing the bound: {e}')
        return strategies
    if bound_list == []:
        strategies['error'] = "The bound is empty or None"
        return strategies  # If there are no bound available, we can't calculate the strategies
    args = {
            'expression': "(Task1, Task2), (Task3, Task4)",
            'impacts': {"Task1": [0,1], "Task2": [0,1], "Task3": [0,1], "Task4": [0,1]},
            'names': {},
            'probabilities': {},
            'loop_thresholds': {},
            'durations': {"Task1": 1, "Task2": 1, "Task3": 1, "Task4": 1},
            'delays': {},
            'h': 0
        }
    bpmn = args
    # calculate strategies
    try:
        print('testing...')
        if algo == list(ALGORITHMS.keys())[0]:
            strategies = calc_strategy_paco(bpmn, bound_list)
        elif algo == list(ALGORITHMS.keys())[1]:
            strategies = calc_strategy_algo1(bpmn, bound_list)
        elif algo == list(ALGORITHMS.keys())[2]:
            strategies = calc_strategy_algo2(bpmn, bound_list)
        
    except Exception as e:
        print(f'test failed: {e}')
    return strategies



def calc_strategy_paco(bpmn:dict, bound:list[int]) -> dict:
    strategies = {}
    try:
        print('testing...')
        strat = automata_search_strategy(bpmn, bound)
        if strat.startswith("A strategy") :
            strategies['strat1'] = strat
        else:            
            return strategies
    except Exception as e:
        print(f'test failed: {e}')
    return strategies

def calc_strategy_algo1(bpmn:dict, bound:list[int]) -> dict:
    strategies = {}
    return strategies

def calc_strategy_algo2(bpmn:dict, bound:list[int]) -> dict:
    strategies = {}
    return strategies