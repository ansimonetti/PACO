import copy
import enum
import numpy as np
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode
from src.paco.evaluations.evaluate_decisions import evaluate_decisions, find_all_decisions

class ExplanationType(enum.IntEnum):
	FORCED_DECISION = -1
	CURRENT_IMPACTS = 0
	DECISION_BASED = 1
	HYBRID = 2

	def __str__(self):
		return str(self.name)


def current_impacts(decisions: dict[ParseNode, set['ExecutionTree']]) -> (list, list):
	#print("Current impacts:")
	impacts, impacts_labels = [], []
	for decision_taken, executionTrees in decisions.items():
		#print(f"Decision: {decision_taken.name if decision_taken.name else decision_taken.id} has {len(executionTrees)} execution trees")
		for executionTree in executionTrees:
			#print(f"I({decision_taken.name if decision_taken.name else decision_taken.id}): {executionTree.root.impacts}")
			impacts.append(copy.deepcopy(executionTree.root.impacts))
			impacts_labels.append(decision_taken.id)

	return impacts, impacts_labels



def decision_based(region_tree: ParseTree, decisions_taken: dict[ParseNode, set['ExecutionTree']]) -> (list[ParseNode], list[np.ndarray], list):
	decisions, decisions_names = find_all_decisions(region_tree)
	decision_vectors, labels = [], []
	#print(f"Decision based:\n{decisions_names}")
	for decision_taken, executionTrees in decisions_taken.items():
		#print(f"Decision: {decision_taken.name if decision_taken.name else decision_taken.id} has {len(executionTrees)} execution trees")
		for executionTree in executionTrees:
			decision_vectors.append(evaluate_decisions(decisions, executionTree.root.states.activityState))
			labels.append(decision_taken.id)
			#print(f"DB({decision_taken.name if decision_taken.name else decision_taken.id}): {decision_vectors[-1]}")

	return decisions_names, decision_vectors, labels
