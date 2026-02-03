import numpy as np
from src.paco.parser.parse_node import ParseNode
from src.paco.saturate_execution.states import States
from src.paco.execution_tree.view_point import ViewPoint


class ExecutionViewPoint(ViewPoint):
	def __init__(self, id: int, states: States, decisions: tuple[ParseNode], choices:tuple, natures: tuple,
				 is_final_state: bool, probability: np.float64, impacts: np.ndarray, cei_top_down: np.ndarray, cei_bottom_up: np.ndarray, pending_choices: set, pending_natures:set, parent = None):

		super().__init__(id, states, decisions, is_final_state, natures, choices, pending_choices, pending_natures, parent)

		self.probability = probability
		self.impacts = impacts
		self.cei_top_down = cei_top_down
		self.cei_bottom_up = cei_bottom_up

		#TODO check
		'''
		pending_activities = [node for node in states.activityState if node.parent not in pending_choices and states.activityState[node] == ActivityState.WAITING]

		self.possible_expected_impacts, self.branches_possible_expected_impacts = evaluate_possible_decisions(self.probability, self.impacts, pending_activities, pending_choices, len(impacts_names))

	def pruning(self, bound: np.ndarray):
		possible_decisions = {}
		for branch_possible_decisions, branch_possible_expected_impacts in self.branches_possible_expected_impacts.items():
			max_possible_expected_impacts = branch_possible_expected_impacts[1]
			min_possible_expected_impacts = branch_possible_expected_impacts[0]

			if np.all(compare_bound(min_possible_expected_impacts, bound) > 0):
				# You can stop here is guaranteed to stay over the bound so it is not a valid choose and this is a dead branch
				continue

			if np.all(compare_bound(max_possible_expected_impacts, bound) <= 0):
				# You can stop here is guaranteed to stay under the bound
				possible_decisions = {branch_possible_decisions : branch_possible_expected_impacts}
				break

			possible_decisions[branch_possible_decisions] = branch_possible_expected_impacts

		possible_transitions = {}
		for transitions, next_child in self.transitions.items():
			decisions = tuple(decision for decision in list(transitions) if isinstance(decision, Choice))
			if decisions in possible_decisions:
				possible_transitions[transitions] = next_child
			else:
				print("Pruning: ", decisions, " not in ", possible_decisions)

		'''

	def dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, frontier:set[int]=set(), previous_node: States = None):
		result = super().common_dot_str(full, state, executed_time, previous_node)
		if full:
			if self.id in frontier:
				result += " style=filled, fillcolor=\"lightblue\""

			result += "];\n"

		return result

	def dot_info_str(self):
		nature_label = ""
		for nature in self.natures:
			nature_label += f"{nature.name}, "

		label = f"Impacts: {self.impacts}\n"
		if self.probability != 1:
			label += f"Probability: {round(self.probability, 2)}\n"

		label += f"EI Current: {self.cei_top_down}\n"
		if not self.is_final_state:
			label += f"EI Max: {self.cei_bottom_up}\n"


		choice_label = ""
		for choice in self.choices:
			choice_label += f"{choice.name}, "
		if choice_label != "":
			label += "Actual Choice: " + choice_label[:-2] + "\n"
		if nature_label != "":
			label += "Actual Nature: " + nature_label[:-2] + "\n"
		choice_label = ""
		for choice in self.pending_choices:
			choice_label += f"{choice.name}, "
		#if choice_label != "":
		#	label += f"Pending Choices: {choice_label[:-2]}\n"
		nature_label = ""
		for nature in self.pending_natures:
			nature_label += f"{nature.name}, "
		#if nature_label != "":
		#	label += f"Pending Natures: {nature_label[:-2]}\n"

		#if not self.is_final_state and self.is_leaf:
		#	label += "Not terminal state\n"

		#TODO
		'''
		label += f"Guaranteed Impacts Max: {self.possible_expected_impacts[1]}\n"
		label += f"Guaranteed Impacts Min: {self.possible_expected_impacts[0]}\n"
		'''

		return self.dot_str(full=False)[:-1] + "description\"", f" [label=\"{label}\", shape=rect];\n"

	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({
			"probability": self.probability,
			"impacts": self.impacts.tolist(),
			"cei_top_down": self.cei_top_down.tolist(),
			"cei_bottom_up": self.cei_bottom_up.tolist()
		})
		return base