import enum
import random
import numpy as np
from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.evaluations.pareto import get_min_dominated_impacts, get_max_dominating_vectors
from src.paco.parser.parse_node import Choice, Nature

'''
def compare_bound(cei: np.ndarray, bound: np.ndarray):
	print(cei, bound, [-1 if v1 < v2 else 0 if v1 == v2 else 1 for v1, v2 in zip(cei, bound)])
	return [-1 if v1 < v2 else 0 if v1 == v2 else 1 for v1, v2 in zip(cei, bound)]
'''

def compare_bound(cei: np.ndarray, bound: np.ndarray):
	#print("CEI: ", cei, " bound: ", bound, "res: ", np.where(cei <= bound, 0, 1))
	#print("type cei:", cei.dtype, "type bound:", bound.dtype)
	#return np.where(cei <= bound, 0, 1)
	return np.where(cei <= bound + np.finfo(np.float64).eps*10, 0, 1) #TODO fix eps value
	#TODO use numpy.allclose(a, b, rtol=1e-05, atol=1e-08, equal_nan=False)[source]


class TypeSearch(enum.IntEnum):
	UNIFORM_PROBABILITY = 0
	WEIGHTED_PROBABILITY = 1

	def __str__(self):
		return str(self.name)

def pick(frontier: list[ExecutionTree], typeSearch: TypeSearch) -> ExecutionTree:
	if typeSearch == TypeSearch.WEIGHTED_PROBABILITY:
		return random.choices(frontier, weights=[tree.root.probability for tree in frontier], k=1)[0]

	return frontier[random.randint(0, len(frontier) - 1)]



def natural_closure(tree: ExecutionTree, selected_tree: ExecutionTree) -> list[ExecutionTree]:
	frontier = []
	#print("nat_nodes: ", tree.root.natures, "chose_id: ", [node.id for node in chose_id])

	for transition, next_child in tree.root.transitions.items():
		check_nat = len(tree.root.natures) == 0
		check_choice = len(selected_tree.root.decisions) != 0
		for t in transition:
			#print("t: ", t[0].type, t[0].id, t[1].id)
			if isinstance(t[0], Nature):# and t[0] in nats:
				check_nat = True
			elif isinstance(t[0], Choice) and t[1] not in selected_tree.root.decisions:
				check_choice = False

			if check_nat and not check_choice:
				break

		if check_nat and check_choice:
			frontier.append(next_child)

	return frontier


def frontier_info(frontier: list[ExecutionTree]) -> str:
	result = ""
	for tree in frontier:
		decisions = ""
		for decision in tree.root.decisions:
			decisions += str(decision.id) + ", "

		choices = ""
		for choice in tree.root.choices:
			choices += str(choice.id) + ", "
		natures = ""
		for nature in tree.root.natures:
			natures += str(nature.id) + ", "

		result += f"ID:{tree.root.id}:<<{decisions[:-2]}>,<{choices[:-2]}; {natures[:-2]}>>, "

	return "[" + result[:-2] + "]"


def found_strategy(frontier: list[ExecutionTree], bound: np.ndarray, typeSearch: TypeSearch = TypeSearch.WEIGHTED_PROBABILITY) -> (list[ExecutionTree], np.ndarray, list[np.ndarray], list[np.ndarray]):
	#print("frontier: ", frontier_info(frontier))
	# Return:
	# 1. frontier_solution: list of ExecutionTree or None if no solution found
	# 2. expected_solution_value: list of np.ndarray or None, minimum solution value
	# 3. frontier_solution_bottom_up: list of np.ndarray, solutions value
	# 4. frontier_solution_top_down: list of np.ndarray, possible minimum solutions value

	frontier_bottom_up:np.ndarray = np.sum([tree.root.cei_bottom_up for tree in frontier], axis=0)
	frontier_top_down:np.ndarray = np.sum([tree.root.cei_top_down for tree in frontier], axis=0)

	if np.all(compare_bound(frontier_bottom_up, bound) <= 0):
		return frontier, frontier_bottom_up, [frontier_bottom_up + frontier_top_down], []

	if np.all(compare_bound(frontier_top_down, bound) > 0) or all(tree.root.is_leaf for tree in frontier):
		#print("Failed top_down: not a valid choose")
		return None, None, [frontier_bottom_up], [frontier_top_down]

	tree = pick([tree for tree in frontier if not tree.root.is_leaf], typeSearch)

	tested_frontier_solution = []
	frontier_solution_bottom_up = []
	frontier_solution_top_down = []
	while len(tested_frontier_solution) < len(tree.root.transitions.values()):
		to_pick_frontier = [subTree for subTree in tree.root.transitions.values() if subTree not in tested_frontier_solution]
		#print("to_pick_frontier: ", frontier_info(to_pick_frontier))

		chose = pick(to_pick_frontier, typeSearch)
		chose_frontier = natural_closure(tree, chose)
		#print("frontier_nat: ", frontier_info(chose_frontier))

		new_frontier = frontier.copy()
		new_frontier.remove(tree)
		new_frontier.extend(chose_frontier)
		#print("new_frontier: ", frontier_info(new_frontier))
		frontier_solution, new_frontier_solution, new_frontier_solution_bottom_up, new_frontier_solution_top_down = found_strategy(new_frontier, bound, typeSearch)
		#print("end_rec")
		if frontier_solution is None:
			tested_frontier_solution.extend(chose_frontier)
			frontier_solution_bottom_up.extend(new_frontier_solution_bottom_up)
			#frontier_solution_bottom_up = get_max_dominating_vectors(frontier_solution_bottom_up)
			frontier_solution_top_down.extend(new_frontier_solution_top_down)
			#frontier_solution_top_down = get_min_dominated_impacts(frontier_solution_top_down)
		else:
			return frontier_solution, new_frontier_solution, new_frontier_solution_bottom_up, new_frontier_solution_top_down

	#print("tested_frontier_solution", frontier_info(tested_frontier_solution))
	#print("Failed: No choose left")
	return None, None, frontier_solution_bottom_up, frontier_solution_top_down
