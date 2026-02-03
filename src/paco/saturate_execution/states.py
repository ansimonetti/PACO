import enum
from src.paco.parser.parse_node import ParseNode, Sequential, Parallel, Choice, Task
from collections import defaultdict


class ActivityState(enum.IntEnum):
	WILL_NOT_BE_EXECUTED = -1
	WAITING = 0
	ACTIVE = 1
	COMPLETED = 2
	COMPLETED_WITHOUT_PASSING_OVER = 3

	def __str__(self):
		return str(self.value)


class States:
	def __init__(self, state: ParseNode = None, activityState: ActivityState = ActivityState.WAITING, executed_time: int = 0):
		self.activityState = defaultdict(lambda: ActivityState.WAITING)
		self.executed_time = defaultdict(lambda: 0)

		if state is not None:
			self.add(state, activityState, executed_time)

	def add(self, state: ParseNode, activityState: ActivityState, executed_time: int):
		self.activityState[state] = activityState
		self.executed_time[state] = executed_time

	def update(self, states: 'States'):
		self.activityState.update(states.activityState)
		self.executed_time.update(states.executed_time)

	def str(self, previousStates: 'States' = None):
		result_s = ""
		result_d = ""

		if previousStates is None:
			for state in sorted(self.activityState.keys(), key=lambda x: x.id):
				result_s += str(state.id) + ":" + str(self.activityState[state]) + ";"
				if state in self.executed_time:
					result_d += str(state.id) + ":" + str(self.executed_time[state]) + ";"
		else:
			for state in sorted(self.activityState.keys(), key=lambda x: x.id):
				if state not in previousStates.activityState or self.activityState[state] != previousStates.activityState[state]:
					result_s += str(state.id) + ":" + str(self.activityState[state]) + ";"
					if state in self.executed_time:
						result_d += str(state.id) + ":" + str(self.executed_time[state]) + ";"

		# Remove last  ";"
		return result_s[:-1], result_d[:-1]

	def __str__(self):
		s, d = self.str()
		return s + " | " + d

	def to_dict(self):
		return {
			"activityState": {k.id: v for k, v in self.activityState.items()},
			"executed_time": {k.id: v for k, v in self.executed_time.items()}
		}

	@staticmethod
	def from_dict(data: dict, parseTreeNodes: dict):
		states = States()
		states.activityState.update({parseTreeNodes[int(k)]: ActivityState(v) for k, v in data["activityState"].items()})
		states.executed_time.update({parseTreeNodes[int(k)]: v for k, v in data["executed_time"].items()})
		return states

def node_info(node: ParseNode, states: States):
	name = "" if not (isinstance(node, Sequential) and isinstance(node, Parallel)) else "name:" + node.name + '; '
	result = f"id:{node.id}; {name} q|s: {states.activityState[node]}; q|delta: {states.executed_time[node]}; "

	if isinstance(node, Choice):
		result += f"delta: {node.max_delay}"
	elif isinstance(node, Task):
		result += f"delta: {node.duration}"

	return result


def states_info(states):
	result = ''
	for s in sorted(states.activityState.keys(), key=lambda x: x.id):
		result += node_info(s, states) + "\n"

	return result
