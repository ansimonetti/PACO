ACTIVE_NODE_COLOR = "ffa500"        # Orange
INACTIVE_NODE_COLOR = "808080"      # Grey
TEXT_COLOR = "000000"               # Black
ALPHA_ACTIVE_BACKGROUND = "ff"      # Full opacity for visible nodes
ALPHA_ACTIVE_TEXT = "ff"            # Full opacity for visible nodes
ALPHA_INACTIVE_BACKGROUND = "7f"    # Semi-transparent for inactive nodes
ALPHA_INACTIVE_TEXT = "7f"          # Semi-transparent for inactive nodes

def tree_node_to_dot(_id, p, impacts, execution_time, impacts_name=None, visible=True):
	"""
    Render a single node of the execution tree as a dot representation.

	:param _id: Node ID
	:param p: Probability
	:param impacts: List of impacts
	:param execution_time: Execution time
	:param impacts_name: Names of the impacts
	:param visible: Whether the node is in the highlighted path
	:return: Dot representation of the node
	"""
	if impacts_name is None or len(impacts_name) == 0:
		impacts_name = [i+1 for i in range(len(impacts))]

	bg_color = ACTIVE_NODE_COLOR if visible else INACTIVE_NODE_COLOR  # Use active color if visible, inactive if not
	alpha_bg = ALPHA_ACTIVE_BACKGROUND if visible else ALPHA_INACTIVE_BACKGROUND  # Full opacity if visible, semi-transparent if not
	alpha_text = ALPHA_ACTIVE_TEXT if visible else ALPHA_INACTIVE_TEXT  # Full opacity if visible, semi-transparent if not
	impacts_label = "[" + ", ".join([f"{name}: {value}" for name, value in zip(impacts_name, impacts)]) + "]"
	return f'\nnode_{_id}[shape=oval label="ID: {_id}\\nProbability: {p}\\nImpacts:\\n{impacts_label}\\nExecution time: {execution_time}" style="filled" fillcolor="#{bg_color}{alpha_bg}" fontcolor="#{TEXT_COLOR}{alpha_text}"];'

def tree_to_dot(tree_root, impacts_names, path=None):
	"""
	Render the execution tree as a dot representation.
	:param tree_root: Root of the execution tree
	:param impacts_names: Impacts names to display
	:param path: Ids of the nodes in the path to highlight
	:return: Dot representation of the execution tree
	"""
	if path is None:
		path = []

	def apply(root):
		code = ""
		is_active = root.get('id') in path

		node_id = root.get('id')
		snapshot = root.get('snapshot', {})
		p = snapshot.get('p', 1.0)
		impacts = snapshot.get('impacts', [0 for _ in impacts_names])
		execution_time = snapshot.get('execution_time', 0)

		code += tree_node_to_dot(
			node_id,
			p,
			impacts,
			execution_time,
			impacts_name=impacts_names,
			visible=is_active
		)

		for child in root.get("children", []):
			child_code = apply(child)
			code += child_code
			code += f'\nnode_{root.get("id")} -> node_{child.get("id")};\n'

		return code

	return apply(tree_root)


def get_execution_tree_dot(execution_tree: dict, impacts_names: list[str], path: list[str] = []):
	"""
	Wrapper to create the dot representation of the execution tree.

	:param execution_tree: Execution tree object
	:param impacts_names: Impacts names to display
	:param path: Ids of the nodes in the path to highlight
	:return: Dot representation of the execution tree
	"""
	code = "digraph G {\n"
	code += tree_to_dot(execution_tree, impacts_names, path)
	code += "\n}"

	return code

def get_path_to_current_node(tree_root, current_node_id):
	"""
	Get the path to the current node in the execution tree.
	:param tree_root: Root of the execution tree
	:param current_node_id: ID of the current node
	:return: List of node IDs in the path to the current node
	"""
	if tree_root.get('id') == current_node_id:
		return [current_node_id]

	for child in tree_root.get("children", []):
		path = get_path_to_current_node(child, current_node_id)
		if path is not None:
			return [tree_root.get('id')] + path

	return None


