from lark import Tree, Token
import pydot
from pydot import *
from PIL import Image
from utils.env import PATH_IMAGE_BPMN_LARK, PATH_IMAGE_BPMN_LARK_SVG, SESE_PARSER, RESOLUTION
"""
    funzioni prese dal notebook
"""
def print_sese_diagram(expression, h = 0, probabilities={}, impacts={}, loop_thresholds = {}, outfile=PATH_IMAGE_BPMN_LARK, outfile_svg = PATH_IMAGE_BPMN_LARK_SVG,
                        graph_options = {}, durations = {}, names = {}, delays = {}, impacts_names = [], resolution_bpmn = RESOLUTION):
    tree = SESE_PARSER.parse(expression)
    diagram = wrap_sese_diagram(tree=tree, h=h, probabilities= probabilities, impacts= impacts, loop_thresholds=loop_thresholds, durations=durations, names=names, delays=delays, impacts_names=impacts_names)
    global_options = f'graph[ { ", ".join([k+"="+str(graph_options[k]) for k in graph_options])  } ];'
    dot_string = "digraph my_graph{ \n rankdir=LR; \n" + global_options + "\n" + diagram +"}"
    graphs = pydot.graph_from_dot_data(dot_string)
    graph = graphs[0]  
    graph.write_svg(outfile_svg)
    #print(graph)  
    graph.set('dpi', resolution_bpmn)
    graph.write_png(outfile)    
    return  Image.open(outfile)   

def dot_sese_diagram(t, id = 0, h = 0, prob={}, imp={}, loops = {}, dur = {}, imp_names = []):
    if type(t) == Token:
        label = t.value
        return dot_task(id, label, h, imp[label] if label in imp else None, dur[label] if label in dur else None, imp_names), id, id
    if type(t) == Tree:
        label = t.data
        if label == 'task':
            return dot_sese_diagram(t.children[0], id, h, prob, imp, loops, dur, imp_names)
        code = ""
        id_enter = id
        last_id = id_enter + 1
        child_ids = []
        for i, c in enumerate(t.children):
            if (label != 'natural' or i != 1) and (label != 'choice' or i != 1) and (label != 'loop_probability' or i !=0 ):
                dot_code, enid, exid = dot_sese_diagram(c, last_id, h, prob, imp, loops, dur, imp_names)
                code += f'\n {dot_code}'
                child_ids.append((enid, exid))
                last_id = exid + 1
        if label != "sequential":    
            id_exit = last_id
            if label == "choice":
                code += dot_exclusive_gateway(id_enter)
                code += dot_exclusive_gateway(id_exit)
            elif label == 'natural':
                code += dot_probabilistic_gateway(id_enter)
                code += dot_probabilistic_gateway(id_exit)
            elif label in {'loop', 'loop_probability'}: 
                code += dot_loop_gateway(id_enter)
                if label == 'loop':
                    code += dot_loop_gateway(id_exit)
                else:
                    code += dot_loop_gateway(id_exit)
            else: 
                label_sym = '+'    
                node_label = f'[shape=diamond label="{label_sym}" style="filled" fillcolor=yellowgreen]'
                code += f'\n node_{id_enter}{node_label};'
                id_exit = last_id
                code += f'\n node_{id_exit}{node_label};'
        else: 
            id_enter = child_ids[0][0]
            id_exit = child_ids[-1][1]    
        edge_labels = ['','',''] 
        if label == "natural":
            prob_key = t.children[1].value
            edge_labels = [f'{prob[prob_key] if prob_key  in prob else 0.5 }',
                           f'{round(1 - prob[prob_key], 2) if prob_key  in prob else 0.5 }']
        if label == "loop_probability":
            prob_key = t.children[0].value
            edge_labels = ['',f'{loops[prob_key] if prob_key  in loops else 0.5 }']
        if label != "sequential":
            for ei,i in enumerate(child_ids):
                edge_label = edge_labels[ei]
                code += f'\n node_{id_enter} -> node_{i[0]} [label="{edge_label}"];'
                code += f'\n node_{i[1]} -> node_{id_exit};'
            if label in  {'loop', 'loop_probability'}:  
                code += f'\n node_{id_exit} -> node_{id_enter} [label="{edge_labels[1]}"];'
        else:
            for ei,i in enumerate(child_ids):
                edge_label = edge_labels[ei]
                if ei != 0:
                    code += f'\n node_{child_ids[ei - 1][1]} -> node_{i[0]} [label="{edge_label}"];'              
    return code, id_enter, id_exit

def wrap_sese_diagram(tree, h = 0, probabilities={}, impacts={}, loop_thresholds = {}, durations={}, names={}, delays={}, impacts_names=[]):
    code, id_enter, id_exit = dot_sese_diagram(tree, 0, h, probabilities, impacts, loop_thresholds, durations, imp_names = impacts_names)   
    code = '\n start[label="" style="filled" shape=circle fillcolor=palegreen1]' +   '\n end[label="" style="filled" shape=doublecircle fillcolor=orangered] \n' + code
    code += f'\n start -> node_{id_enter};'
    code += f'\n node_{id_exit} -> end;'
    return code

def get_tasks(t):
    trees = [subtree for subtree in t.iter_subtrees()]
    v = {subtree.children[0].value for subtree in   filter(lambda x: x.data == 'task', trees)}
    return v

def dot_task(id, name, h=0, imp=None, dur=None, imp_names = []):
    label = name
    #print(f"impacts in dot task : {imp}")
    if imp is not None: # modifica per aggiungere impatti e durate in modo leggibile 
        if h == 0:
            imp =  ", ".join(f"{key}: {value}" for key, value in zip(imp_names, imp))
            label += f", impacts: {imp}"
            label += f", dur: {str(dur)}"  
        else: 
            label += str(imp[0:-h])
            label += str(imp[-h:]) 
            label += f", dur:{str(dur)}"   
    return f'\n node_{id}[label="{label}", shape=rectangle style="rounded,filled" fillcolor="lightblue"];'

def dot_exclusive_gateway(id, label="X"):
    return f'\n node_{id}[shape=diamond label={label} style="filled" fillcolor=orange];'

def dot_probabilistic_gateway(id, label="N"):
    return f'\n node_{id}[shape=diamond label={label} style="filled" fillcolor=orange];' 

def dot_loop_gateway(id, label="X"):
    return f'\n node_{id}[shape=diamond label={label} style="filled" fillcolor=yellow];' 

def dot_parallel_gateway(id, label="+"):
    return f'\n node_{id}[shape=diamond label={label} style="filled" fillcolor=yellowgreen];'

def dot_rectangle_node(id, label):
    return f'\n node_{id}[shape=rectangle label={label}];'  