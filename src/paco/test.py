import random
import re
from src.paco.optimizer.pareto_optimizer import pareto_optimal_impacts
from src.utils.env import (
    EXPRESSION,
    H,
    IMPACTS,
    DURATIONS,
    IMPACTS_NAMES,
    LOOP_PROBABILITY,
    DELAYS,
    PROBABILITIES,
    LOOP_ROUND,
)

#fare replacement di ^ con nature o choice

expression = "(((((((T1 , T2) ^[C1] ((T3 , T4) || T5)) , ((T6 , T7) / [N1] T8)) , ((T9 ^ [C2] T10) , (T11 , ((T12 , T13) , T14)))) , (((T15 ^ [C3] T16) / [N3] T17) / [N2] (T18 , T19))) ^ [C4] ((((T20 , T21) , T22) || T23) , ((T24 , T25) ^ [C5] T26))) || ((T27 || ((T28 / [N4] T29) ^ [N5] (T30 ^ [C6] (((T31 , T32) , ((T33 / [N7] T34) ^ [C7] T35)) , (T36 , T37))))) || T38))"
expression = expression.replace(" ", "").replace('^[C', '/[C').replace('/[N', '^[N')


tasks = sorted(set(re.findall(r'T\d+', expression)))
natures = sorted(set(re.findall(r'N\d+', expression)))
choices = sorted(set(re.findall(r'C\d+', expression)))

impacts_names = ["A", "B"]

impacts_range = [1, 50]
duration_range = [1, 100]
delay_range = [0, 10]


bpmn = {
    EXPRESSION: expression,
    H: 0,
    IMPACTS: {task: [random.randint(impacts_range[0], impacts_range[1]) for _ in impacts_names] for task in tasks},
    DURATIONS: {task: [1, random.randint(duration_range[0], duration_range[1])] for task in tasks},
    IMPACTS_NAMES: impacts_names,
    LOOP_PROBABILITY: {},
    DELAYS: {choice: random.randint(delay_range[0], delay_range[1]) for choice in choices},
    PROBABILITIES: {nature: round(random.uniform(0.1, 0.9), 2) for nature in natures},
    LOOP_ROUND: {}
}

try:
    '''
    bpmn_svg_folder = "assets/bpmnTest/"
    if not os.path.exists(bpmn_svg_folder):
        os.makedirs(bpmn_svg_folder)
    # Create a new SESE Diagram from the input
    #name_svg =  bpmn_svg_folder + "bpmn_"+ str(datetime.timestamp(datetime.now())) +".png"
    print(name_svg)
    '''
    #print_sese_diagram(**bpmn_ex_article, outfile='test.png')#name_svg)
    dict_output, bound, expected_impacts, min_solutions = pareto_optimal_impacts(bpmn)

except Exception as e:
    print(f'Error: {e}')

