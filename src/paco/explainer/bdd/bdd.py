import math
import os
import graphviz
import numpy as np
import pandas as pd

from src.paco.execution_tree.view_point import get_next_task
from src.paco.explainer.bdd.dag_node import DagNode
from src.paco.explainer.explanation_type import ExplanationType
from src.paco.parser.parse_node import ParseNode
from src.utils.env import PATH_EXPLAINER_DECISION_TREE, PATH_BDD


class Bdd:
	def __init__(self, choice: ParseNode, class_0: ParseNode, class_1: ParseNode, typeStrategy:ExplanationType,
				 impacts:list = None, labels:list = None, features_names:list = None, dot = None):
		self.choice = choice
		self.class_0 = class_0
		self.class_1 = class_1 # in case is NOT splittable is None
		is_forced_decision = class_1 is None
		self.typeStrategy = typeStrategy if not is_forced_decision else ExplanationType.FORCED_DECISION
		self.dot = dot
		self.root = None
		self.nodes = None

		#If the dot is already provided, the BDD is already built
		if (not is_forced_decision and
				(dot is None or impacts is None or labels is None or features_names is None)):

			df = pd.DataFrame(impacts, columns=features_names)
			df['class'] = labels # The labels are the id of the ParseNode
			self.root = DagNode(df, class_0, class_1)
			self.nodes = {self.root}


	def __str__(self):
		result = ""
		if self.nodes is not None:
			for node in self.nodes:
				result += str(node) + ", "
		return "{" + result[:-2] + "}"

	def to_dict(self):
		return {
			"choice": self.choice.id,
			"class_0": self.class_0.id,
			"class_1": self.class_1.id if self.class_1 is not None else None,
			"typeStrategy": self.typeStrategy,
			"dot": self.dot,
		}

	@staticmethod
	def from_dict(data: dict, parseTreeNodes: dict):
		choice = parseTreeNodes[data['choice']]
		class_0 = parseTreeNodes[data['class_0']]
		class_1 = parseTreeNodes[data['class_1']] if data['class_1'] is not None else None


		return Bdd(choice, class_0, class_1,
				   ExplanationType(data['typeStrategy']),
				   dot=data['dot'])

	def transitions_str(self):
		result = ""
		for node in self.nodes:
			for target_node in node.edges:
				result += node.transition_str(target_node) + "\n"
		return result

	def is_separable(self):
		if self.root is None:
			#print("is_separable: root is None")
			return True

		#Find duplicates based on all columns except 'class'
		duplicated_vectors = self.root.df[self.root.df.duplicated(
			subset=self.root.df.columns[:-1], keep=False
		)]
		#Group by all columns except 'class' and check for unique 'class' labels
		grouped = duplicated_vectors.groupby(list(duplicated_vectors.columns[:-1]))['class'].nunique()
		#Identify groups with more than one unique label
		conflicting_vectors = grouped[grouped > 1]
		#print("is_separable: ", conflicting_vectors.empty)
		return conflicting_vectors.empty

	def get_splittable_leaves(self):
		return [node for node in self.nodes if len(node.edges) == 0 and node.splittable]

	@staticmethod
	def generate_test(df):
		thresholds = {}
		for c in df.columns:
			if c == 'class':
				continue
			l = sorted(set(df[c]))
			thresholds[c] = [(l[i+1] + l[i])/2 for i in range(len(l)-1)]
		return thresholds

	@staticmethod
	def generate_tests(df, t):
		tests = []
		for feature, thresholds in t.items():
			#print(f"feature: {feature}, thresholds: {thresholds}")
			for threshold in thresholds:
				d1 = df[df[feature] < threshold] #d1 = df[df[feature]] < threshold
				d2 = df[df[feature] >= threshold] #d2 = df[df[feature]] >= threshold
				#print(f"df[k]: {df[feature]}, v: {threshold}, df[k]<v: {df[feature]<threshold}, d1: {d1}, d2: {d2}")
				if len(d1) > 0 and len(d2) > 0:
					tests.append((feature, threshold, True, d1))
					tests.append((feature, threshold, False, d2))
		return tests

	def expand(self, node: DagNode):
		thresholds = self.generate_test(node.df)
		#print("thresholds:",  thresholds)
		for feature, threshold, lt, df in self.generate_tests(node.df, thresholds):
			#print(f"{Node.test_str((feature, threshold, lt))}, index: {index}")
			index = frozenset(sorted(df.index.to_list()))
			target_node = None
			distances_from_root = node.min_distances_from_root + 1
			for n in self.nodes:
				if n.index == index:
					target_node = n
					if target_node.min_distances_from_root > distances_from_root:
						target_node.min_distances_from_root = distances_from_root
					break

			if target_node is None:
				class_0 = self.class_0
				class_1 = self.class_1

				target_node = DagNode(df, class_0, class_1)
				self.nodes.add(target_node)
				target_node.min_distances_from_root = distances_from_root

			edge = (feature, threshold, lt)
			changed = node.add_node(target_node, edge)
			#print(node.transition_str(target_node, changed))

	def compute_tree(self, node: DagNode):
		if node.visited:
			return
		if len(node.edges) == 0: # is leaf
			node.best_height = 0
			node.visited = True
			return

		for child in node.edges.keys():
			self.compute_tree(child)
		for test in node.tests:
			target_t, target_f = node.get_targets(test)
			if (target_t.best_height < math.inf or target_f.best_height < math.inf) and len(node.edges) > 0: # is not leaf
				candidate_max_height = max(target_t.best_height, target_f.best_height) + 1
				if candidate_max_height < node.best_height:
					node.best_height = candidate_max_height
					node.best_test = test
			node.visited = True

	def build(self, debug=False):
		if self.typeStrategy == ExplanationType.FORCED_DECISION:
			self.dot = self.bdd_to_dot()
			return True

		if not self.is_separable():
			return False

		i = 1
		while True:
			open_leaves = self.get_splittable_leaves()
			if len(open_leaves) == 0:
				break

			for node in open_leaves:
				self.expand(node)

			#print(f"step {i}\n", self)
			#print(self.transitions_str())
			if debug:
				self.save_dag(f'{PATH_EXPLAINER_DECISION_TREE}_{str(self.choice.name)}_{i}')
			i += 1

		#print(f"computed tree: {i}\n", self)
		self.compute_tree(self.root)
		if debug:
			self.save_dag(f'{PATH_EXPLAINER_DECISION_TREE}_{str(self.choice.name)}_{i}_final')

		self.dot = self.bdd_to_dot()
		return True


	def get_minimum_tree_nodes(self, node: DagNode):
		nodes = []
		if node.best_test is not None and len(node.edges) > 0: # is not leaf
			nodes.append(node)
			target_t, target_f = node.get_targets(node.best_test)
			nodes.extend(self.get_minimum_tree_nodes(target_t))
			nodes.extend(self.get_minimum_tree_nodes(target_f))
		return nodes

	def choose(self, vector: np.ndarray):
		if self.root is None:# forced decision give always the same decision
			return self.class_0

		if vector.size != len(self.root.df.columns[:-1]):
			raise Exception("BDD:choose: different columns size")

		df = pd.DataFrame([vector], columns=self.root.df.columns[:-1])
		#print("df:", df)

		node:DagNode = self.root
		while node.splittable:
			feature, threshold, lt = node.best_test
			#print(f"node: {node}, feature: {feature}")
			true_node, false_node = node.get_targets(node.best_test)
			#print("true_node: ", true_node)
			#print("false_node: ", false_node)

			#print(f"value: {df.loc[0, feature]} {'<' if lt else '>='} threshold: {threshold}")
			result = df.loc[0, feature] < threshold if lt else df.loc[0, feature] >= threshold
			#print("Result: ", result)
			node = true_node if result else false_node

		return node.class_0

	def dag_to_dot(self):
		dot = graphviz.Digraph()

		minimum_tree_nodes = self.get_minimum_tree_nodes(self.root)
		for node in self.nodes:
			node_name = str(node)
			label = f"{node_name}\nmin depth: {node.min_distances_from_root}\nBest Height: {node.best_height}\n"

			color = 'white'
			if node.best_test is not None:
				label += f"Test: {node.best_test[0]} < {node.best_test[1]}\n"
			if node in minimum_tree_nodes:
				color = 'lightblue'

			class_0_name = node.class_0.name if node.class_0.name else node.class_0.id
			if not node.splittable:
				color = 'green'
				label += f"Class: {class_0_name}"
			else:
				class_1_name = node.class_1.name if node.class_1.name else node.class_1.id
				label += f"Classes: {class_0_name}, {class_1_name}"

			dot.node(node_name, label=label, style='filled', fillcolor=color)

			for target_node, edge in node.edges.items():
				dot.edge(node_name, str(target_node), label=DagNode.edge_str(edge))

		return dot

	def save_dag(self, file_path:str):
		dot = self.dag_to_dot()
		dot.save(file_path + '.dot')
		dot.render(filename=file_path, format='svg')
		os.remove(file_path)  # tmp dot file
		#os.remove(file_path + '.dot')  # tmp dot file


	def bdd_to_dot(self) -> str:
		if self.dot is not None:
			return self.dot

		dot = graphviz.Digraph()

		dot.node(str(self.choice.name), label=f"{self.choice.name}", shape="box", style="filled", color="black", fillcolor="orange")

		if self.typeStrategy != ExplanationType.FORCED_DECISION:
			dot.edge(str(self.choice.name), str(self.root))
			self.bdd_to_dot_recursively(dot, self.root)
		else:
			if self.choice.children[1] == self.class_0:
				label = '0'
				next_task, names, color = get_next_task(self.choice.children[1])
			else:
				label = '1'
				next_task, names, color = get_next_task(self.choice.children[0])

			dot.node(label, label=label, shape="box", style="filled", color="black", fillcolor=color)
			dot.edge(str(self.choice.name), label, label="True", style='')

		return dot.source


	def save_bdd(self, outfile:str = ""):
		if outfile == "":
			outfile = PATH_BDD + "_" + self.choice.name

		directory = os.path.dirname(outfile)
		if directory:
			os.makedirs(directory, exist_ok=True)

		dot = self.bdd_to_dot()
		with open(outfile + ".svg", "wb") as f:
			f.write(graphviz.Source(dot).pipe(format="svg"))


	def bdd_to_dot_recursively(self, dot, node: DagNode):
		if not node.splittable:
			if node.class_0 == self.choice.children[1]:
				label = '0'
				next_task, names, color = get_next_task(self.choice.children[0])
			else:
				label = '1'
				next_task, names, color = get_next_task(self.choice.children[1])

			dot.node(str(node), label=label, shape="box", style="filled", color="black", fillcolor=color)
		elif node.best_test is None:
			dot.node(str(node), label="Undetermined", shape="box", style="filled", color="black", fillcolor="red")
		else:
			left_child, right_child = node.get_targets(node.best_test)

			if self.typeStrategy != ExplanationType.DECISION_BASED:
				dot.node(str(node), label=f"{node.best_test[0]} < {node.best_test[1]}", shape="ellipse")

				#The left is always the true condition
				if not node.best_test[2]: # Swap to keep always < instead of >=
					tmp = left_child
					left_child = right_child
					right_child = tmp
			else:
				#decisions_names = [f"{d.parent.name}_{'0' if d.parent.sx_child == d else '1'}" for d in decisions]
				# node.best_test[0] is like N1_0 or N1_1 look at find_all_decisions
				print(f"Best test: {node.best_test}?")
				dot.node(str(node), label=f"Exec: {node.best_test[0]}?", shape="ellipse")
				if node.best_test[2]: # Swap to keep always to check if active instead of not active
					tmp = left_child
					left_child = right_child
					right_child = tmp

			dot.edge(str(node), self.bdd_to_dot_recursively(dot, left_child), label="True", style="")
			dot.edge(str(node), self.bdd_to_dot_recursively(dot, right_child), label="False", style="")

		return str(node)
