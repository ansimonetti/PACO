from datetime import datetime

from src.paco.evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.parser.bpmn_parser import create_parse_tree
from src.paco.parser.parse_tree import ParseTree
from src.paco.searcher.create_execution_tree import create_execution_tree
from src.utils.env import IMPACTS_NAMES, PATH_EXECUTION_TREE


def create(bpmn:dict, parse_tree:ParseTree=None, pending_choices:set=None, pending_natures:set=None, execution_tree:ExecutionTree=None, debug=False):
	times = {}

	#print(f"{datetime.now()} CreateParseTree:")
	if parse_tree is None or pending_choices is None:
		t = datetime.now()
		parse_tree, pending_choices, pending_natures, pending_loops = create_parse_tree(bpmn)
		t1 = datetime.now()
		time_create_parse_tree = (t1 - t).total_seconds()*1000
		#print(f"{t1} CreateParseTree:completed: {time_create_parse_tree} ms")
		if debug:
			parse_tree.save_dot()

	else: #Cache
		#parse_tree, pending_choices, pending_natures = ParseTree.from_json()
		time_create_parse_tree = 0
		#print(f"{datetime.now()} CreateParseTree:completed: cache")

	#times["time_create_parse_tree"] = time_create_parse_tree

	#print(f"{datetime.now()} CreateExecutionTree:")
	if execution_tree is None or pending_choices is None:
		t = datetime.now()
		execution_tree = create_execution_tree(parse_tree, bpmn[IMPACTS_NAMES], pending_choices, pending_natures)
		t1 = datetime.now()
		time_create_execution_tree = (t1 - t).total_seconds()*1000
		#print(f"{t1} CreateExecutionTree:completed: {time_create_execution_tree} ms")
		t = datetime.now()
		evaluate_cumulative_expected_impacts(execution_tree)
		t1 = datetime.now()
		time_evaluate_cei_execution_tree = (t1 - t).total_seconds()*1000
		#print(f"{t1} CreateExecutionTree:CEI evaluated: {time_evaluate_cei_execution_tree} ms")
		if debug:
			execution_tree.save_dot(state=True, executed_time=True, diff=False)

	else: #Cache
		#execution_tree = ExecutionTree.from_json(parse_tree, bpmn[IMPACTS_NAMES])
		time_create_execution_tree = 0
		time_evaluate_cei_execution_tree = 0
		#print(f"{datetime.now()} CreateExecutionTree:completed: cache")
		#print(f"{datetime.now()} CreateExecutionTree:CEI evaluated: cache")

	times["time_create_execution_tree"] = time_create_execution_tree
	times["time_evaluate_cei_execution_tree"] = time_evaluate_cei_execution_tree

	return parse_tree, pending_choices, pending_natures, execution_tree, times

