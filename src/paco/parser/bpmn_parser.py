from lark import Lark

from src.utils.env import (
    LOOP_PROBABILITY,
    EXPRESSION,
    IMPACTS,
    PROBABILITIES,
    DURATIONS,
    DELAYS,
    H,
    LOOP_ROUND,
)

from .grammar import sese_diagram_grammar
from .parse_node import Choice, Loop, Nature, Parallel, Sequential, Task
from .parse_tree import ParseTree

SESE_PARSER = Lark(sese_diagram_grammar, parser='lalr')
DEFAULT_UNFOLDING_NUMBER = 3


def create_parse_tree(bpmn: dict):
    tree = SESE_PARSER.parse(bpmn[EXPRESSION])
    #print(tree.pretty())
    root_parse_tree, last_id, pending_choice, pending_natures, pending_loops = parse(tree, bpmn[PROBABILITIES], bpmn[IMPACTS], bpmn[DURATIONS], bpmn[DELAYS], h=bpmn[H], loop_probability=bpmn[LOOP_PROBABILITY], loop_round=bpmn[LOOP_ROUND])
    parse_tree = ParseTree(root_parse_tree)

    return parse_tree, pending_choice, pending_natures, pending_loops


def parse(lark_tree, probabilities, impacts, durations, delays, loop_probability, loop_round, h = 0, parent = None, index_in_parent = 0, id = 0):
    pending_choices = set()
    pending_natures = set()
    pending_loops = set()

    if lark_tree.data == 'task':
        name = lark_tree.children[0].value
        impact = impacts.get(name, [])
        task = Task(parent, index_in_parent, id, name=name, impact=impact[0:len(impact) - h], duration=durations[name])
        #print(f"Task: {task.name}, Impact: {task.impact}, Non-cumulative Impact: {task.non_cumulative_impact}, Duration: {task.duration}, ID: {id}")
        return task, id, pending_choices, pending_natures, pending_loops

    if lark_tree.data == 'loop_probability':
        name = lark_tree.children[0].value
        loop_prob = loop_probability.get(name, 0.5)
        loop_bound = loop_round.get(name, DEFAULT_UNFOLDING_NUMBER)
        loop = Loop(parent, index_in_parent, id, name=name, probability=loop_prob, bound=loop_bound)
        pending_loops.add(loop)

        children = lark_tree.children[1]
        child, last_id, pending_choices, pending_natures, pending_loops = parse(children, probabilities, impacts, durations, delays, loop_probability, loop_round, id=id+1, h=h, parent=loop, index_in_parent=0)
        loop.set_children([child])

        return loop, last_id, pending_choices, pending_natures, pending_loops

    if lark_tree.data in {'choice', 'natural'}:
        name = lark_tree.children[1].value

        if lark_tree.data == 'choice':
            if lark_tree.children[1].value not in delays.keys():
                raise ValueError(f"Delay for {lark_tree.children[1].value} not found in the delays dictionary")

            node = Choice(parent, index_in_parent, id, name, max_delay=delays[lark_tree.children[1].value])
            #print(f"Choice: {name}, Max Delay: {node.max_delay}, ID: {id}")
            pending_choices.add(node)

        else:#Natural
            if lark_tree.children[1].value not in probabilities:
                raise ValueError(f"Probability for {lark_tree.children[1].value} not found in the probabilities dictionary")

            p = probabilities[lark_tree.children[1].value]
            node = Nature(parent, index_in_parent, id, name, distribution=[p, 1-p])
            #print(f"Nature: {name}, Probability: {node.distribution}, ID: {id}")
            pending_natures.add(node)

        left_child, last_id, left_pending_choice, left_pending_natures, left_pending_loops = parse(lark_tree.children[0], probabilities, impacts, durations, delays, loop_probability, loop_round, id =id + 1, h=h, parent=node, index_in_parent=0)
        right_child, last_id, right_pending_choice, right_pending_natures, right_pending_loops = parse(lark_tree.children[2], probabilities, impacts, durations, delays, loop_probability, loop_round, id =last_id + 1, h=h, parent=node, index_in_parent=1)


    elif lark_tree.data in {'sequential', 'parallel'}:
        if lark_tree.data == 'sequential':
            node = Sequential(parent, index_in_parent, id)
        else:
            node = Parallel(parent, index_in_parent, id)
        left_child, last_id, left_pending_choice, left_pending_natures, left_pending_loops = parse(lark_tree.children[0], probabilities, impacts, durations, delays, loop_probability, loop_round, id =id + 1, h=h, parent=node, index_in_parent=0)
        right_child, last_id, right_pending_choice, right_pending_natures, right_pending_loops = parse(lark_tree.children[1], probabilities, impacts, durations, delays, loop_probability, loop_round, id =last_id + 1, h=h, parent=node, index_in_parent=1)
        #print(f"{lark_tree.data.capitalize()}: ID: {id}")

    else:
        raise ValueError(f"Unhandled lark_tree type: {lark_tree.data}")

    node.set_children([left_child, right_child])
    pending_choices.update(left_pending_choice)
    pending_choices.update(right_pending_choice)
    pending_natures.update(left_pending_natures)
    pending_natures.update(right_pending_natures)
    pending_loops.update(left_pending_loops)
    pending_loops.update(right_pending_loops)

    return node, last_id, pending_choices, pending_natures, pending_loops

