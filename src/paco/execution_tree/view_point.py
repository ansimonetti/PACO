import math
from abc import ABC, abstractmethod

from src.paco.parser.parse_node import ParseNode, Sequential, Nature, Parallel, Loop, Choice, Task
from src.paco.saturate_execution.states import States, states_info


class ViewPoint(ABC):
	def __init__(self, id: int, states: States, decisions: tuple[ParseNode], is_final_state: bool, natures: tuple, choices:tuple, pending_choices:set, pending_natures:set, parent): #Parent is ExecutionTree
		self.id = id
		self.states = states
		self.decisions = decisions
		self.is_final_state = is_final_state #If is leaf and the execution is finished
		self.is_leaf = is_final_state or len(pending_choices) + len(choices) == 0
		self.natures = natures
		self.choices = choices
		self.pending_choices = pending_choices
		self.pending_natures = pending_natures
		self.parent = parent
		self.transitions: dict[tuple, 'ExecutionTree'] = {}

	def __str__(self) -> str:
		return str(self.states)

	def __hash__(self):
		return hash(str(self))

	def add_child(self, subTree: 'ExecutionTree'):
		transition = []
		for i in range(len(subTree.root.decisions)):
			transition.append((subTree.root.decisions[i].parent,
							   subTree.root.decisions[i]))

		#for i in range(len(self.choices_natures)):
		#	transition.append((self.choices_natures[i], subTree.root.decisions[i],))

		self.transitions[tuple(transition)] = subTree


	@staticmethod
	def text_format(text: str, line_length: int):
		parts = []
		current_part = ""
		char_count = 0

		for char in text:
			current_part += char
			char_count += 1
			if char == ';' and char_count >= line_length:
				parts.append(current_part)
				current_part = ""
				char_count = 0

		if current_part:
			parts.append(current_part)

		return "\\n".join(parts)

	def common_dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, previous_node: States = None):
		#result = str(self).replace('(', '').replace(')', '').replace(';', '_').replace(':', '_').replace('-', "neg").replace(' | ', '_')
		result = f'\"{self.id}\"'

		if not full:
			return result

		result += f' [label=\"'

		s, d = self.states.str(previous_node)
		s = "Execution State:\n{" + s + "}"
		d = "Execution Time:\n{" + d + "}"

		label = f"ID: {self.id}\n"  # ""
		if state:
			label += s
		if state and executed_time:
			label += ",\n"
		if executed_time:
			label += d

		line_length = int(1.3 * math.sqrt(len(label)))
		return result + (self.text_format(label, line_length)) + "\", "

	@abstractmethod
	def dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, previous_node: States = None):
		pass

	@abstractmethod
	def dot_info_str(self):
		pass

	@abstractmethod
	def to_dict(self) -> dict:
		s = {"id": self.id,
			 "states": self.states.to_dict(),
			 "decisions": [d.id for d in self.decisions],
			 "is_final_state": self.is_final_state,
			 "is_leaf": self.is_leaf,
			 "natures": [n.id for n in self.natures],
			 "choices": [c.id for c in self.choices],
			 "pending_choices": [pc.id for pc in self.pending_choices],
			 "pending_natures": [pn.id for pn in self.pending_natures],
			 "transitions": {
				 str([(decision[0].id, decision[1].id) for decision in decisions]): nextViewPoint.root.to_dict()
				 for decisions, nextViewPoint in self.transitions.items()
			 }
			 }
		return s



def get_next_task(node: ParseNode):
	type_by_name = type(node).__name__
	if isinstance(node, Sequential) or type_by_name == 'Sequential':
		return get_next_task(node.children[0])

	if isinstance(node, Parallel) or type_by_name == 'Parallel':
		sx_node, sx_name, sx_color = get_next_task(node.children[0])
		dx_node, dx_name, dx_color = get_next_task(node.children[1])

		return node, f"{sx_name} || {dx_name}", 'white'

	if isinstance(node, Choice) or type_by_name == 'Choice':
		color = 'orange'
	elif isinstance(node, Nature) or isinstance(node, Loop) or type_by_name == 'Loop' or type_by_name == 'Nature':
		color = 'yellowgreen'
	elif isinstance(node, Task) or type_by_name == 'Task':
		color = 'lightblue'
	else:
		raise Exception(f"view_point:get_next_task: {node} not recognized, type:{type(node)}")

	return node, node.name, color


def view_point_node_info(node: ViewPoint) -> str:
	result = f"ID:{node.id}:decisions:<"
	for n in list(node.decisions):
		result += str(n.id) + ";"
	result = result[:-1]

	if len(node.choices) > 0:
		result += ">:choices:<"
		tmp = ""
		for n in node.choices:
			tmp += str(n.id) + ";"
		result += tmp[:-1]
	if len(node.natures) > 0:
		result += ">:natures:<"
		tmp = ""
		for n in node.natures:
			tmp += str(n.id) + ";"
		result += tmp[:-1]

	return result + ">:status:\n" + states_info(node.states)

