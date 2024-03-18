from random import randint

from solver.test_aalpy import test

" Here the automata is called to calculate the strategies for the process "
def calc_strat(bpmn:dict, bound:dict) -> dict:
    print('calc_strat...')
    strategies = {}
    if bpmn['expression'] == '':
        return strategies
    founded = randint(0, 1)
    # prova test 
    try:
        test()
    except Exception as e:
        print(f'test failed: {e}')
    if founded == 0:
        strategies['strat1'] = 'SomeTask1, SomeTask2, SomeTask3'
        strategies['strat2'] = 'SomeTask1, SomeTask3'
    return strategies