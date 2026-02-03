import json

from src.paco.explainer.bdd.bdd import Bdd
from src.paco.parser.parse_node import ParseNode
from src.paco.parser.parse_tree import ParseTree


def bdds_from_json(parseTree: 'ParseTree', data) -> dict[ParseNode:Bdd]:
	if isinstance(data, str):
		data = json.loads(data)

	parseTreeNodes = parseTree.root.to_dict_id_node()
	return {parseTreeNodes[int(choice_id)]: Bdd.from_dict(bdd_data, parseTreeNodes)
							 for choice_id, bdd_data in data.items()}


def bdds_to_dict(bdds: dict[ParseNode:Bdd]) -> dict[int, dict]:
	return {choice.id: bdd.to_dict() for choice, bdd in bdds.items()}


def bdds_to_json(bdds: dict[ParseNode:Bdd]) -> str:
	return json.dumps(bdds_to_dict(bdds), indent=2)


def bdds_to_dict_dot(bdds: dict[ParseNode:Bdd]) -> dict[str, str]:
	return {choice.name: (str(bdd.typeStrategy), bdd.bdd_to_dot()) for choice, bdd in bdds.items()}
