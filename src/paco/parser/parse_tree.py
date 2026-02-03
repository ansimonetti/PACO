import json
import os
from abc import ABC
import graphviz

from src.utils.env import PATH_PARSE_TREE
from ..evaluations.sampler_expected_impact import sample_expected_impact
from .json_schema.json_validator import validate_json
from .parse_node import Choice, Gateway, Loop, Nature, Parallel, Sequential, Task


class ParseTree:
	def __init__(self, root: "ParseNode(ABC)") -> None:
		self.root = root

	def sample_expected_impact(self):
		return sample_expected_impact(json.loads(self.to_json()), track_choices=False)

	def copy(self) -> "ParseTree":
		return ParseTree(self.root.copy())

	def dot_tree(self, root: "ParseNode(ABC)" = None):
		if root is None:
			root = self.root

		if isinstance(root, Task):
			return root.dot()

		dot_code = root.dot()
		for child in root.children:
			dot_code += self.dot_tree(child)

		for i in range(len(root.children)):
			edge_label = ""
			if isinstance(root, Nature):
				edge_label = f"{root.distribution[i]}"

			dot_code += f'\n node_{root.id} -> node_{root.children[i].id} [label="{edge_label}"];'

		return dot_code

	def to_dot(self):
		return "digraph parse_tree{" + self.dot_tree() + "}"

	def save_dot(self, outfile=PATH_PARSE_TREE):
		directory = os.path.dirname(outfile)
		if directory:
			os.makedirs(directory, exist_ok=True)

		dot = self.to_dot()
		with open(outfile + ".svg", "wb") as f:
			f.write(graphviz.Source(dot).pipe(format="svg"))

	def to_json(self) -> str:
		return json.dumps(self.root.to_dict(), indent=2)

	def to_dict(self) -> dict:
		return self.root.to_dict()

	def to_dict_id_node(self) -> dict:
		return self.root.to_dict_id_node()

	@staticmethod
	def create_node(
			node_data: dict,
			parent: "ParseNode" = None,
			impact_size=-1,
			non_cumulative_impact=-1,
	) -> "ParseNode":
		node_type = node_data["type"].lower()
		node_id = node_data["id"]
		index_in_parent = node_data.get("index_in_parent", -1)
		pending_choice, pending_natures = set(), set()

		if node_type == "task":
			return (
				Task(
					parent=parent,
					index_in_parent=index_in_parent,
					id=node_id,
					name=node_data["label"],
					impact=node_data["impacts"],
					#TODO Daniel: non_cumulative_impact=node_data["non_cumulative_impact"],
					duration=node_data["duration"],
				),
				pending_choice,
				pending_natures,
			)

		if node_type == "sequential":
			node = Sequential(
				parent=parent, index_in_parent=index_in_parent, id=node_id
			)
		elif node_type == "parallel":
			node = Parallel(parent=parent, index_in_parent=index_in_parent, id=node_id)
		elif node_type == "choice":
			node = Choice(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data["label"],
				max_delay=node_data["max_delay"],
			)
			pending_choice.add(node)
		elif node_type == "nature":
			node = Nature(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data["label"],
				distribution=node_data["distribution"],
			)
			pending_natures.add(node)
		elif node_type == "loop":
			node = Loop(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data["label"],
				probability=node_data["probability"],
				bound=node_data["bound"],
			)
		else:
			raise ValueError(f"Unsupported node type: {node_type}")

		# Recursively create children if they exist
		if isinstance(node, Gateway):
			#sx_child_data = node_data.get("sx_child")
			#dx_child_data = node_data.get("dx_child")
			children_data = node_data.get("children")#Is a list

			if isinstance(node, Sequential) and children_data and len(children_data) > 2:
				raise ValueError(f"Sequential node {node_id} has more than two children")

			children = []
			for child_data in children_data:
				child, pending_choice, spending_natures = (
					ParseTree.create_node(
						child_data,
						parent=node,
						impact_size=impact_size,
						non_cumulative_impact=non_cumulative_impact,
					)
				)
				children.append(child)
				pending_choice.update(pending_choice)
				pending_natures.update(pending_natures)

			node.set_children(children)

		return node, pending_choice, pending_natures

	@staticmethod
	def from_json(
			data, impact_size: int = -1, non_cumulative_impact_size: int = -1
	) -> "ParseTree":
		if isinstance(data, str):
			data = json.loads(data)

		validate_json(data, impact_size, non_cumulative_impact_size)
		
		root, pending_choice, pending_natures = ParseTree.create_node(data)
		return ParseTree(root), pending_choice, pending_natures
