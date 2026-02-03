import numpy as np

from src.paco.execution_tree.view_point import get_next_task
from src.paco.saturate_execution.states import ActivityState
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode, Gateway, ExclusiveGateway


def find_all_decisions_rec(node: ParseNode) -> list[ParseNode]:
	if not isinstance(node, Gateway):
		return []

	if node.children[0] is None or node.children[1] is None:
		raise ValueError(f"Gateway {node.__class__} with ID: {node.id} has missing children")

	decisions = []
	if isinstance(node, ExclusiveGateway):
		decisions.extend([node.children[0], node.children[1]])

	decisions.extend(find_all_decisions_rec(node.children[0]))
	decisions.extend(find_all_decisions_rec(node.children[1]))

	return decisions


def find_all_decisions(region_tree: ParseTree) -> (list[ParseNode], list[str]):
	decisions = sorted(find_all_decisions_rec(region_tree.root), key=lambda d: d.id)
	#decisions_names = [f"{d.parent.name}_{'0' if d.parent.dx_child == d else '1'}" for d in decisions]
	decisions_names = []
	for d in decisions:
		_, decision_name, _ = get_next_task(d)
		decisions_names.append(f"{d.parent.name}->{decision_name}")
	# print(f"Decisions: {decisions_names}")
	return decisions, decisions_names


def evaluate_decisions(decisions: list[ParseNode], execution: ActivityState) -> np.ndarray:
	return np.array([0 if decision not in execution or execution[decision] < ActivityState.ACTIVE
					 else 1 for decision in decisions], dtype='int')
