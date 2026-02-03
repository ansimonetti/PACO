import numpy as np

from src.paco.execution_tree.view_point import ViewPoint
from src.paco.explainer.bdd.bdd import Bdd
from src.paco.explainer.explanation_type import ExplanationType
from src.paco.parser.parse_node import ParseNode
from src.paco.saturate_execution.states import States

class StrategyViewPoint(ViewPoint):
	def __init__(self, bpmn_root: ParseNode, id: int, states: States, decisions: tuple[ParseNode], choices: dict[ParseNode:Bdd], natures: list[ParseNode],
				 is_final_state: bool, probability:np.float64, impacts: np.ndarray, pending_choices:set, pending_natures:set, parent = None, expected_impacts: np.ndarray = None, expected_time: np.float64 = None, explained_choices: dict[ParseNode:Bdd] = {}):
		super().__init__(id, states, decisions, is_final_state, tuple(natures), tuple(choices), pending_choices, pending_natures, parent)

		self.probability = probability
		self.impacts = impacts
		self.executed_time = states.executed_time[bpmn_root]
		self.explained_choices = explained_choices

		if expected_impacts is None or expected_time is None:
			self.expected_impacts = probability * impacts
			self.expected_time = probability * self.executed_time
		else:
			self.expected_impacts = expected_impacts
			self.expected_time = expected_time


	def dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, previous_node: States = None):
		result = super().common_dot_str(full, state, executed_time, previous_node)
		if full:
			#print(f"ID: {self.id}, choice: ", len(self.choices), "natures: ", len(self.natures))
			choices_number = len(self.choices)
			natures_number = len(self.natures)
			if choices_number > 0 and natures_number == 0:
				result += "style=filled, fillcolor=\"orange\""
			elif choices_number == 0 and natures_number > 0:
				result += "style=filled, fillcolor=\"yellowgreen\""
			elif choices_number > 0 and natures_number > 0:
				result += "style=wedged, fillcolor=\"yellowgreen;0.5:orange\""

			result += "];\n"

		return result

	def dot_info_str(self):
		label = f" [label=\""
		label += f"Time: {self.executed_time}\n"
		label += f"Impacts: {self.impacts}\n"
		if self.probability != 1:
			label += f"Probability: {round(self.probability, 2)}\n"
			label += f"Exp. Time: {round(self.expected_time, 2)}\n"
			label += f"Exp. Impacts: {np.round(self.expected_impacts, 2)}\n"

		nature_label = ""
		for nature in self.natures:
			nature_label += f"{nature.name}, "
		if nature_label != "":
			label += "Actual Nature: " + nature_label[:-2] + "\n"

		if len(self.pending_choices) + len(self.choices)  > 0:
			choice_label = ""
			for choice in self.choices:
				choice_label += f"{choice.name}: "
				if choice in self.explained_choices:
					bdd = self.explained_choices[choice]
					choice_label += str(ExplanationType(bdd.typeStrategy)).replace("_", " ").lower()
				else:
					choice_label += 'arbitrary'

			if choice_label != "":
				label += "Actual Choice:\n" + choice_label + "\n"

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

		label += "\", shape=rect];\n"
		return self.dot_str(full=False)[:-1] + "description\"", label

	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({
			"probability": self.probability,
			"impacts": self.impacts.tolist(),
			"executed_time": self.executed_time,
			"expected_impacts": self.expected_impacts.tolist(),
			"expected_time": self.expected_time
		})
		return base