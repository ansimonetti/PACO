from datetime import datetime
import os
from utils.print_sese_diagram import print_sese_diagram
from utils.automa import calc_strategy_paco


bpmn_ex = {
    "bpmn_linear": {"expression": "SimpleTask1, Task1", 
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2]}, 
          "durations": {"SimpleTask1": 100, "Task1": 100}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {}, "delays": {}
        },

    "bpmn_only_choices": {"expression": "SimpleTask1, (Task1 / [C1] T2)", 
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2] , "T2": [3, 1]}, 
          "durations": {"SimpleTask1": 100, "Task1": 100, "T2":100}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {}, "delays": {}
        },
    
    "bpmn_only_natures": {"expression": "SimpleTask1, (Task1 ^ [N1] T2)", 
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1]}, 
          "durations": {"SimpleTask1": 100, "Task1": 100, "T2":100}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6}, "names": {}, "delays": {}
        },
    
    "bpmn_seq_choices": {"expression": "SimpleTask1,  (Task1 / [C1] T2),  (T3 / [C2] T4)", 
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]}, 
          "durations": {"SimpleTask1": 100, "Task1": 100}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {}, "delays": {}
        },

    "bpmn_seq_natures": {"expression": "SimpleTask1,  (Task1 ^ [N1] T2),  (T3 ^ [N2] T4)", 
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]}, 
          "durations": {"SimpleTask1": 100, "Task1": 100}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6, "N2": 0.7}, "names": {}, "delays": {}
        },

    "bpmn_choices_natures": {"expression": "(Cutting, ((HP ^ [N1]LP ) || ( FD / [C1] RD)), (HPHS / [C2] LPLS))", 
          "h": 0, 
          "impacts": {"Cutting": [11, 15], "HP": [4, 2], "LP": [3, 1] , "FD": [8, 9], "RD": [10, 5] , "HPHS": [4, 7], "LPLS": [3, 8]}, 
          "durations": {"Cutting": 1, "HP": 1, "LP": 1, "FD": 1, "RD":1 , "HPHS": 1, "LPLS": 1}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6}, "names": {}, "delays": {}
        },
}


def test_calc_strategy_paco(bpmn_ex_dicts:dict, bound = [20,20]):

    for key , bpmn in bpmn_ex_dicts.items():
        
        print(f' type bpmn: {key}, strategy {bpmn}')
        
        # per disegnare 
        
        # bpmn_svg_folder = "assets/bpmnTest/"
        # if not os.path.exists(bpmn_svg_folder):
        #     os.makedirs(bpmn_svg_folder)
        # # Create a new SESE Diagram from the input
        # name_svg =  bpmn_svg_folder + "bpmn_"+ str(datetime.timestamp(datetime.now())) +".png"
        # print_sese_diagram(**bpmn, outfile=name_svg) 
        

        # CHIAMA LA FUNZIONE per calcolo paco
        strategies = calc_strategy_paco(bpmn, bound)
        print(f' type bpmn: {key}, strategy {strategies}')

test_calc_strategy_paco(bpmn_ex)