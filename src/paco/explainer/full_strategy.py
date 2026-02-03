import copy
import random
from itertools import product
import numpy as np
from src.paco.evaluations.evaluate_decisions import find_all_decisions, evaluate_decisions
from src.paco.evaluations.evaluate_impacts import evaluate_expected_impacts
from src.paco.explainer.bdd.bdd import Bdd
from src.paco.explainer.strategy_tree import saturate_execution
from src.paco.explainer.strategy_view_point import StrategyViewPoint
from src.paco.explainer.explanation_type import ExplanationType
from src.paco.saturate_execution.create_branches import get_excluded_gateways
from src.paco.saturate_execution.states import States, ActivityState
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode
from src.paco.execution_tree.execution_tree import ExecutionTree


def make_decisions(region_tree: ParseTree, strategyViewPoint: StrategyViewPoint, explainers: dict[ParseNode, Bdd], impacts: np.ndarray, states: States, pending_choices:set, pending_natures:set) -> (States, list[ParseNode], set, set):
	if len(strategyViewPoint.choices) == 0:
		return states, [], pending_choices, pending_natures

	decisions = []
	for choice in strategyViewPoint.choices:
		if choice not in explainers: #Arbitrary
			print(f"Choice not explained (arbitrary): {str(choice)}, random decision")
			random.seed()
			if random.choice([0, 1]) == 0:
				decision_true = choice.children[0]
				decision_false = choice.children[1]
			else:
				decision_true = choice.children[1]
				decision_false = choice.children[0]

		elif explainers[choice].typeStrategy == ExplanationType.FORCED_DECISION:
			bdd = explainers[choice]
			strategyViewPoint.explained_choices[choice] = bdd

			print(f"Choice {choice.name} has just one decision to take")
			decision_true = explainers[choice].class_0
			decision_false = choice.children[1] if decision_true == choice.children[0] else choice.children[0]

		else:
			#print("Explaining choice: ", choice.name)
			bdd = explainers[choice]
			strategyViewPoint.explained_choices[choice] = bdd

			if bdd.typeStrategy == ExplanationType.CURRENT_IMPACTS:
				vector = impacts
				#print("Current impacts: ", vector)
			elif bdd.typeStrategy == ExplanationType.DECISION_BASED:
				actual_decisions, features_names = find_all_decisions(region_tree)
				vector = evaluate_decisions(actual_decisions, strategyViewPoint.states.activityState)
				#print(f"Decisions:\n{features_names}\n{vector}")
			else:
				raise Exception("make_decisions: TypeStrategy not implemented: " + str(bdd.typeStrategy))

			decision_true = bdd.choose(vector)
			decision_false = choice.children[1] if decision_true == choice.children[0] else choice.children[0]

		decisions.append(decision_true)
		#print("Decision True: ", decision_true.name if decision_true.name else decision_true.id)
		#print("Decision False: ", decision_false.name if decision_false.name else decision_false.id)
		states.activityState[decision_true] = ActivityState.ACTIVE
		states.activityState[decision_false] = ActivityState.WILL_NOT_BE_EXECUTED
		excluded_choice, excluded_nature = get_excluded_gateways(decision_false)


	#print("make_decisions:Decisions: ", [d.name if d.name else d.id for d in decisions])
	return states, decisions, pending_choices, pending_natures


def nature_clausure(natures: list[ParseNode], states: States, decisions: list[ParseNode], pending_choices:set, pending_natures:set):
	branches = dict[tuple, States]()
	if len(natures) == 0:
		branches[tuple(decisions)] = (states, pending_choices, pending_natures)
		return branches

	branches_decisions = list(product([True, False], repeat=len(natures)))
	excluded_choice, excluded_nature = set(), set()
	#print(f"combinations:{branches_decisions}")
	for branch_choices in branches_decisions:
		branch_states = copy.deepcopy(states)
		branch_decisions = copy.deepcopy(decisions)

		for i in range(len(natures)):
			node = natures[i]

			if branch_choices[i]:
				activeNode = node.children[0]
				inactiveNode = node.children[1]
			else:
				activeNode = node.children[1]
				inactiveNode = node.children[0]

			branch_states.activityState[activeNode] = ActivityState.ACTIVE
			branch_states.activityState[inactiveNode] = ActivityState.WILL_NOT_BE_EXECUTED
			excluded_choice, excluded_nature = get_excluded_gateways(inactiveNode)
			branch_decisions.append(activeNode)

		branch_pending_choices = set(choice for choice in pending_choices if choice not in excluded_choice)
		branch_pending_natures = set(nature for nature in pending_natures if nature not in excluded_nature)


		branches[tuple(branch_decisions)] = (branch_states, branch_pending_choices, branch_pending_natures)

	return branches


def full_strategy(region_tree: ParseTree, explained_choices: dict[ParseNode, Bdd], impacts_size: int, pending_choices:set, pending_natures:set,
				  states: States = None, decisions_taken: tuple[ParseNode] = None, id: int = 0):
	if states is None:
		states = States(region_tree.root, ActivityState.WAITING, 0)
		decisions_taken = (region_tree.root,)

	states, is_final, choices, natures, pending_choices, pending_natures = saturate_execution(region_tree, states, pending_choices, pending_natures)
	probability, impacts = evaluate_expected_impacts(states, impacts_size)

	strategyViewPoint = StrategyViewPoint(bpmn_root=region_tree.root, id=id, states=states,
										  decisions=decisions_taken, choices=choices,
										  natures=natures, is_final_state=is_final,
										  impacts=impacts, probability=probability,
										  pending_choices=pending_choices,
										  pending_natures=pending_natures)

	strategyTree = ExecutionTree(strategyViewPoint)
	#print(view_point_node_info(strategyViewPoint), f"Impacts: {impacts}\n")

	if is_final:
		return strategyTree, [strategyViewPoint], probability*impacts, probability*strategyViewPoint.executed_time, pending_choices, pending_natures, id

	chosen_states, next_decisions, pending_choices, pending_natures = make_decisions(region_tree, strategyViewPoint, explained_choices, impacts, copy.deepcopy(states), pending_choices, pending_natures)

	branches = nature_clausure(natures, chosen_states, next_decisions, pending_choices, pending_natures)

	children = []
	expected_impacts = np.zeros(impacts_size, dtype=np.float64)
	expected_time = 0
	for next_decisions, (branch_states, pending_choices, pending_natures) in branches.items():
		sub_tree, new_children, new_expected_impacts, new_expected_time, pending_choices, pending_natures, id = full_strategy(region_tree, explained_choices, impacts_size, pending_choices, pending_natures, branch_states, tuple(next_decisions), id + 1)
		strategyViewPoint.add_child(sub_tree)
		children.extend(new_children)
		expected_impacts += new_expected_impacts
		expected_time += new_expected_time

	return strategyTree, children, expected_impacts, expected_time, pending_choices, pending_natures, id
