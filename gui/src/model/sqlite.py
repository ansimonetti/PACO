from pony.orm import Database, Required, Optional, Set, db_session, commit, rollback
import json
from gui.src.env import DB_PATH

db = Database()

class BPMN(db.Entity):
	bpmn = Required(str, unique=True)
	bpmn_dot = Optional(str, nullable=True)
	parse_tree = Optional(str, nullable=True)
	execution_tree = Optional(str, nullable=True)
	petri_net = Optional(str, nullable=True)
	petri_net_dot = Optional(str, nullable=True)
	spin_svg = Optional(str, nullable=True)
	execution_petri_net = Optional(str, nullable=True)
	actual_execution = Optional(str, nullable=True)

	strategie = Set('Strategy')

class Bound(db.Entity):
	bound_data = Required(str, unique=True)
	strategie = Set('Strategy')

class Strategy(db.Entity):
	bpmn = Required(BPMN)
	bound = Required(Bound)
	result = Required(str)
	expected_impacts = Optional(str, nullable=True)
	guaranteed_bounds = Required(str, nullable=True)
	possible_min_solution = Required(str, nullable=True)
	bdds = Optional(str, nullable=True)


if not db.provider:
	db.bind(provider='sqlite', filename=DB_PATH, create_db=True)
	db.generate_mapping(create_tables=True)



@db_session
def fetch_bpmn(bpmn_dict:dict) -> BPMN | None:
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	return BPMN.get(bpmn=bpmn_str)


@db_session
def fetch_strategy(bpmn_dict:dict, bound_list:list):
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	bound_json = json.dumps(bound_list)

	bpmn = BPMN.get(bpmn=bpmn_str)
	if not bpmn:
		return None

	bound = Bound.get(bound_data=bound_json)
	if not bound:
		return None

	return Strategy.get(bpmn=bpmn, bound=bound)


@db_session
def save_bpmn_dot(bpmn_dict:dict, bpmn_dot:str):
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	if not BPMN.get(bpmn=bpmn_str):
		BPMN(bpmn=bpmn_str, bpmn_dot=bpmn_dot, parse_tree="", execution_tree="")
		commit()

@db_session
def update_bpmn_dot(bpmn_dict:dict, bpmn_dot:str):
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	record = BPMN.get(bpmn=bpmn_str)
	if record:
		record.bpmn_dot = bpmn_dot or ""
		commit()

@db_session
def save_execution_tree(bpmn_dict: dict, execution_tree: str, actual_execution: str):
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	record = BPMN.get(bpmn=bpmn_str)
	if not record:
		record = BPMN(bpmn=bpmn_str)
	record.execution_tree = execution_tree or ""
	record.actual_execution = actual_execution or ""
	commit()

@db_session
def save_parse_tree(bpmn_dict:dict, parse_tree:str):
	# print("save_parse_tree: ", parse_tree)
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	record = BPMN.get(bpmn=bpmn_str)
	if not record:
		record = BPMN(bpmn=bpmn_str)
	record.parse_tree = parse_tree or ""
	commit()


@db_session
def save_parse_and_execution_tree(bpmn_dict:dict, parse_tree:str, execution_tree:str):
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	record = BPMN.get(bpmn=bpmn_str)
	if record:
		record.parse_tree = parse_tree or ""
		record.execution_tree = execution_tree or ""
		commit()

@db_session
def save_strategy(bpmn_dict: dict, bound_list: list, result:str, expected_impacts:str,
				  guaranteed_bounds:str, possible_min_solution:str, bdds: dict):

	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	bound_json = json.dumps(bound_list)

	bpmn = BPMN.get(bpmn=bpmn_str)
	if not bpmn:
		bpmn = BPMN(bpmn=bpmn_str)

	bound = Bound.get(bound_data=bound_json)
	if not bound:
		bound = Bound(bound_data=bound_json)

	if not Strategy.get(bpmn=bpmn, bound=bound):
		Strategy(bpmn=bpmn, bound=bound,
				 result=result, expected_impacts=expected_impacts,
				 guaranteed_bounds=guaranteed_bounds, possible_min_solution=possible_min_solution,
				 bdds=str(bdds))

	commit()



@db_session
def save_petri_net(bpmn_dict:dict, petri_net:str, petri_net_dot:str, spin_svg:str=None):
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	record = BPMN.get(bpmn=bpmn_str)
	if not record:
		record = BPMN(bpmn=bpmn_str)
	record.petri_net = petri_net or ""
	record.petri_net_dot = petri_net_dot or ""
	record.spin_svg = spin_svg or ""
	commit()


@db_session
def save_execution_petri_net(bpmn_dict:dict, execution_petri_net:str, actual_execution:str):
	bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
	record = BPMN.get(bpmn=bpmn_str)
	if record:
		record.execution_petri_net = execution_petri_net or ""
		record.actual_execution = actual_execution or ""
		commit()
