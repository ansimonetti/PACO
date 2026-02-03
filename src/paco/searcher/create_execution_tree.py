import numpy as np
from src.paco.evaluations.evaluate_impacts import evaluate_expected_impacts_from_parseNode, evaluate_expected_impacts
from src.paco.execution_tree.execution_view_point import ExecutionViewPoint
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode
from src.paco.saturate_execution.saturate_execution import saturate_execution_decisions
from src.paco.saturate_execution.states import States, ActivityState
from src.paco.execution_tree.execution_tree import ExecutionTree

def evaluate_viewPoint(id, region_tree, decisions: tuple[ParseNode], states:States, pending_choices:set, pending_natures:set, solution_tree:ExecutionTree, impacts_size:int) -> (ExecutionViewPoint, dict[tuple[ParseNode], (States,set,set)]):
	states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(region_tree, states, pending_choices, pending_natures)
	probability, impacts = evaluate_expected_impacts(states, impacts_size)
	cei_bottom_up = np.zeros(impacts_size, dtype=np.float64)

	earlyStop = len(pending_choices) + len(choices) == 0 and len(pending_natures) + len(natures) > 0
	earlyStop = False # TODO Daniel: earlyStop
	if earlyStop:
		print(f"EarlyStop:id:{id}: No pending choices, pending nature: {[n.name for n in pending_natures]}, nature: {[n.name for n in natures]}")
		for nature in natures:
			cei_bottom_up += evaluate_expected_impacts_from_parseNode(nature, impacts_size)
		for node in list(states.activityState.keys()):
			if states.activityState[node] == ActivityState.WAITING:
				cei_bottom_up += evaluate_expected_impacts_from_parseNode(node, impacts_size)
		#		print(f"Node:id:{node.id}:", evaluate_expected_impacts_from_parseNode(node, impacts_size))

		branches = {}

	#cei_bottom_up = probability * (cei_bottom_up + impacts)
	#impacts += cei_bottom_up
	#print("cei_bottom_up:", cei_bottom_up)
	#print("Impacts + cei_bottom_up:", impacts)

	return (ExecutionTree(ExecutionViewPoint(
				id=id, states=states, decisions=decisions, choices=choices, natures=natures,
				is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
				probability=probability, impacts=impacts,
				cei_top_down=probability * impacts, cei_bottom_up=cei_bottom_up,
				pending_choices=pending_choices, pending_natures=pending_natures,
				parent=solution_tree)),
			branches)


def create_execution_tree(region_tree: ParseTree, impacts_names:list, pending_choices:set, pending_natures:set) -> ExecutionTree:
	id = 0
	solution_tree, branches = evaluate_viewPoint(id, region_tree, (region_tree.root,), States(region_tree.root, ActivityState.WAITING, 0), pending_choices, pending_natures, None, len(impacts_names))

	for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
		id = create_execution_viewpoint(region_tree, decisions, branch_states, solution_tree, id + 1, pending_choices, pending_natures, impacts_names)

	return solution_tree


def create_execution_viewpoint(region_tree: ParseTree, decisions: tuple[ParseNode], states: States, solution_tree: ExecutionTree, id: int, pending_choices:set, pending_natures:set, impacts_names:list) -> int:
	new_solution_tree, branches = evaluate_viewPoint(id, region_tree, decisions, states, pending_choices, pending_natures, solution_tree, len(impacts_names))

	solution_tree.root.add_child(new_solution_tree)
	for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
		id = create_execution_viewpoint(region_tree, decisions, branch_states, new_solution_tree, id + 1, pending_choices, pending_natures, impacts_names)

	return id
