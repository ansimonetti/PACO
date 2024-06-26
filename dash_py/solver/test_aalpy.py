from random import seed
seed(42)
#############
# https://github.com/DES-Lab/AALpy/wiki/SUL-Interface,-or-How-to-Learn-Your-Systems
#############

from aalpy.oracles import RandomWalkEqOracle, StatePrefixEqOracle
from aalpy.learning_algs import run_Lstar, run_KV
from aalpy.utils import visualize_automaton, load_automaton_from_file

from lark import Lark
import os, sys
from IPython.display import display
import numpy as np
from itertools import product
import pydot
from datetime import datetime
from solver.view_points import VPChecker
from solver.tree_lib import CNode, CTree, print_sese_custom_tree
from solver.tree_lib import from_lark_parsed_to_custom_tree as Lark_to_CTree
from solver.tree_lib import print_sese_custom_tree as print_sese_CTree
from utils.env import AUTOMATON_TYPE, LOOPS_PROB, PATH_AUTOMATON_IMAGE, PATH_AUTOMATON_IMAGE_SVG, RESOLUTION, SESE_PARSER, TASK_SEQ, IMPACTS, NAMES, PROBABILITIES, DURATIONS, LOOP_THRESHOLD, DELAYS,H, PATH_AUTOMATON, PATH_AUTOMATON_CLEANED, IMPACTS_NAMES
from solver.gCleaner import gCleaner
from explainer.explainer import explainer
# import array_operations

from solver.automaton_graph import AutomatonGraph
from solver.solver import GameSolver

current_directory = os.path.dirname(os.path.realpath('tree_lib.py'))
# Add the current directory to the Python path
sys.path.append(current_directory)

os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

# sese_diagram_grammar = r"""
# ?start: xor

# ?xor: parallel
#     | xor "/" "[" NAME "]" parallel -> choice
#     | xor "^" "[" NAME "]" parallel -> natural

# ?parallel: sequential
#     | parallel "||" sequential  -> parallel

# ?sequential: region
#     | sequential "," region -> sequential    

# ?region: 
#      | NAME   -> task
#      | "(@" xor "@)" -> loop
#      | "(@" "[" NAME "]"  xor "@)" -> loop_probability
#      | "(" xor ")"

# %import common.CNAME -> NAME
# %import common.NUMBER
# %import common.WS_INLINE

# %ignore WS_INLINE
# """

#SESE_PARSER = Lark(sese_diagram_grammar, parser='lalr')

# ex = "((Task8 ^ [N1] Task3), (Task1 / [C3] Task2),(Task6 / [C1] Task7))|| (Task9, (Task4 / [C2] Task5))"
# exi = {"Task1": [0,1], "Task2": [0,2], "Task3": [3,3], "Task4": [1,2], "Task5": [2,1], "Task6": [1,0], "Task7": [1,5], "Task8": [0,3], "Task9": [0,3]}
# exd = {"Task1": 1, "Task2": 1,"Task4": 1, "Task3": 1, "Task5": 1, "Task6": 1, "Task7": 1, "Task8": 3, "Task9": 2}
# exn = {"C1": 'Choice1', "C2": 'Choice2', "C3": 'Choice3'}
# exdl = {"C1": np.Inf, "C2": 0, "C3": 0} #maximum delays for the choices
# exp = {"N1": 0.2}

# ex = "(Task1, Task2), (Task3, Task4)"
# exi = {"Task1": [0,1], "Task2": [0,1], "Task3": [0,1], "Task4": [0,1]}
# exd = {"Task1": 1, "Task2": 1, "Task3": 1, "Task4": 1}
# exn = {}
# exdl = {} #maximum delays for the choices
# exp = {}

ex = "(Task1 ^ [N1] Task2) || (Task3 / [C1] Task4)"
exi = {"Task1": [1,1], "Task2": [0,1], "Task3": [2,1], "Task4": [0,1]}
exd = {"Task1": 3, "Task2": 1, "Task3": 3, "Task4": 4}
exn = {"C1": 'Choice1'}
exdl = {"C1": 2} #maximum delays for the choices
exp = {"N1":0.3}

# ex = "Task1 || (Task2, (Task3 / [C1] Task4))"
# exi = {"Task1": [0,1], "Task2": [0,2], "Task3": [3,3], "Task4": [1,2]}
# exd = {"Task1": 1, "Task2": 1,"Task4": 1, "Task3": 1}
# exn = {"C1": 'Choice1'}
# exdl = {"C1": 5} #maximum delays for the choices
# exp = {}

# ex = "(T1 ^ [N1] T2),((T3 / [C1] T4)||(T5 / [C2] T6))"
# exi = {"T1": [2,3], "T2": [4,1], "T3": [2,3], "T4": [3,1], "T5": [2,1], "T6": [1,2]}
# exd = {"T1": 1, "T2": 1,"T4": 1, "T3": 1, "T5":4, "T6":2}
# exn = {"C1": 'Choice1', "C2": 'Choice2'}
# exdl = {"C1": 5, "C2": 2} #maximum delays for the choices
# exp = {"N1": 0.3}

args = {
    'expression': ex,
    'impacts': exi,
    'names': exn,
    'probabilities': exp,
    'loop_thresholds': {},
    'durations': exd,
    'delays': exdl,
    'h': 0
}

# tree = SESE_PARSER.parse(args['expression'])
# custom_tree, last_id = Lark_to_CTree(tree, args['probabilities'], args['impacts'], args['durations'], args['names'], args['delays'], h=args['h'])
# number_of_nodes = last_id + 1

# print_sese_CTree(custom_tree, h=args['h']).show()

# sul = VPChecker(custom_tree, number_of_nodes) #system under learning, with step, pre and post methods defined
# input_al = sul.accepted_alphabet

# eq_oracle = RandomWalkEqOracle(input_al, sul, num_steps=100, reset_after_cex=True, reset_prob=0.01)
# eq_oracle_2 = StatePrefixEqOracle(input_al, sul, walks_per_state=100, walk_len=100, depth_first=True)

# learned_automaton= run_Lstar(input_al, sul, eq_oracle=eq_oracle, automaton_type=AUTOMATON_TYPE, cache_and_non_det_check=False,
#                   print_level=1, max_learning_rounds=20)
# #learned_automaton = run_KV(input_al, sul, eq_oracle,automaton_type=AUTOMATON_TYPE, cache_and_non_det_check=True, print_level=2)#, max_learning_rounds=100)

# #visualize_automaton(learned_automaton)
# learned_automaton.save("automaton.dot")

# cleaner = gCleaner("automaton.dot")
# cleaner.save_cleaned_dot_graph("automaton_cleaned.dot")
# cleaner.save_cleaned_pdf_graph("automaton_cleaned")

# mealy = load_automaton_from_file(path='automaton_cleaned.dot', automaton_type=AUTOMATON_TYPE, compute_prefixes=True)
# ag = AutomatonGraph(mealy, sul)

# goal = [7,6]
# solver = GameSolver(ag, goal)
# winning_set = solver.compute_winning_final_set()
# if winning_set != None: print("\n\nA strategy could be found\n")
# else: print("\n\nFor this specific instance a strategy does not exist\n")
# for s in states:
#     for k in s.output_fun.keys():
#         if s.output_fun[k] == 1:
#             k = k.replace(" ", "")
#             k_tuple = tuple(map(int, k[1:-1].split(',')))
#             executed_tasks = [i for i in range(number_of_nodes) if k_tuple[i] == 2 and sul.types[i] == sul.TASK]
#             impact = []
#             for t in executed_tasks:
#                 impact = array_operations.sum(impact, array_operations.product(sul.taskDict[t]["impact"], sul.taskDict[t]["probability"]))
#             print(s.state_id, k, impact)

def automata_search_strategy(bpmn: dict, bound: list[int]) -> str:
    """
    This function takes a BPMN diagram and a bound as input, and returns a strategy for the automaton.
    
    Parameters:
    bpmn (dict): The BPMN diagram represented as a dictionary.
    bound (list[int]): The bound for the automaton.

    Returns:
    str: A string representing the strategy for the automaton.
    """
    try:
        # Parse the task sequence from the BPMN diagram
        tree = SESE_PARSER.parse(bpmn[TASK_SEQ])
        print(tree.pretty)
        print(f'{datetime.now()} bound {bound}')
        # Convert the parsed tree into a custom tree and get the last ID
        custom_tree, last_id = Lark_to_CTree(tree, bpmn[PROBABILITIES],
                                            bpmn[IMPACTS], bpmn[DURATIONS], 
                                            bpmn[NAMES], bpmn[DELAYS], h=bpmn[H], loops_prob=bpmn[LOOPS_PROB])

        # Calculate the number of nodes in the tree
        number_of_nodes = last_id + 1
        print('Number of nodes:', number_of_nodes)
        # Create a system under learning (SUL) with the custom tree and number of nodes
        sul = VPChecker(custom_tree, number_of_nodes)
        print(sul.VPDict, sul.accepted_alphabet)
        print('eseguito sul')
        print_sese_custom_tree(custom_tree)#.show() # ,sul, custom_tree
        # Get the accepted alphabet from the SUL
        input_al = sul.accepted_alphabet

        # Create an equivalence oracle using a random walk
        eq_oracle = RandomWalkEqOracle(input_al, sul, num_steps=100, reset_after_cex=True, reset_prob=0.01)
        print(f'{datetime.now()} eseguito eq_oracle') #, sul.print_vp_list()
        # Learn the automaton using the L* algorithm
        learned_automaton= run_Lstar(input_al, sul, eq_oracle=eq_oracle, automaton_type=AUTOMATON_TYPE, cache_and_non_det_check=False,
                        print_level=2, max_learning_rounds=20)
        print(f'{datetime.now()} eseguito run_Lstar')
        # Save the learned automaton
        learned_automaton.save(PATH_AUTOMATON)

        # Clean the automaton
        cleaner = gCleaner(PATH_AUTOMATON)
        cleaner.remove_null_nodes_from_graph()
        print(f'{datetime.now()} eseguito cleaner')
        # Load the cleaned automaton
        mealy = load_automaton_from_file(path=PATH_AUTOMATON_CLEANED, automaton_type=AUTOMATON_TYPE, compute_prefixes=True)
        print('eseguito mealy')
        # Create an automaton graph with the cleaned automaton and the SUL
        ag = AutomatonGraph(mealy, sul)
        print(f'{datetime.now()} eseguito ag')
        # Create a game solver with the automaton graph and the bound
        solver = GameSolver(ag, bound)
        print('eseguito solver')
        # Compute the winning final set
        winning_set = solver.compute_winning_final_set()

        # Print the winning set
        print(f'{datetime.now()} winning set:')
        print(winning_set)

        # If a winning set exists, return a strategy
        if winning_set != None: 
            graphs = pydot.graph_from_dot_file(PATH_AUTOMATON_CLEANED)
            graph = graphs[0] 
            # color the winning nodes            
            for el in winning_set: 
                node = graph.get_node(el[0])[0]
                node.set_style('filled')
                node.set_fillcolor('green')            
            
            graph.write_svg(PATH_AUTOMATON_IMAGE_SVG)
            graph.set('dpi', RESOLUTION)
            graph.write_png(PATH_AUTOMATON_IMAGE)   
            expected_impacts = [s[1] for s in winning_set]
            expected_impacts = [sum(values) for values in zip(*expected_impacts)]
            impacts = "\n".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES], expected_impacts))
            s = f"A strategy could be found, which has as an expected imact of : {impacts} "
            explainer(custom_tree)
            return s
        else: 
            # If no winning set exists, return a message indicating that no strategy exists
            s = "\n\nFor this specific instance a strategy does not exist\n"
            return s
    except Exception as e:
        # If an error occurs, print the error and return a message indicating that an error occurred
        print(f'test failed in PACO execution : {e}')
        s = f'Error! Finding the strategy failed in PACO execution : {e}'
        return s