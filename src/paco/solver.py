import numpy as np
from src.paco.explainer.build_explained_strategy import build_explained_strategy
from src.paco.explainer.explanation_type import ExplanationType
from src.paco.parser.create import create
from src.paco.searcher.search import search
from src.utils import check_syntax as cs
from src.utils.env import IMPACTS_NAMES, DURATIONS
from datetime import datetime


def paco(bpmn:dict, bound:np.ndarray, parse_tree=None, pending_choices=None, pending_natures=None, execution_tree=None, search_only=False, type_strategy=ExplanationType.HYBRID, debug = False):
	result = {"bpmn": bpmn, "bound": bound}

	bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS]) # set max duration

	parse_tree, pending_choices, pending_natures, execution_tree, times = create(bpmn, parse_tree, pending_choices, pending_natures, execution_tree, debug)
	result.update({"parse_tree": parse_tree,
					"pending_choices": pending_choices,
					"pending_natures": pending_natures,
					"execution_tree": execution_tree})

	frontier_solution, expected_impacts, possible_min_solution, frontier_values, strategy, search_times = search(execution_tree, bound, bpmn[IMPACTS_NAMES], search_only, debug)

	result.update({"possible_min_solution": possible_min_solution,
				   "guaranteed_bounds": frontier_values})
	times.update(search_times)

	if frontier_solution is None:# Also expected_impacts is None
		#text_result = ""
		#for i in range(len(possible_min_solution)):
		#	text_result += f"Exp. Impacts {i}:\t{np.round(possible_min_solution[i], 2)}\n"

		#text_result = f"Failed:\t\t\t{bpmn[IMPACTS_NAMES]}\nPossible Bound Impacts:\t{bound}\n" + text_result
		#for i in range(len(frontier_values)):
		#	text_result += f"Guaranteed Bound {i}:\t{np.ceil(frontier_values[i])}\n"

		text_result = "Failed"
		# print(str(datetime.now()) + " " + text_result)
		return text_result, result, times

	result.update({"frontier_solution": frontier_solution,
				   "expected_impacts": expected_impacts})

	if strategy is None:
		text_result = f"Any choice taken will provide a winning strategy"# with an expected impact of: "
		#text_result += " ".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in expected_impacts]))
		# print(str(datetime.now()) + " " + text_result)
		return text_result, result, times


	strategy_tree, strategy_expected_impacts, strategy_expected_time, bdds, explainer_times = build_explained_strategy(parse_tree, strategy, type_strategy, bpmn[IMPACTS_NAMES], pending_choices, pending_natures, debug)
	times.update(explainer_times)

	#text_result = f"This is the strategy, with an expected impact of: "
	#text_result += " ".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in strategy_expected_impacts]))
	text_result = f"Found, watch the explainers to make decisions"
	# print(str(datetime.now()) + " " + text_result)

	result.update({"strategy_tree": strategy_tree,
				   "strategy_expected_impacts": strategy_expected_impacts,
				   "strategy_expected_time": strategy_expected_time,
				   "bdds": bdds})

	return text_result, result, times

