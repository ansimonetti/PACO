from random import randint

" Here the automata is called to calculate the strategies for the process "
def calc_strat(bpmn:dict, bound:dict) -> dict:
    print('calc_strat...')
    strategies = {}
    if bpmn['expression'] == '':
        return strategies
    founded = randint(0, 1)
    if founded == 0:
        strategies['strat1'] = 'SomeTask1, SomeTask2, SomeTask3'
        strategies['strat2'] = 'SomeTask1, SomeTask3'
    return strategies