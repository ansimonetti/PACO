import os
import json
from jsonschema import validate, ValidationError

SCHEMA_DIR = os.path.dirname(__file__)
SCHEMAS = {}

for schema_file in os.listdir(SCHEMA_DIR):
	if not schema_file.endswith("_schema.json"):
		continue

	with open(os.path.join(SCHEMA_DIR, schema_file), 'r') as f:
		SCHEMAS[schema_file.replace("_schema.json", "")] = json.load(f)


def validate_node(node_data: dict) -> dict:
	node_data['type'] = node_data['type'].lower()
	schema = SCHEMAS.get(node_data['type'])

	if not schema:
		raise ValueError(f"Unsupported node type: {node_data['type']}")

	try:
		validate(instance=node_data, schema=schema)
	except ValidationError as e:
		raise ValueError(f"Validation error in node with id:{node_data['id']} and type:{node_data['type']} : {e}")

	if node_data['type'] == "sequential":
		children = node_data.get("children")
		if isinstance(children, list) and len(children) > 2:
			raise ValueError(f"Sequential node {node_data['id']} has more than two children")

	if node_data['type'] == "task":
		return {node_data['id'] : (node_data['label'], len(node_data['impacts']), 0)}#TODO Daniel: len(node_data['non_cumulative_impact'])

	results = {}
	for node in node_data['children']:
		results.update(validate_node(node))

	return results


def validate_json(node_data: dict, impact_size: int, non_cumulative_impact_size: int):
	task_dict = validate_node(node_data)
	result = ""

	if impact_size == -1 or non_cumulative_impact_size == -1:
		# find the most frequent impact size and non_cumulative impact size
		impact_sizes = {}
		non_cumulative_impact_sizes = {}
		for node_id, (name, node_impact_size, node_non_cumulative_impact_size) in task_dict.items():
			impact_sizes[node_impact_size] = impact_sizes.get(node_impact_size, 0) + 1
			non_cumulative_impact_sizes[node_non_cumulative_impact_size] = non_cumulative_impact_sizes.get(node_non_cumulative_impact_size, 0) + 1

		impact_size = max(impact_sizes, key=impact_sizes.get)
		non_cumulative_impact_size = max(non_cumulative_impact_sizes, key=non_cumulative_impact_sizes.get)

	for node_id, (name, node_impact_size, node_non_cumulative_impact_size) in task_dict.items():
		if node_impact_size != impact_size:
			result += f"Task {name} with id:{node_id} has inconsistent impact size: {node_impact_size} (expected {impact_size})\n"
		if node_non_cumulative_impact_size != non_cumulative_impact_size:
			result += f"Task {name} with id:{node_id} has inconsistent non_cumulative_impact size: {node_non_cumulative_impact_size} (expected {non_cumulative_impact_size})\n"

	if result != "":
		raise ValueError(result)
