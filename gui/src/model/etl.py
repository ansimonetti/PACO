import ast
import base64
import json
from copy import deepcopy

import graphviz
import requests
from requests.exceptions import RequestException

from gui.src.env import (
	URL_SERVER,
	HEADERS,
	SESE_PARSER,
	EXPRESSION,
	IMPACTS_NAMES,
	IMPACTS,
	DURATIONS,
	DELAYS,
	PROBABILITIES,
	LOOP_PROBABILITY,
	LOOP_ROUND,
	extract_nodes,
	BOUND,
	SIMULATOR_SERVER,
	H,
)
from gui.src.model.execution_tree import (
	get_execution_node,
	get_current_marking_from_execution_tree,
	get_execution_probability,
	get_execution_time,
	get_execution_impacts,
)
from gui.src.model.petri_net import (
	get_pending_decisions,
	is_final_marking,
	is_initial_marking,
)
from gui.src.model.sqlite import (
	fetch_bpmn,
	save_execution_tree,
	save_parse_tree,
	fetch_strategy,
	save_strategy,
	save_petri_net,
	save_bpmn_dot,
	update_bpmn_dot as _update_bpmn_record,
)
from gui.src.model.bpmn import get_active_region_by_pn, ActivityState


def load_bpmn_dot(bpmn: dict, *, force_refresh: bool = False) -> str:
	"""
	Given a BPMN process, return its DOT representation as an SVG base64 string.
	If the DOT representation is already stored in the database, retrieve it from there.
	Otherwise, generate it, store it in the database, and return it.

	:param bpmn: BPMN dictionary
	:param force_refresh: If True, re-generate the DOT even if cached
	:return: SVG base64 string of the BPMN DOT representation
	"""
	if bpmn[EXPRESSION] == '':
		return None

	normalized_bpmn = _normalize_bpmn(bpmn)

	record = fetch_bpmn(normalized_bpmn)
	if not force_refresh and record and record.bpmn_dot:
		return record.bpmn_dot

	bpmn_dot = bpmn_snapshot_to_dot(bpmn)
	bpmn_svg_base64 = dot_to_base64svg(bpmn_dot)

	if record:
		_update_bpmn_record(normalized_bpmn, bpmn_svg_base64)
	else:
		save_bpmn_dot(normalized_bpmn, bpmn_svg_base64)

	return bpmn_svg_base64


def load_petri_net_svg(bpmn: dict, *, force_refresh: bool = False) -> str:
	"""
	Given a BPMN process, return its Petri Net DOT representation as an SVG base64 string.

	:param bpmn: BPMN dictionary
	:param force_refresh: If True, re-generate the Petri net even if cached
	:return: SVG base64 string of the Petri Net DOT representation
	"""
	if bpmn[EXPRESSION] == '':
		return None

	normalized_bpmn = _normalize_bpmn(bpmn)
	petri_net, petri_net_dot, spin_svg = get_petri_net(normalized_bpmn, 0, force_refresh=force_refresh)
	
	if spin_svg:
		return f"data:image/svg+xml;base64,{base64.b64encode(spin_svg.encode('utf-8')).decode('utf-8')}"

	if not petri_net_dot:
		return None

	return dot_to_base64svg(petri_net_dot)


def reset_simulation_state(bpmn: dict, bound_store: dict | None = None) -> tuple[str | None, str | None, dict]:
	"""
	Force-refresh execution tree and Petri net, then return updated SVGs and simulation data.
	"""
	if bpmn[EXPRESSION] == '':
		return None, None, {"expression": ""}

	load_execution_tree(bpmn, force_refresh=True)
	bpmn_svg = load_bpmn_dot(bpmn, force_refresh=True)
	petri_svg = load_petri_net_svg(bpmn, force_refresh=True)

	sim_data = get_simulation_data(bpmn, bound_store)
	sim_data["expression"] = bpmn.get(EXPRESSION, "")

	return bpmn_svg, petri_svg, sim_data


def dot_to_base64svg(dot: str) -> str:
	"""
	Convert a DOT string to an SVG base64 string.

	:param dot: DOT string
	:return: SVG base64 string
	"""
	svg = graphviz.Source(dot).pipe(format='svg')
	svg_base64 = f"data:image/svg+xml;base64,{base64.b64encode(svg).decode('utf-8')}"
	return svg_base64


def get_activity_status(root, status:dict) -> dict[str, ActivityState]:
	node_id = str(root['id'])

	if root['type'] == 'task':
		if node_id in status.keys():
			return {root['label']: ActivityState(status[node_id])}, {root['id']: ActivityState(status[node_id])}
		return {root['label']: ActivityState.WAITING}, {root['id']: ActivityState.WAITING}

	result_with_ids, result_with_names  = {}, {}

	if root['type'] == 'choice' or root['type'] == 'nature':
		node_name = root['label']
	else:
		node_name = f"{root['type'].capitalize()}_{node_id}"

	if node_id in status:
		result_with_ids[node_id] = ActivityState(status[node_id])
		result_with_names[node_name] = ActivityState(status[node_id])
	else:
		result_with_ids[node_id] = ActivityState.WAITING
		result_with_names[node_name] = ActivityState.WAITING

	for child in root['children']:
		sub_status_with_names, sub_status_with_ids = get_activity_status(child, status)
		result_with_ids.update(sub_status_with_ids)
		result_with_names.update(sub_status_with_names)

	return result_with_names, result_with_ids

def get_status(bpmn, status:dict):
	parse_tree = load_parse_tree(bpmn)

	is_initial = True
	is_final = False
	if parse_tree['id'] in status.keys() and status[parse_tree['id']] > ActivityState.WAITING:
		is_initial = False
		if status[parse_tree['id']] > ActivityState.ACTIVE:
			is_final = True

	status_with_names, status_with_ids = get_activity_status(parse_tree, status)
	return is_initial, is_final, status_with_names, status_with_ids


def bpmn_snapshot_to_dot(bpmn) -> str:
	"""
	Given a BPMN process, return its DOT representation.

	:param bpmn: BPMN dictionary
	:return: BPMN DOT string
	"""
	petri_net, _, _ = get_petri_net(bpmn, step=0)

	execution_tree, current_execution_node = load_execution_tree(bpmn)

	current_node = get_execution_node(execution_tree, current_execution_node)

	return bpmn_to_dot(bpmn, current_node['snapshot']['status'])


def _get_bpmn_dot_local(bpmn: dict, status_with_ids: dict) -> str:
	from src.paco.parser.dot.bpmn import get_bpmn_dot_from_parse_tree
	from src.paco.parser.parse_tree import ParseTree

	parse_tree_dict = load_parse_tree(bpmn)
	parse_tree, _, _ = ParseTree.from_json(
		parse_tree_dict,
		impact_size=len(bpmn[IMPACTS_NAMES]),
		non_cumulative_impact_size=0,
	)
	return get_bpmn_dot_from_parse_tree(parse_tree, bpmn[IMPACTS_NAMES], status_with_ids)


def bpmn_to_dot(bpmn, status = {}) -> str:
	'''
	current_marking = current_node['snapshot']['marking']
	is_initial = is_initial_marking(current_marking, petri_net)
	is_final = is_final_marking(current_marking, petri_net)
	active_regions = {}
	if not is_initial:
		active_regions = get_active_region_by_pn(petri_net, current_marking)
	'''
	is_initial, is_final, status_with_names, status_with_ids = get_status(bpmn, status)

	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn[EXPRESSION]))
	bpmn = filter_bpmn(bpmn, tasks, choices, natures, loops)

	# for task, status in status_with_names.items():
	# 	print(task, status)

	try:
		resp = requests.get(
			URL_SERVER + "create_bpmn",
			json={
				"bpmn": bpmn,
				"status": status_with_ids,
			},
			headers=HEADERS,
		)
		resp.raise_for_status()
		bpmn_dot_str = resp.json()["bpmn_dot"]
	except RequestException:
		bpmn_dot_str = _get_bpmn_dot_local(bpmn, status_with_ids)

	return bpmn_dot_str


def update_bpmn_dot(bpmn: dict, bpmn_dot: str):
	"""
	Update the BPMN DOT representation in the database for the given BPMN process.

	:param bpmn: BPMN dictionary
	:param bpmn_dot: BPMN DOT string
	:return: None
	"""
	if bpmn[EXPRESSION] != '':
		normalized_bpmn = _normalize_bpmn(bpmn)
		_update_bpmn_record(normalized_bpmn, bpmn_dot)


def _normalize_bpmn(bpmn_store: dict) -> dict:
	"""Return a normalized copy of the BPMN data used for caching purposes."""
	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
	return filter_bpmn(bpmn_store, tasks, choices, natures, loops)


def _create_parse_tree_local(bpmn: dict) -> dict:
	from src.utils.check_syntax import check_bpmn_syntax, set_max_duration
	from src.paco.parser.bpmn_parser import create_parse_tree

	bpmn_copy = deepcopy(bpmn)
	check_bpmn_syntax(bpmn_copy)
	bpmn_copy[DURATIONS] = set_max_duration(bpmn_copy[DURATIONS])
	parse_tree, _, _, _ = create_parse_tree(bpmn_copy)
	return parse_tree.to_dict()


def load_parse_tree(bpmn: dict, *, force_refresh: bool = False) -> dict:
	"""
	Given a BPMN process, return its parse tree.
	If the parse tree is already stored in the database, retrieve it from there.
	Otherwise, request it from the server and store it in the database.

	:param bpmn: BPMN dictionary
	:return: Parse tree dictionary
	"""
	if bpmn[EXPRESSION] == '':
		return None

	normalized_bpmn = _normalize_bpmn(bpmn)

	record = fetch_bpmn(normalized_bpmn)
	if not force_refresh and record and record.parse_tree:
		return json.loads(record.parse_tree)
	# print("load_parse_tree:bpmn", bpmn)

	try:
		resp = requests.get(URL_SERVER + "create_parse_tree", json={"bpmn": normalized_bpmn}, headers=HEADERS)
		resp.raise_for_status()
	except RequestException as exc:
		print(f"ERROR: load_parse_tree fallback to local parser: {exc}")
		parse_tree = _create_parse_tree_local(normalized_bpmn)
		save_parse_tree(normalized_bpmn, json.dumps(parse_tree))
		return parse_tree

	resp_json = resp.json()
	if 'error' in resp_json:
		raise ValueError(f"Error from server: {resp_json['error']}")

	parse_tree = resp_json["parse_tree"]

	save_parse_tree(normalized_bpmn, json.dumps(parse_tree))

	return parse_tree


def load_execution_tree(bpmn: dict, *, force_refresh: bool = False) -> tuple[dict, str]:
	"""
	Given a BPMN process, return its execution tree and the current execution node.
	If the execution tree is already stored in the database, retrieve it from there.
	Otherwise, request it from the simulator server and store it in the database.

	:param bpmn: BPMN dictionary
	:return: Tuple of execution tree dictionary and current execution node ID
	"""
	if bpmn[EXPRESSION] == '':
		return {}, None

	normalized_bpmn = _normalize_bpmn(bpmn)

	record = fetch_bpmn(normalized_bpmn)
	if (not force_refresh and record and record.execution_tree and record.actual_execution):
		return json.loads(record.execution_tree), record.actual_execution

	# print("load_execution_tree:", bpmn)
	parse_tree = load_parse_tree(bpmn, force_refresh=force_refresh)

	try:
		resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
		resp.raise_for_status()
	except requests.exceptions.HTTPError as exc:
		if exc.response is None or exc.response.status_code != 422:
			raise


		parse_tree = load_parse_tree(bpmn, force_refresh=True)
		resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
		resp.raise_for_status()
	resp_json = resp.json()

	if 'error' in resp_json:
		raise ValueError(f"Simulator error: {resp_json['error']}")

	execution_tree = resp_json.get('execution_tree', None)
	if execution_tree is None:
		raise ValueError("Simulator error: No execution tree returned")

	execution_tree_root = execution_tree.get('root', None)
	current_execution_node = execution_tree.get('current_node', None)

	if execution_tree_root is None or current_execution_node is None:
		raise ValueError("Simulator error: Incomplete execution tree data")

	save_execution_tree(normalized_bpmn, json.dumps(execution_tree_root), current_execution_node)

	return execution_tree_root, current_execution_node


def get_petri_net(bpmn: dict, step: int, *, force_refresh: bool = False) -> tuple[dict, str, str|None]:
	"""
	Given a BPMN process, return its Petri net representation and its DOT format.
	If the Petri net is already stored in the database, retrieve it from there.
	Otherwise, request it from the simulator server and store it in the database.

	:param bpmn: BPMN dictionary
	:param step: Step number (currently unused)
	:return: Tuple of Petri net dictionary, DOT string, and Spin SVG string (optional)
	"""
	if bpmn[EXPRESSION] == '':
		return None, None, None
	normalized_bpmn = _normalize_bpmn(bpmn)

	record = fetch_bpmn(normalized_bpmn)
	if not force_refresh and record and record.petri_net and record.petri_net_dot:
		return json.loads(record.petri_net), record.petri_net_dot, record.spin_svg

	parse_tree = load_parse_tree(bpmn, force_refresh=force_refresh)

	try:
		resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
		resp.raise_for_status()
	except requests.exceptions.HTTPError as exc:
		if exc.response is None or exc.response.status_code != 422:
			raise

		parse_tree = load_parse_tree(bpmn, force_refresh=True)
		resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
		resp.raise_for_status()
	resp_json = resp.json()

	if 'error' in resp_json:
		raise ValueError(f"Simulator error: {resp_json['error']}")

	petri_net = resp_json.get('petri_net', None)
	petri_net_dot = resp_json.get('petri_net_dot', None)
	spin_svg = resp_json.get('spin_svg', None)

	if petri_net is None or petri_net_dot is None:
		raise ValueError("Simulator error: Incomplete Petri net data")

	save_petri_net(normalized_bpmn, json.dumps(petri_net, sort_keys=True), petri_net_dot, spin_svg=spin_svg)

	return petri_net, petri_net_dot, spin_svg


def load_strategy(bpmn_store, bound_store):
	if bpmn_store[EXPRESSION] == '':
		raise ValueError("The expression is empty")
	if BOUND not in bound_store or not bound_store[BOUND]:
		raise ValueError("Bound is empty")

	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
	bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

	bound = [float(bound_store[BOUND][impact_name]) for impact_name in bpmn[IMPACTS_NAMES]]  # Already sorted

	record = fetch_strategy(bpmn, bound)
	# if record and record.bdds:
	#   return record.bdds

	# print("load_strategy:", bpmn)
	parse_tree = load_parse_tree(bpmn)
	# print(parse_tree)
	#execution_tree = load_execution_tree(bpmn)
	resp = requests.get(f'{URL_SERVER}create_execution_tree',
						json={"bpmn": bpmn},  headers=HEADERS)

	resp.raise_for_status()
	response = resp.json()

	resp = requests.get(URL_SERVER + "create_strategy",
						json={"bpmn": bpmn, "bound": bound,
							  "parse_tree": parse_tree, "execution_tree": response["execution_tree"]},
						headers=HEADERS)

	resp.raise_for_status()
	response = resp.json()

	expected_impacts = []
	if "expected_impacts" in response:  # Solution found
		expected_impacts = [float(x) for x in response["expected_impacts"].strip('[]').split()]

	guaranteed_bounds = [
		[float(x) for x in s.strip('[]').split()]
		for s in ast.literal_eval(response['guaranteed_bounds'])
	]

	possible_min_solution = [
		[float(x) for x in s.strip('[]').split()]
		for s in ast.literal_eval(response['possible_min_solution'])
	]

	bdds = {}
	if "bdds_dot" in response:  # Solution Explained
		for choice, v in response["bdds_dot"].items():
			type_strategy, bdd_dot = v
			bdds[choice] = (
				type_strategy,
				f"data:image/svg+xml;base64,{base64.b64encode(graphviz.Source(bdd_dot).pipe(format='svg')).decode('utf-8')}"
			)

	save_strategy(bpmn, bound, response["result"],
				  str(expected_impacts), response['guaranteed_bounds'],
				  response['possible_min_solution'], bdds)

	return response["result"], expected_impacts, guaranteed_bounds, possible_min_solution, bdds


def filter_bpmn(bpmn_store, tasks, choices, natures, loops):
	# Filter the data to keep only the relevant tasks, choices, natures, and loops
	bpmn = deepcopy(bpmn_store)
	impact_values = list(bpmn[IMPACTS].values())
	if impact_values and isinstance(impact_values[0], dict):
		bpmn[IMPACTS_NAMES] = sorted(bpmn_store[IMPACTS_NAMES])
		bpmn[IMPACTS] = {
			task: [float(bpmn_store[IMPACTS][task][impact_name]) for impact_name in bpmn[IMPACTS_NAMES]]
			for task in tasks if task in bpmn_store[IMPACTS]
		}
	bpmn[DURATIONS] = {task: bpmn_store[DURATIONS][task] for task in tasks if task in bpmn_store[DURATIONS]}
	bpmn[DELAYS] = {choice: bpmn_store[DELAYS][choice] for choice in choices if choice in bpmn_store[DELAYS]}
	bpmn[PROBABILITIES] = {nature: bpmn_store[PROBABILITIES][nature] for nature in natures if
						   nature in bpmn_store[PROBABILITIES]}
	bpmn[LOOP_PROBABILITY] = {loop: bpmn_store[LOOP_PROBABILITY][loop] for loop in loops if
							  loop in bpmn_store[LOOP_PROBABILITY]}
	bpmn[LOOP_ROUND] = {loop: bpmn_store[LOOP_ROUND][loop] for loop in loops if loop in bpmn_store[LOOP_ROUND]}

	return bpmn


def set_actual_execution(bpmn: dict, actual_execution: str):
	"""
	Set the actual execution node in the database for the given BPMN process.

	:param bpmn: BPMN dictionary
	:param actual_execution: Current execution node ID
	:return: None
	"""
	if bpmn[EXPRESSION] == '':
		return
	normalized_bpmn = _normalize_bpmn(bpmn)

	record = fetch_bpmn(normalized_bpmn)
	if not record or not record.execution_tree:
		return

	save_execution_tree(normalized_bpmn, record.execution_tree, actual_execution)


def get_current_state(bpmn):
	"""
	Given a BPMN process, return the current marking from its execution tree.

	:param bpmn: BPMN dictionary
	:return: Current marking dictionary
	"""
	execution_tree, current_execution = load_execution_tree(bpmn)
	return get_current_marking_from_execution_tree(execution_tree, current_execution)


def get_simulation_data(bpmn, bound_store=None):
	"""
	Get the simulation data for the given BPMN process.
	This includes pending gateway decisions, impacts, expected impacts, probability, and execution time.

	:param bpmn: BPMN dictionary
	:param bound_store: Bound dictionary (optional, to fetch strategy)
	:return: Simulation data dictionary
	"""
	if bpmn[EXPRESSION] == '':
		raise ValueError("BPMN expression is empty")

	petri_net, _, _ = get_petri_net(bpmn, 0)
	current_state = get_current_state(bpmn)
	pending_decisions = get_pending_decisions(petri_net, current_state)

	# Fetch strategy explainers if bound_store is provided
	if bound_store and pending_decisions:
		bdds = _fetch_strategy_data(bpmn, bound_store)
		if bdds:
			for gateway in pending_decisions:
				if gateway in bdds:
					# Inject explainer into the decision dict
					# bdds[gateway] is (type, svg_base64)
					pending_decisions[gateway]["__explainer__"] = bdds[gateway][1]

	execution_tree, current_execution = load_execution_tree(bpmn)
	probability = get_execution_probability(execution_tree, current_execution)

	execution_time = get_execution_time(execution_tree, current_execution)

	raw_impacts = get_execution_impacts(execution_tree, current_execution)

	impacts = {name: round(value, 2) for name, value in zip(bpmn[IMPACTS_NAMES], raw_impacts)}
	expected_impacts = {name: round(value * probability, 2) for name, value in zip(bpmn[IMPACTS_NAMES], raw_impacts)}

	task_statuses = get_task_statuses(bpmn)

	return {
		"gateway_decisions": pending_decisions,
		"impacts": impacts,
		"expected_impacts": expected_impacts,
		"probability": probability,
		"execution_time": execution_time,
		"task_statuses": task_statuses
	}


def get_formatted_label(node: dict) -> str:
	label = node.get('label')
	if label:
		return label

	children = node.get('children', [])
	if children:
		children_labels = [get_formatted_label(child) for child in children]
		node_type = node.get('type', '').lower()
		if node_type == 'sequential':
			return f"({', '.join(children_labels)})"
		elif node_type == 'parallel':
			return f"({' || '.join(children_labels)})"

	return "None"

def get_task_statuses(bpmn: dict) -> dict[str, str]:
	"""Get status of all tasks (not gateways) from the simulation snapshot."""
	execution_tree, current_execution_node = load_execution_tree(bpmn)
	node = get_execution_node(execution_tree, current_execution_node)
	status = node['snapshot']['status']  # dict[str_id, int_status]

	parse_tree = load_parse_tree(bpmn)
	
	task_statuses = {}
	
	# Map ActivityState enum to human-readable names
	status_names = {
		ActivityState.WAITING: "Waiting",
		ActivityState.ACTIVE: "Active", 
		ActivityState.COMPLETED: "Completed",
		ActivityState.COMPLETED_WITHOUT_PASSING_OVER: "Completed",
		ActivityState.WILL_NOT_BE_EXECUTED: "Skipped"
	}
	
	def traverse(root):
		node_id = str(root['id'])
		node_type = root.get('type', '').lower()
		
		# Only include tasks (not gateways/sequential/parallel)
		if node_type == 'task':
			label = root.get('label', f"Task_{node_id}")
			if node_id in status:
				state = status[node_id]
				task_statuses[label] = status_names.get(state, str(state))
			else:
				task_statuses[label] = "Waiting"
				
		children = root.get('children', [])
		for child in children:
			traverse(child)

	if parse_tree:
		traverse(parse_tree)
		
	return task_statuses


def execute_decisions(bpmn, gateway_decisions: list[str], time_step: float | None = None, bound_store=None):
	"""
	Execute the given gateway decisions on the BPMN process.
	Update the Petri net and execution tree in the database.
	Return the updated simulation data.

	:param bpmn: BPMN dictionary
	:param gateway_decisions: List of gateway decision IDs
	:param time_step: Time step for TimeStrategy
	:param bound_store: Bound dictionary (optional)
	:return: Updated simulation data dictionary or None if error occurs
	"""
	if bpmn[EXPRESSION] == '':
		raise ValueError("BPMN expression is empty")

	normalized_bpmn = _normalize_bpmn(bpmn)

	decisions = list(gateway_decisions)

	# print("execute_decisions:", bpmn, gateway_decisions, time_step)
	parse_tree = load_parse_tree(bpmn)
	petri_net, petri_net_dot, _ = get_petri_net(bpmn, None)
	execution_tree, current_execution = load_execution_tree(bpmn)

	request = {
		"bpmn": parse_tree,
		"petri_net": petri_net,
		"petri_net_dot": petri_net_dot,
		"execution_tree": {"root": execution_tree, "current_node": current_execution},
		"choices": decisions,
		"time_step": time_step,
	}

	try:
		response = requests.post(SIMULATOR_SERVER + "execute", json=request, headers=HEADERS)
		response.raise_for_status()
	except requests.exceptions.HTTPError as exc:
		if exc.response is None or exc.response.status_code != 422:
			raise

		parse_tree = load_parse_tree(bpmn, force_refresh=True)
		petri_net, petri_net_dot, _ = get_petri_net(bpmn, None, force_refresh=True)
		execution_tree, current_execution = load_execution_tree(bpmn, force_refresh=True)

		request = {
			"bpmn": parse_tree,
			"petri_net": petri_net,
			"petri_net_dot": petri_net_dot,
			"execution_tree": {"root": execution_tree, "current_node": current_execution},
			"choices": decisions,
			"time_step": time_step,
		}

		response = requests.post(SIMULATOR_SERVER + "execute", json=request, headers=HEADERS)
		response.raise_for_status()

	resp_json = response.json()

	if 'error' in resp_json:
		raise ValueError(f"Simulator error: {resp_json['error']}")
	
	# Check for error response format (type, message, traceback)
	if 'type' in resp_json and resp_json.get('type') == 'error':
		error_msg = resp_json.get('message', 'Unknown error')
		tb = resp_json.get('traceback', [])
		if tb:
			tb_str = '\n'.join(tb) if isinstance(tb, list) else str(tb)
			raise ValueError(f"Simulator error: {error_msg}\nTraceback:\n{tb_str}")
		raise ValueError(f"Simulator error: {error_msg}")
	
	# Check for required keys with helpful error message
	if 'petri_net' not in resp_json:
		raise ValueError(f"Simulator response missing 'petri_net'. Response keys: {list(resp_json.keys())}")

	petri_net = resp_json['petri_net']
	petri_net_dot = resp_json['petri_net_dot']
	execution_tree = resp_json['execution_tree']['root']
	current_execution = resp_json['execution_tree']['current_node']
	spin_svg = resp_json.get('spin_svg')



	save_petri_net(normalized_bpmn, json.dumps(petri_net, sort_keys=True), petri_net_dot, spin_svg=spin_svg)
	save_execution_tree(normalized_bpmn, json.dumps(execution_tree), current_execution)

	# Convert DOT to SVG for return
	if spin_svg:
		petri_net_svg = f"data:image/svg+xml;base64,{base64.b64encode(spin_svg.encode('utf-8')).decode('utf-8')}"
	else:
		petri_net_svg = dot_to_base64svg(petri_net_dot)

	return get_simulation_data(bpmn, bound_store), petri_net_svg


def preview_petri_net_svg(bpmn: dict) -> str | None:
	"""
	Request a preview of the current Petri net state (no execution), returning the SVG.
	"""
	if bpmn[EXPRESSION] == '':
		return None

	normalized_bpmn = _normalize_bpmn(bpmn)
	parse_tree = load_parse_tree(bpmn)
	petri_net, petri_net_dot, _ = get_petri_net(bpmn, 0)
	execution_tree, current_execution = load_execution_tree(bpmn)

	request = {
		"bpmn": parse_tree,
		"petri_net": petri_net,
		"execution_tree": {"root": execution_tree, "current_node": current_execution},
		"preview": True,
	}

	try:
		response = requests.post(SIMULATOR_SERVER + "execute", json=request, headers=HEADERS)
		response.raise_for_status()
	except requests.exceptions.HTTPError as exc:
		if exc.response is None or exc.response.status_code != 422:
			raise

		parse_tree = load_parse_tree(bpmn, force_refresh=True)
		petri_net, petri_net_dot, _ = get_petri_net(bpmn, 0, force_refresh=True)
		execution_tree, current_execution = load_execution_tree(bpmn, force_refresh=True)

		request = {
			"bpmn": parse_tree,
			"petri_net": petri_net,
			"execution_tree": {"root": execution_tree, "current_node": current_execution},
			"preview": True,
		}

		response = requests.post(SIMULATOR_SERVER + "execute", json=request, headers=HEADERS)
		response.raise_for_status()

	resp_json = response.json()

	if 'error' in resp_json:
		raise ValueError(f"Simulator error: {resp_json['error']}")

	if 'type' in resp_json and resp_json.get('type') == 'error':
		error_msg = resp_json.get('message', 'Unknown error')
		tb = resp_json.get('traceback', [])
		if tb:
			tb_str = '\n'.join(tb) if isinstance(tb, list) else str(tb)
			raise ValueError(f"Simulator error: {error_msg}\nTraceback:\n{tb_str}")
		raise ValueError(f"Simulator error: {error_msg}")

	new_petri_net_dot = resp_json.get('petri_net_dot') or petri_net_dot
	spin_svg = resp_json.get('spin_svg')

	save_petri_net(normalized_bpmn, json.dumps(petri_net, sort_keys=True), new_petri_net_dot or "", spin_svg=spin_svg)

	if spin_svg:
		return f"data:image/svg+xml;base64,{base64.b64encode(spin_svg.encode('utf-8')).decode('utf-8')}"
	if not new_petri_net_dot:
		return None
	return dot_to_base64svg(new_petri_net_dot)


def log_debug(msg):
    try:
        with open("debug.log", "a") as f:
            f.write(f"{msg}\n")
    except Exception as e:
        pass

def _fetch_strategy_data(bpmn_store, bound_store):
	"""Helper to fetch strategy BDDs."""
	log_debug(f"DEBUG: _fetch_strategy_data called. Boundstore keys: {list(bound_store.keys()) if bound_store else 'None'}")
	if not bound_store or BOUND not in bound_store or not bound_store[BOUND]:
		log_debug("DEBUG: bound_store missing or empty BOUND key.")
		return None
	
	try:
		tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
		bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)
		if not bpmn.get(IMPACTS_NAMES):
			log_debug("DEBUG: No IMPACTS_NAMES in bpmn.")
			return None
		bound = [float(bound_store[BOUND].get(impact_name, 0)) for impact_name in bpmn[IMPACTS_NAMES]]
		log_debug(f"DEBUG: Computed bound: {bound}")
		
		record = fetch_strategy(bpmn, bound)
		if record and record.bdds:
			log_debug("DEBUG: Strategy record found with BDDs.")
			bdds_raw = record.bdds
			if isinstance(bdds_raw, dict):
				return bdds_raw
			if isinstance(bdds_raw, str):
				try:
					# record.bdds can be JSON or a Python literal string from save_strategy.
					return json.loads(bdds_raw)
				except json.JSONDecodeError:
					return ast.literal_eval(bdds_raw)
		else:
			log_debug("DEBUG: No strategy record found or no BDDs.")
	except Exception as e:
		log_debug(f"Error fetching strategy: {e}")
		return None
	return None
