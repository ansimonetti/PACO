from src.paco.evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from src.paco.explainer.explain_strategy import explain_strategy
from src.paco.explainer.full_strategy import full_strategy
from src.paco.searcher.build_strategy import build_strategy
from src.paco.searcher.create_execution_tree import create_execution_tree
from src.paco.searcher.found_strategy import found_strategy
import numpy as np
from datetime import datetime
from src.utils.env import IMPACTS_NAMES


def refine_bounds(bpmn, parse_tree, pending_choices, pending_natures, initial_bounds, num_refinements = 10):
	t = datetime.now()
	execution_tree = create_execution_tree(parse_tree, bpmn[IMPACTS_NAMES], pending_choices, pending_natures)
	metadata = {"time_create_execution_tree" : (datetime.now() - t).total_seconds()*1000}
	print(f"{datetime.now()} CreateExecutionTree: {metadata["time_create_execution_tree"]} ms")
	t = datetime.now()
	evaluate_cumulative_expected_impacts(execution_tree)
	metadata["time_evaluate_cei_execution_tree"] = (datetime.now() - t).total_seconds()*1000
	print(f"{datetime.now()} CreateExecutionTree:CEI: {metadata["time_evaluate_cei_execution_tree"]} ms")

	cumulative_found_strategy_time = 0

	intervals = [ [0.0, bound_value] for bound_value in initial_bounds ]
	bounds = []
	for i in range(len(intervals)):
		bounds.append(intervals[i][1])

	for iteration in range(num_refinements):
		for current_impact in range(len(intervals)):
			test_bounds = []
			for i in range(len(intervals)):
				test_bounds.append(intervals[i][1])

			test_bounds[current_impact] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
			t = datetime.now()
			frontier_solution, expected_impacts, frontier_values, possible_min_solution = found_strategy([execution_tree], np.array(test_bounds))
			found_strategy_time = (datetime.now() - t).total_seconds()*1000
			cumulative_found_strategy_time += found_strategy_time

			if frontier_solution is not None:# Success Condition
				intervals[current_impact][1] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
				bounds = test_bounds
				s = "Success"
			else:
				intervals[current_impact][0] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
				s = "Fail"

			print(f"{datetime.now()} FoundStrategy:iteration:{iteration}: {found_strategy_time} ms " + s)


	t = datetime.now()
	final_frontier_solution, expected_impacts, frontier_values, possible_min_solution = found_strategy([execution_tree], np.array(bounds))
	found_strategy_time = (datetime.now() - t).total_seconds()*1000
	cumulative_found_strategy_time += found_strategy_time
	print(f"{datetime.now()} FoundStrategy: {found_strategy_time} ms")
	metadata["found_strategy_time"] = cumulative_found_strategy_time

	if final_frontier_solution is None:
		raise Exception("No solution found, bounds: " + str(bounds))

	t = datetime.now()
	_, strategy = build_strategy(final_frontier_solution)
	metadata["build_strategy_time"] = (datetime.now() - t).total_seconds()*1000
	print(f"{datetime.now()} Build Strategy: {metadata["build_strategy_time"]} ms")

	if strategy is not None:
		t = datetime.now()
		worst_type_strategy, bdds = explain_strategy(parse_tree, strategy, bpmn[IMPACTS_NAMES])
		metadata["time_explain_strategy"] = (datetime.now() - t).total_seconds()*1000
		print(f"{datetime.now()} Explain Strategy: {metadata["time_explain_strategy"]} ms")

		t = datetime.now()
		strategy_tree, children, expected_impacts, expected_time, pending_choices, pending_natures, _ = full_strategy(parse_tree, bdds, len(bpmn[IMPACTS_NAMES]), pending_choices, pending_natures)
		metadata["strategy_tree_time"] = (datetime.now() - t).total_seconds()*1000
		print(f"{datetime.now()} StrategyTree: {metadata["strategy_tree_time"]} ms\n")
	else:
		print(f"{datetime.now()} No needed: ")

	metadata["initial_bounds"] = initial_bounds
	metadata["final_bounds"] = bounds

	return metadata

