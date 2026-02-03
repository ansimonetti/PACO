import copy
from src.paco.parser.parse_node import ParseNode, Choice
from src.paco.execution_tree.execution_tree import ExecutionTree


def build_strategy(frontier: list[ExecutionTree], strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]] = {}) -> (set[ExecutionTree], dict[ParseNode, dict[ParseNode, set[ExecutionTree]]]):
	if len(frontier) == 0:
		return frontier, strategy

	#print("building_strategy:frontier: ", frontier_info(frontier))

	newFrontier = []
	newStrategy = copy.deepcopy(strategy)
	for execution_tree in frontier:
		execution_viewpoint = execution_tree.root
		if execution_viewpoint.parent is None: #Is the first choice/nature because parent is None
			continue

		#print(f"ID: {execution_viewpoint.id}")
		for decision in execution_viewpoint.decisions:
			#print(f"ID:{decision.id}, Parent id: {decision.parent.id}, type: {decision.parent.type}")
			if isinstance(decision.parent, Choice):
				choice = decision.parent
				if choice not in newStrategy:
					newStrategy[choice] = {decision: {execution_viewpoint.parent}}
				elif decision not in newStrategy[decision.parent]:
					newStrategy[choice][decision] = {execution_viewpoint.parent}
				else:
					newStrategy[choice][decision].add(execution_viewpoint.parent)

		newFrontier.append(execution_viewpoint.parent)

	return build_strategy(newFrontier, newStrategy)
