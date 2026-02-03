import random

def sample_expected_impact(root_dict, track_choices=False):
	def merge_impacts(impact1, impact2):
		return [a + b for a, b in zip(impact1, impact2)]

	def scale_impacts(impacts, scale):
		if isinstance(scale, (list, tuple)):
			return [s * x for s, x in zip(scale, impacts)]
		return [scale * x for x in impacts]

	choices_made = {}

	def process_node(node):
		if node["type"] == "task":
			return node["impacts"]

		if node["type"] == "sequential":
			acc = None
			for child in node["children"]:
				vec = process_node(child)
				acc = vec if acc is None else merge_impacts(acc, vec)
			return acc if acc is not None else []

		elif node["type"] == "parallel":
			acc = None
			for child in node["children"]:
				vec = process_node(child)
				acc = vec if acc is None else merge_impacts(acc, vec)
			return acc if acc is not None else []

		elif node["type"] == "choice":
			idx = random.randrange(len(node["children"]))
			if track_choices:
				choices_made[f"choice{node['id']}"] = idx
			return process_node(node["children"][idx])

		elif node["type"] == "nature":
			acc = None
			for i in range(len(node["children"])):
				vec = scale_impacts(process_node(node["children"][i]), node["distribution"][i])
				acc = vec if acc is None else merge_impacts(acc, vec)
			return acc if acc is not None else []

		raise ValueError(f"Unknown node type: {node['type']}")

	impacts = process_node(root_dict)
	if track_choices:
		return impacts, choices_made
	return impacts
