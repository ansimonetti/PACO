import pydot
from PIL import Image
import numpy as np

from utils import env

class CTree:
    def __init__(self, root: 'CNode') -> None:
        self.root = root
    
    def copy(self) -> 'CTree':
        r = self.root
        if r.type == 'task':
            return CTree(r.copy())
        else:
            r_copy = r.copy()
            left_children = r.childrens[0].copy()
            left_children.root.parent = r_copy
            right_children = r.childrens[1].copy()
            right_children.root.parent = r_copy
            r_copy.set_childrens([left_children, right_children])
            return CTree(r_copy)

class CNode:
    # Simple custom class for representing nodes of a graph
    #
    #

    # types = ['task', 'sequential', 'parallel', 'natural', 'choice', 'loop', 'loop_probability']
    isLeaf = True
    childrens = None

    def __init__(self, parent, index_in_parent, type, id = None, impact = [], non_cumulative_impact = [], probability = None, name = None, short_name = None, ttr = 0, max_delay = 0, duration = 0, incoming_impact_vectors = []) -> None:
        self.id = id
        self.name = name
        self.short_name = short_name
        self.parent = parent
        self.index_in_parent = index_in_parent
        self.type = type
        self.impact = impact
        self.non_cumulative_impact = non_cumulative_impact
        self.probability = probability
        self.ttr = ttr
        self.max_delay = max_delay
        self.duration = duration
        self.incoming_impact_vectors = incoming_impact_vectors

    def copy(self) -> 'CNode':
        return CNode(self.parent, self.index_in_parent, self.type, self.id, self.impact, self.non_cumulative_impact, self.probability, self.name, self.short_name, self.ttr, self.max_delay, self.duration, self.incoming_impact_vectors)

    def set_childrens(self, childrens: list[CTree]) -> None:
        self.childrens = childrens
        self.isLeaf = False

    def __eq__(self, other: 'CNode') -> bool:
        if other == None: return False
        if self.id == other.id: return True
        else: return False

def recursiveUnfoldingOfLoop(children_list, id, parent, index_in_parent, loop_prob):
    #recursive construction of the final unfolded tree
    if len(children_list) == 1:
        return children_list[0], id
    else:
        tmp = CNode(parent, index_in_parent, "natural", id=id+1, probability=loop_prob)
        seq = CNode(tmp, 0, "sequential", id=id+2)
        last_id = id+2
        unfolded, last_id = recursiveUnfoldingOfLoop(children_list[2:], last_id, seq, 1, loop_prob)
        children_list[0].root.parent = seq
        children_list[0].root.index_in_parent = 0
        children_list[1].root.parent = tmp
        children_list[1].root.index_in_parent = 1
        seq.set_childrens([children_list[0], unfolded])
        tmp.set_childrens([CTree(seq), children_list[1]])
        return CTree(tmp), last_id

def from_lark_parsed_to_custom_tree(lark_tree, probabilities, impacts, durations, names, delays, loops_prob, loop_round =3, h = 0, loop_thresholds = None, parent = None, index_in_parent = None, id = 0):
    if lark_tree.data == 'task':
        impact = impacts[lark_tree.children[0].value] if lark_tree.children[0].value in impacts else []
        tmp_node = CNode(parent, index_in_parent, lark_tree.data, id = id, name = lark_tree.children[0].value, impact = impact[0:len(impact)-h], non_cumulative_impact = impact[len(impact)-h:], duration=durations[lark_tree.children[0].value])
        return CTree(tmp_node), id
    elif (lark_tree.data == 'choice'):
        tmp_node = CNode(parent, index_in_parent, lark_tree.data, id = id, name=names[lark_tree.children[1].value], short_name=lark_tree.children[1].value, max_delay=delays[lark_tree.children[1].value] if lark_tree.children[1].value in delays.keys() else np.inf)
        left_children, last_id = from_lark_parsed_to_custom_tree(lark_tree.children[0], probabilities, impacts, durations, names, delays, loops_prob, loop_round, id = id + 1, h=h, loop_thresholds=loop_thresholds, parent=tmp_node, index_in_parent=0)
        right_children, last_id = from_lark_parsed_to_custom_tree(lark_tree.children[2], probabilities, impacts, durations, names, delays, loops_prob, loop_round, id = last_id + 1, h=h, loop_thresholds=loop_thresholds, parent=tmp_node, index_in_parent=1)
        childrens = [left_children, right_children]
        tmp_node.set_childrens(childrens)
        return CTree(tmp_node), last_id
    elif (lark_tree.data in {'sequential', 'parallel'}):
        tmp_node = CNode(parent, index_in_parent, lark_tree.data, id = id)
        left_children, last_id = from_lark_parsed_to_custom_tree(lark_tree.children[0], probabilities, impacts, durations, names, delays, loops_prob, loop_round, id = id + 1, h=h, loop_thresholds=loop_thresholds, parent=tmp_node, index_in_parent=0)
        right_children, last_id = from_lark_parsed_to_custom_tree(lark_tree.children[1], probabilities, impacts, durations, names, delays, loops_prob, loop_round, id = last_id + 1, h=h, loop_thresholds=loop_thresholds, parent=tmp_node, index_in_parent=1)
        childrens = [left_children, right_children]
        tmp_node.set_childrens(childrens)
        return CTree(tmp_node), last_id
    elif (lark_tree.data == 'natural'):
        tmp_node = CNode(parent, index_in_parent, lark_tree.data, id = id, probability=probabilities[lark_tree.children[1].value] if lark_tree.children[1].value in probabilities else 0.5)
        left_children, last_id = from_lark_parsed_to_custom_tree(lark_tree.children[0], probabilities, impacts, durations, names, delays, loops_prob, loop_round, id = id + 1, h=h, loop_thresholds=loop_thresholds, parent=tmp_node, index_in_parent=0)
        right_children, last_id = from_lark_parsed_to_custom_tree(lark_tree.children[2], probabilities, impacts, durations, names, delays, loops_prob, loop_round, id = last_id + 1, h=h, loop_thresholds=loop_thresholds, parent=tmp_node, index_in_parent=1)
        childrens = [left_children, right_children]
        tmp_node.set_childrens(childrens)
        return CTree(tmp_node), last_id
    elif (lark_tree.data == 'loop_probability'):
        loop_prob = loop_prob[lark_tree.children[0].value] if lark_tree.children[0].value in loops_prob else 0.5
        number_of_unfoldings = loop_round[lark_tree.children[0].value] if lark_tree.children[0].value in loop_round else env.DEFAULT_UNFOLDING_NUMBER
        num_of_regions_to_replicate = ((number_of_unfoldings - 1)*2) + 1
        # loops have only one child
        id -= 1
        children_list = []
        for dup in range(num_of_regions_to_replicate):
            children, last_id = from_lark_parsed_to_custom_tree(lark_tree.children[1], probabilities, impacts, durations, names, delays, loops_prob, loop_round, id = id + 1, h=h, loop_thresholds=loop_thresholds, parent=None, index_in_parent=0) #parent and index will be modified
            children_list.append(children.copy())
            id = last_id
        unfolded_tree, last_id = recursiveUnfoldingOfLoop(children_list, last_id, parent, index_in_parent, loop_prob)
        return unfolded_tree, last_id
    
def print_sese_custom_tree(tree, h = 0, probabilities={}, impacts={}, loop_thresholds = {}, outfile="assets/out.png"):
    tree = dot_tree(tree, h, probabilities, impacts, loop_thresholds)
    dot_string = "digraph my_graph{"+ tree +"}"
    graph = pydot.graph_from_dot_data(dot_string)[0]
    graph.write_png(outfile)
    return Image.open(outfile).convert('RGB')

def dot_task(id, name, duration, h=0, imp=None):
    label = name
    if imp is not None:
        if h == 0:
            label += str(imp)
        else: 
            label += str(imp[0:-h])
            label += str(imp[-h:])
    label += ' dur:'
    label += str(duration)
    label += ' id:'
    label += str(id)
    return f'node_{id}[label="{label}", shape=rectanble style="rounded,filled" fillcolor="lightblue"];'

def dot_exclusive_gateway(id, label="X"):
    return f'\n node_{id}[shape=diamond label="{label}" style="filled" fillcolor=orange];'    

def dot_loop_gateway(id, label="X"):
    return f'\n node_{id}[shape=diamond label="{label}" style="filled" fillcolor=yellow];' 

def dot_parallel_gateway(id, label="+"):
    return f'\n node_{id}[shape=diamond label="{label}" style="filled" fillcolor=yellowgreen];'

def dot_rectangle_node(id, label):
    return f'\n node_{id}[shape=rectangle label="{label}"];'

def dot_tree(t: CTree, h=0, prob={}, imp={}, loops={}, token_is_task=True):
    r = t.root
    if r.type == 'task':
        label = (r.name)
        impact = r.impact
        duration = r.duration
        impact.extend(r.non_cumulative_impact)
        code = dot_task(r.id, label, duration, h, impact if len(impact) != 0 else None) if token_is_task else dot_rectangle_node(r.id, label)
        return code
    else:
        label = (r.type)
        code = ""
        child_ids = []
        for i, c in enumerate(r.childrens):
            dot_code = dot_tree(c, h, prob, imp, loops)
            code += f'\n {dot_code}'
            child_ids.append(c.root.id)
        if label == 'choice':
            if r.max_delay == np.inf: dly_str = 'inf'
            else: dly_str = str(r.max_delay)
            code += dot_exclusive_gateway(r.id, r.name + ' id:' + str(r.id) + ' dly:' + dly_str)
        elif label == 'natural':
            code += dot_exclusive_gateway(r.id, label + ' id:' + str(r.id))
        elif label == 'loops_prob': 
            code += dot_loop_gateway(r.id, label + ' id:' + str(r.id))
        elif label == 'parallel':
            code += dot_parallel_gateway(r.id, label + ' id:' + str(r.id))        
        else:    
            code += f'\n node_{r.id}[label="{label + " id:" + str(r.id)}"];'
        edge_labels = ['',''] 
        if label == "natural":
            proba = r.probability
            edge_labels = [f'{proba}', f'{round((1 - proba), 2)}']
        if label == "loops_prob":
            proba = r.probability
            edge_labels = [f'{proba}', f'{round((1 - proba), 2)}']  
        for ei,i in enumerate(child_ids):
            edge_label = edge_labels[ei]
            code += f'\n node_{r.id} -> node_{i} [label="{edge_label}"];'
        return code