from solver.tree_lib import print_sese_custom_tree
from utils.env import PATH_AUTOMATON_CLEANED, SESE_PARSER
import pydot 

def explainer(custom_tree, automata_path = PATH_AUTOMATON_CLEANED):
    graph = pydot.graph_from_dot_file(automata_path)
    print(graph)
    print_sese_custom_tree(custom_tree).show()