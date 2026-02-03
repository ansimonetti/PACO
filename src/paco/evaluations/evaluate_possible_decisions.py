from itertools import product
import numpy as np
from src.paco.parser.parse_node import ParseNode, Task, ExclusiveGateway, Nature

 #TODO Daniel: on the fly implementation

def evaluate_min_max_impacts(node: ParseNode):
	if isinstance(node, Task):
		return np.array(node.impacts), np.array(node.impacts)

	sx_child_min_impacts, sx_child_max_impacts = evaluate_min_max_impacts(node.children[0])
	dx_child_min_impacts, dx_child_max_impacts = evaluate_min_max_impacts(node.children[1])

	if isinstance(node, ExclusiveGateway):
		if isinstance(node, Nature):
			min_impacts = node.probability * sx_child_min_impacts + (1 - node.probability) * dx_child_min_impacts
			max_impacts = node.probability * sx_child_max_impacts + (1 - node.probability) * dx_child_max_impacts
		else:
			min_impacts = np.minimum(sx_child_min_impacts, dx_child_min_impacts)
			max_impacts = np.maximum(sx_child_max_impacts, dx_child_max_impacts)

	else: #Parallel or Sequential
		min_impacts = sx_child_min_impacts + dx_child_min_impacts
		max_impacts = sx_child_max_impacts + dx_child_max_impacts

	return min_impacts, max_impacts


def evaluate_possible_decisions(probability, impacts, pending_activities: list, pending_choices: list, impacts_size: int):
	min_impacts = np.zeros(impacts_size, dtype=np.float64)
	max_impacts = np.zeros(impacts_size, dtype=np.float64)
	for pending_activity in pending_activities:
		choice_min_impacts, choice_max_impacts = evaluate_min_max_impacts(pending_activity)
		min_impacts += choice_min_impacts
		max_impacts += choice_max_impacts

	choices_min_impacts = np.array(min_impacts)
	choices_max_impacts = np.array(max_impacts)
	pending_choices_impacts = {}
	for pending_choice in pending_choices:
		choice_min_impacts, choice_max_impacts = evaluate_min_max_impacts(pending_choice)
		choices_min_impacts += choice_min_impacts
		choices_max_impacts += choice_max_impacts

		sx_min_impacts, sx_max_impacts = evaluate_min_max_impacts(pending_choice.sx_child)
		dx_min_impacts, dx_max_impacts = evaluate_min_max_impacts(pending_choice.dx_child)

		pending_choices_impacts[pending_choice] = (sx_min_impacts, sx_max_impacts), (dx_min_impacts, dx_max_impacts)

	#if choices_min_impacts and choices_max_impacts out of bound -> stop here

	branches_possible_expected_impacts = {}
	for branch in list(product([True, False], repeat=len(pending_choices))):
		branch_min_impacts = np.array(min_impacts)
		branch_max_impacts = np.array(max_impacts)

		branch_decisions = []
		for choice, take_sx in zip(pending_choices_impacts.keys(), branch):
			if take_sx:
				pending_decision_impacts = pending_choices_impacts[choice][0]
				decision = choice.children[0]
			else:
				pending_decision_impacts = pending_choices_impacts[choice][1]
				decision = choice.children[1]

			branch_decisions.append(decision)
			branch_min_impacts += pending_decision_impacts[0]
			branch_max_impacts += pending_decision_impacts[1]

		branch_min_expected_impacts = probability * (branch_min_impacts + impacts)
		branch_max_expected_impacts = probability * (branch_max_impacts + impacts)

		branches_possible_expected_impacts[tuple(branch_decisions)] = (branch_min_expected_impacts, branch_max_expected_impacts)

	return (choices_min_impacts, choices_max_impacts), branches_possible_expected_impacts
