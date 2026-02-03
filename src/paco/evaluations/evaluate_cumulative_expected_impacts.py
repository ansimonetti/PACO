import copy
from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.parser.parse_node import Choice


def evaluate_cumulative_expected_impacts(solution_tree: ExecutionTree):
	root = solution_tree.root
	# root.cei_top_down = root.probability * root.impacts #Useless, already done in the constructor
	#Print the root
	#print("evaluate_cumulative_expected_impacts:id:", root.id, "cei_top_down:", root.cei_top_down)
	if root.is_final_state:# or root.is_leaf: #TODO Daniel: earlyStop
		root.cei_bottom_up = copy.deepcopy(root.cei_top_down)
		#print("evaluate_cumulative_expected_impacts:id:", root.id, "cei_bottom_up:", root.cei_bottom_up)
		return

	onlyChoice = True
	choices_cei_bottom_up = {}
	for Transition, subTree in root.transitions.items():
		evaluate_cumulative_expected_impacts(subTree)

		choices_transitions = []
		for t in Transition:
			if isinstance(t[0], Choice):
				onlyChoice = False
				choices_transitions.append(t)

		if onlyChoice:
			root.cei_bottom_up += subTree.root.cei_bottom_up
		else:
			choices_transitions = tuple(choices_transitions)
			if choices_transitions not in choices_cei_bottom_up:
				choices_cei_bottom_up[choices_transitions] = copy.deepcopy(subTree.root.cei_bottom_up)
			else:
				choices_cei_bottom_up[choices_transitions] += subTree.root.cei_bottom_up

	'''
	for Transition, subTree in root.transitions.items():
		print(subTree.root.cei_bottom_up)
	
	print("choices_cei_bottom_up:")
	for child, cei_bottom_up in choices_cei_bottom_up.items():
		message = ""
		for t in range(len(child)):
			message += str(child[t][0].id) + "->" + str(child[t][1].id) + ", "
		print(message[:-2] + " = " + str(cei_bottom_up))
	print("End")
	'''
	for c in choices_cei_bottom_up.keys():
		for i in range(len(root.impacts)):
			if root.cei_bottom_up[i] < choices_cei_bottom_up[c][i]:
				root.cei_bottom_up[i] = choices_cei_bottom_up[c][i]
