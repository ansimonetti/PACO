from datetime import datetime
import numpy as np
from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.searcher.found_strategy import found_strategy
from src.paco.searcher.build_strategy import build_strategy


def search(execution_tree: ExecutionTree, bound: np.ndarray, impacts_names: list, search_only: bool, debug=False):
    times = {}

    #print(f"{datetime.now()} FoundStrategy:")
    t = datetime.now()
    frontier_solution, expected_impacts, frontier_values, possible_min_solution = found_strategy([execution_tree], bound)
    t1 = datetime.now()
    found_strategy_time = (t1 - t).total_seconds()*1000
    #print(f"{t1} FoundStrategy:completed: {found_strategy_time} ms")
    times["found_strategy_time"] = found_strategy_time

    if frontier_solution is None:
        #TODO plot_pareto_frontier
        #print(f"Failed:\t\t{impacts_names}\nBound Impacts:\t{bound}")
        return None, None, possible_min_solution, frontier_values, [], times

    #print(f"Success:\t\t{impacts_names}\nBound Impacts:\t{bound}\nExp. Impacts:\t{expected_impacts}")
    if debug:
        execution_tree.save_dot(
            state=True, executed_time=True, diff=False,
            frontier = {tree.root.id for tree in frontier_solution})

    if search_only:
        return frontier_solution, expected_impacts, possible_min_solution, frontier_values, None, times

    #print(f'{datetime.now()} BuildStrategy:')
    t = datetime.now()
    _, strategy = build_strategy(frontier_solution)
    t1 = datetime.now()
    build_strategy_time = (t1 - t).total_seconds()*1000
    #print(f"{t1} Build Strategy:completed: {build_strategy_time} ms")
    times["build_strategy_time"] = build_strategy_time

    return frontier_solution, expected_impacts, possible_min_solution, frontier_values, None if len(strategy) == 0 else strategy, times
