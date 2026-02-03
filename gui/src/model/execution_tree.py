def get_prev_execution_node(execution_tree: dict, current_execution_id) -> dict | None:
    """
    Given an execution tree and a current execution ID, return the previous execution node (parent node)
    in the execution tree.

    :param execution_tree: The execution tree dictionary
    :param current_execution_id: The current execution ID
    :return: The parent of current execution node or None if not found
    """
    current_node = get_execution_node(execution_tree, current_execution_id)
    if not current_node:
        return None

    return get_parent_node(execution_tree, current_node['id'])


def get_parent_node(root: dict, node_id: str) -> dict | None:
    """
    Given a tree root and a node ID, return the parent node of the node with the given ID.

    :param root: The root of the tree
    :param node_id: The ID of the node whose parent is to be found
    :return: The parent node dictionary or None if not found
    """
    if root is None:
        return None
    if root['id'] == node_id:
        return None

    for child in root.get('children', []):
        if child['id'] == node_id:
            return root
        result = get_parent_node(child, node_id)
        if result:
            return result

    return None


def get_current_marking_from_execution_tree(execution_tree: dict, current_pointer: str) -> dict:
    """
    Given an execution tree and a current pointer (node ID), return the marking at the current node.

    :param execution_tree: The execution tree dictionary
    :param current_pointer: The current node ID
    :return: The marking dictionary at the current node or empty dict if not found
    """
    if execution_tree['id'] == current_pointer:
        return execution_tree['snapshot']['marking']
    for child in execution_tree.get('children', []):
        result = get_current_marking_from_execution_tree(child, current_pointer)
        if result:
            return result
    return {}


def get_execution_node(root: dict, node_id: str) -> dict | None:
    """
    Given a tree root and a node ID, return the node with the given ID.

    :param root: The root of the tree
    :param node_id: The ID of the node to find
    :return: The node dictionary or None if not found
    """
    if root['id'] == node_id:
        return root
    for child in root.get('children', []):
        result = get_execution_node(child, node_id)
        if result:
            return result
    return None


def get_execution_impacts(execution_tree: dict, node_id: str) -> list[float]:
    """
    Given an execution tree and a node ID, return the impacts at the given node.

    :param execution_tree: The execution tree dictionary
    :param node_id: The ID of the node to find
    :return: The impacts list at the given node or empty list if not found
    """
    node = get_execution_node(execution_tree, node_id)
    if node:
        return __get_execution_impacts(node)
    return []


def __get_execution_impacts(node: dict) -> list[float]:
    """
    Given a node, return the impacts if available.

    :param node: The node dictionary
    :return: The impacts list or empty list if not found
    """
    if 'snapshot' in node and 'impacts' in node['snapshot']:
        return node['snapshot']['impacts']
    return []


def get_execution_probability(execution_tree: dict, node_id: str) -> float:
    """
    Given an execution tree and a node ID, return the probability at the given node.

    :param execution_tree: The execution tree dictionary
    :param node_id: The ID of the node to find
    :return: The probability at the given node or 0.0 if not found
    """
    node = get_execution_node(execution_tree, node_id)
    if node:
        return __get_execution_probability(node)
    return 0.0


def __get_execution_probability(node: dict) -> float:
    """
    Given a node, return the probability if available.

    :param node: The node dictionary
    :return: The probability or 0.0 if not found
    """
    if 'snapshot' in node and 'probability' in node['snapshot']:
        return node['snapshot']['probability']
    return 0.0


def get_execution_time(execution_tree: dict, node_id: str) -> float:
    """
    Given an execution tree and a node ID, return the execution time at the given node.

    :param execution_tree: The execution tree dictionary
    :param node_id: The ID of the node to find
    :return: The execution time at the given node or 0.0 if not found
    """
    node = get_execution_node(execution_tree, node_id)
    if node:
        return __get_execution_time(node)
    return 0.0


def __get_execution_time(node: dict) -> float:
    """
    Given a node, return the execution time if available.

    :param node: The node dictionary
    :return: The execution time or 0.0 if not found
    """
    if 'snapshot' in node and 'execution_time' in node['snapshot']:
        return node['snapshot']['execution_time']
    return 0.0
