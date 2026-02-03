import copy
import numpy as np
from src.paco.saturate_execution.states import States, ActivityState
from src.paco.parser.parse_node import ParseNode, Sequential, Parallel, ExclusiveGateway, Nature, Task, Gateway


def evaluate_expected_impacts(states: States, impacts_size: int) -> (np.float64, np.ndarray):
	impacts = np.zeros(impacts_size, dtype=np.float64)
	probability = np.float64(1.0)

	for node, state in states.activityState.items():
		if (isinstance(node, Nature) and state > ActivityState.WAITING):
			for i in range(len(node.children)):
				if node.children[i] in states.activityState and states.activityState[node.children[i]] > ActivityState.WAITING:
					probability *= node.distribution[i]
					break

		elif isinstance(node,Task) and state > ActivityState.WAITING:
			impacts += node.impacts

	return probability, impacts

def evaluate_expected_impacts_from_parseNode(parseNode: ParseNode, impacts_size: int) -> (np.float64, np.ndarray):
	if isinstance(parseNode, Task):
		return parseNode.impacts

	expected_impacts = np.zeros(impacts_size, dtype=np.float64)
	if isinstance(parseNode, Gateway):
		for i in range(len(parseNode.children)):
			probability = np.float64(1.0)
			if isinstance(parseNode, Nature):
				probability = parseNode.distribution[i]
			expected_impacts += probability * evaluate_expected_impacts_from_parseNode(parseNode.children[i], impacts_size)

	return expected_impacts