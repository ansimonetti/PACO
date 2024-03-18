
from lark import Tree, Token
import pydot
from PIL import Image
from env import SESE_PARSER
from utils.print_sese_diagram import dot_sese_diagram, dot_task, dot_exclusive_gateway, dot_loop_gateway, dot_parallel_gateway, dot_rectangle_node
"""
    funzioni prese dal notebook
"""
def print_sese_tree(expression, h = 0, probabilities={}, impacts={}, loop_thresholds = {}, outfile="out.png"):
    expression_tree = SESE_PARSER.parse(expression)
    tree, id = dot_tree(expression_tree, 0, h, probabilities, impacts, loop_thresholds)
    dot_string = "digraph my_graph{"+ tree +"}"
    graph = pydot.graph_from_dot_data(dot_string)[0]
    graph.write_png(outfile)
    return Image.open(outfile)  

def dot_tree(t, id=0, h=0,  prob={}, imp={}, loops={}, token_is_task=True):
    if type(t) == Token:
        label = (t.value)  
        code = dot_task(id, label, h, imp[label] if label in imp else None) if token_is_task else dot_rectangle_node(id, label)
        return code, id
    if type(t) == Tree:
        label = (t.data)
        code = ""
        last_id = id
        child_ids = []
        for i, c in enumerate(t.children):
            if (label != 'xor_probability' or i != 1) and (label != 'loop_probability' or i !=0 ):
                dot_code, last_id = dot_tree(c, last_id, h, prob, imp, loops)
            else:    
                dot_code, last_id = dot_tree(c, last_id, h, prob, imp, loops, token_is_task=False)
            code += f'\n {dot_code}'
            child_ids.append(last_id)
            last_id += 1
        if label in {'xor', 'xor_probability'}:
            code += dot_exclusive_gateway(last_id, label)
        elif label in {'loop', 'loop_probability'}: 
            code += dot_loop_gateway(last_id, label)
        elif label == 'parallel':
            code += dot_parallel_gateway(last_id, label)        
        else:    
            code += f'\n node_{last_id}[label="{label}"];'
        edge_labels = ['','',''] 
        if label == "xor_probability":
            prob_key = t.children[1].value
            edge_labels = [f'{prob[prob_key] if prob_key  in prob else 0.5 }','',
                           f'{1 - prob[prob_key] if prob_key  in prob else 0.5 }']
        if label == "loop_probability":
            prob_key = t.children[0].value
            edge_labels = [f'{loops[prob_key] if prob_key  in loops else 0.5 }','']     
        for ei,i in enumerate(child_ids):
            edge_label = edge_labels[ei]
            code += f'\n node_{last_id} -> node_{i} [label="{edge_label}"];'
        return code, last_id 