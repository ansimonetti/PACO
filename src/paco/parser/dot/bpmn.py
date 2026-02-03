from ..parse_node import ParseNode, Nature, Parallel, Sequential, Loop, Choice, Task
from ..parse_tree import ParseTree
from ...saturate_execution.states import ActivityState

ACTIVE_BORDER_COLOR = "red"
ACTIVE_BORDER_WIDTH = 4
ACTIVE_STYLE = "solid"
WAITING_STYLE = "dashed"

TASK_FILL_COLOR = "lightblue"
TASK_COMPLETED_FILL_COLOR = "lightskyblue"
EXCLUSIVE_GATEWAY_FILL_COLOR = "orange"
EXCLUSIVE_GATEWAY_COMPLETED_FILL_COLOR = "darkorange"
PARALLEL_GATEWAY_FILL_COLOR = "green"
PARALLEL_GATEWAY_COMPLETED_FILL_COLOR = "forestgreen"
PROBABILISTIC_GATEWAY_FILL_COLOR = "yellowgreen"
PROBABILISTIC_GATEWAY_COMPLETED_FILL_COLOR = "olivedrab"
LOOP_GATEWAY_FILL_COLOR = "yellowgreen"
LOOP_GATEWAY_COMPLETED_FILL_COLOR = "olivedrab"

SKIPPED_FILL_COLOR = "lightgray"


def node_to_dot(_id, shape, label, style, fillcolor, border_color=None, border_size=None):
    """
    Create the dot representation of a node.

    :param _id: Unique ID of the node
    :param shape: Shape of the node
    :param label: Label of the node
    :param style: Style of the node
    :param fillcolor: Fill color of the node
    :param border_color: Border color of the node
    :param border_size: Border size of the node
    :return: Dot representation of the node
    """
    other_code = ""
    if border_color is not None:
        other_code += f'color={border_color} '
    if border_size is not None:
        other_code += f'penwidth={border_size} '
    return f'\nnode_{_id}[shape={shape} label="{label or ""}" style="{style or ""}" fillcolor={fillcolor} {other_code or ""}];'


def gateway_to_dot(_id, label, style, fillcolor, border_color=None, border_size=None):
    """
    Create the dot representation of a gateway.

    :param _id: Unique ID of the gateway
    :param label: Label of the gateway
    :param style: Style of the gateway
    :param fillcolor: Fill color of the gateway
    :param border_color: Border color of the gateway
    :param border_size: Border size of the gateway
    :return: Dot representation of the gateway
    """
    return node_to_dot(_id, "diamond", label, style, fillcolor, border_color, border_size)


def exclusive_gateway_to_dot(_id, label, style, fillcolor=None, border_color=None, border_size=None):
    """
    Create the dot representation of an exclusive gateway.

    :param _id: Unique ID of the gateway
    :param label: Label of the gateway
    :param style: Style of the gateway
    :param border_color: Border color of the gateway
    :param border_size: Border size of the gateway
    :return: Dot representation of the gateway
    """
    if style is None:
        style = "filled"
    else:
        style = f"filled,{style}"
    if fillcolor is None:
        fillcolor = EXCLUSIVE_GATEWAY_FILL_COLOR
    return gateway_to_dot(_id, label, style, fillcolor, border_color, border_size)


def parallel_gateway_to_dot(_id, style=None, fillcolor=None, border_color=None, border_size=None):
    """
    Create the dot representation of a parallel gateway.

    :param _id: Unique ID of the gateway
    :param style: Style of the gateway
    :param border_color: Border color of the gateway
    :param border_size: Border size of the gateway
    :return: Dot representation of the gateway
    """
    if fillcolor is None:
        fillcolor = PARALLEL_GATEWAY_FILL_COLOR
    return gateway_to_dot(_id, f"+", style, fillcolor, border_color, border_size)


def probabilistic_gateway_to_dot(_id, name, style, fillcolor=None, border_color=None, border_size=None):
    """
    Create the dot representation of a probabilistic gateway.

    :param _id: Unique ID of the gateway
    :param name: Name of the gateway
    :param style: Style of the gateway
    :param border_color: Border color of the gateway
    :param border_size: Border size of the gateway
    :return: Dot representation of the gateway
    """
    if style is None:
        style = "filled"
    else:
        style = f"filled,{style}"
    if fillcolor is None:
        fillcolor = PROBABILISTIC_GATEWAY_FILL_COLOR
    return gateway_to_dot(_id, f"{name}", style, fillcolor, border_color, border_size)


def loop_gateway_to_dot(_id, label, style, fillcolor=None, border_color=None, border_size=None):
    """
    Create the dot representation of a loop gateway.

    :param _id: Unique ID of the gateway
    :param label: Label of the gateway
    :param style: Style of the gateway
    :param border_color: Border color of the gateway
    :param border_size: Border size of the gateway
    :return: Dot representation of the gateway
    """
    if style is None:
        style = "filled"
    else:
        style = f"filled,{style}"
    if fillcolor is None:
        fillcolor = LOOP_GATEWAY_FILL_COLOR
    return gateway_to_dot(_id, label, style, fillcolor, border_color, border_size)


def task_to_dot(_id, name, style, impacts, duration, impacts_names, fillcolor=None, border_color=None, border_size=None):
    """
    Create the dot representation of a task.

    :param _id: Unique ID of the task
    :param name: Name of the task
    :param style: Style of the task
    :param impacts: List of impacts values
    :param duration: Duration of the task
    :param impacts_names: Names of the impacts
    :param border_color: Border color of the task
    :param border_size: Border size of the task
    :return: Dot representation of the task
    """

    additional_label = ""

    tmp = ""
    for i in range(len(impacts)):
        tmp += f"\\n{impacts_names[i]}: {impacts[i]}"

    additional_label += f"\\n impacts: {tmp}"
    if duration:
        additional_label += f"\\n duration: {duration}"

    if style is None:
        style = "rounded,filled"
    else:
        style = f"rounded,filled,{style}"

    if fillcolor is None:
        fillcolor = TASK_FILL_COLOR

    return node_to_dot(
        _id,
        "rectangle",
        f"{name}{additional_label}",
        style,
        fillcolor,
        border_color,
        border_size
    )


def arc_to_dot(source, target, label=None, style=None):
    """
    Create the dot representation of an arc.

    :param source: Source node ID
    :param target: Target node ID
    :param label: Label of the arc
    :return: Dot representation of the arc
    """
    attrs = []
    if label is not None:
        attrs.append(f'label="{label}"')
    if style is not None:
        attrs.append(f"style={style}")
    attrs_code = f"[{' '.join(attrs)}]" if attrs else ""
    return f'\nnode_{source} -> node_{target}{attrs_code};\n'



def get_bpmn_dot_from_parse_tree(parse_tree: ParseTree, impacts_names: list[str], status:dict):

    """
    Wrapper to create the dot representation of the BPMN.
    :param parse_tree: Parse tree of the expression
    :param impacts_names: Impacts names to display
    :param active_regions: Ids of the active regions to highlight
    :return: Dot representation of the BPMN
    """
    node_status = _get_status(status, parse_tree.root.id)

    is_initial = node_status is None or node_status == ActivityState.WAITING
    #print("Root id", parse_tree.root.id, " status:", node_status, "is_initial:", is_initial)
    is_final = node_status is not None and node_status > ActivityState.ACTIVE


    code = "digraph G {\n"
    code += "rankdir=LR;\n"
    code += node_to_dot("start",
                        "circle",
                        "",
                        "filled",
                        "palegreen1",
                        border_color=ACTIVE_BORDER_COLOR if is_initial else None,
                        border_size=ACTIVE_BORDER_WIDTH if is_initial else None, ) + "\n"

    border_color = ACTIVE_BORDER_COLOR if is_final else None
    border_size = ACTIVE_BORDER_WIDTH if is_final else None
    code += node_to_dot("end",
                        "doublecircle",
                        "",
                        "filled",
                        "orangered",
                        border_color=border_color,
                        border_size=border_size) + "\n"

    other_code, entry_id, exit_id, exit_p = region_to_dot(parse_tree.root, impacts_names, status)
    code += other_code
    code += f'node_start -> node_{entry_id};\n'
    end_label = f'[label="{exit_p}"]' if exit_p != 1.0 else ''
    code += f'node_{exit_id} -> node_end{end_label};\n'
    code += "\n}"

    return code


def serial_generator():
    """Generator to create unique IDs."""
    id_counter = 0
    while True:
        yield id_counter
        id_counter += 1


id_generator = serial_generator()


def _get_status(status, node_id):
    """Return the status value for *node_id* supporting both int and str keys."""

    if node_id in status:
        return status[node_id]

    str_key = str(node_id)
    if str_key in status:
        return status[str_key]

    return None


def region_to_dot(region_root: ParseNode, impacts_names, status) -> tuple[str, int, int, float]:
    node_status = _get_status(status, region_root.id)
    is_active = node_status == ActivityState.ACTIVE
    is_pending = node_status is None or node_status <= ActivityState.ACTIVE
    is_completed = node_status is not None and node_status > ActivityState.ACTIVE
    is_skipped = node_status == ActivityState.WILL_NOT_BE_EXECUTED

    type_by_name = type(region_root).__name__
    if isinstance(region_root, Task) or type_by_name == 'Task':
        _id = next(id_generator)
        task_style = WAITING_STYLE if is_pending else None
        return task_to_dot(
            _id,
            region_root.name,
            task_style,
            region_root.impacts,
            region_root.duration,
            impacts_names,
            fillcolor=SKIPPED_FILL_COLOR if is_skipped else (TASK_COMPLETED_FILL_COLOR if is_completed else None),
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        ), _id, _id, 1.0
    elif isinstance(region_root, Loop) or type_by_name == 'Loop':
        entry_id = next(id_generator)
        exit_id = next(id_generator)

        # Entry point
        code = loop_gateway_to_dot(
            entry_id,
            region_root.name,
            style=None,
            fillcolor=LOOP_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None,
        )

        # Exit point
        code += loop_gateway_to_dot(
            exit_id,
            region_root.name,
            style=None,
            fillcolor=LOOP_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Child
        other_code, child_entry_id, child_exit_id, exit_p = region_to_dot(region_root.children[0], impacts_names,
                                                                          status)
        code += other_code
        p = region_root.probability
        code += arc_to_dot(entry_id, child_entry_id)
        code += arc_to_dot(exit_id, entry_id, label=p)
        code += arc_to_dot(child_exit_id, exit_id, label=exit_p if exit_p != 1 else None)

        return code, entry_id, exit_id, 1 - p
    elif isinstance(region_root, Choice)  or type_by_name == 'Choice':
        entry_id = next(id_generator)
        last_exit_id = next(id_generator)

        # Entry point
        code = exclusive_gateway_to_dot(
            entry_id,
            region_root.name,
            ACTIVE_STYLE if is_active else None,
            fillcolor=EXCLUSIVE_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Exit point
        code += exclusive_gateway_to_dot(
            last_exit_id,
            region_root.name,
            style=None,
            fillcolor=EXCLUSIVE_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None
        )

        # Children
        for child_index, child in enumerate(region_root.children):
            child_code, child_entry_id, child_exit_id, exit_p = region_to_dot(child, impacts_names, status)
            code += child_code
            edge_style = "dashed" if (child_index % 2 == 0) else None
            code += arc_to_dot(entry_id, child_entry_id, style=edge_style)
            code += arc_to_dot(
                child_exit_id,
                last_exit_id,
                label=exit_p if exit_p != 1 else None,
                style=edge_style,
            )

        return code, entry_id, last_exit_id, 1.0
    elif isinstance(region_root, Parallel) or type_by_name == 'Parallel':
        entry_id = next(id_generator)
        last_exit_id = next(id_generator)

        # Entry point
        code = parallel_gateway_to_dot(
            entry_id,
            style=ACTIVE_STYLE if is_active else None,
            fillcolor=PARALLEL_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Exit point
        code += parallel_gateway_to_dot(
            last_exit_id,
            style=None,
            fillcolor=PARALLEL_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None
        )

        # Children
        for child in region_root.children:
            child_code, child_entry_id, child_exit_id, exit_p = region_to_dot(child, impacts_names, status)
            code += child_code
            code += arc_to_dot(entry_id, child_entry_id)
            code += arc_to_dot(child_exit_id, last_exit_id, label=exit_p if exit_p != 1 else None)

        return code, entry_id, last_exit_id, 1.0
    elif isinstance(region_root, Nature) or type_by_name == 'Nature':
        entry_id = next(id_generator)
        last_exit_id = next(id_generator)

        # Entry point
        code = probabilistic_gateway_to_dot(
            entry_id,
            region_root.name,
            style=ACTIVE_STYLE if is_active else None,
            fillcolor=PROBABILISTIC_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Exit point
        code += probabilistic_gateway_to_dot(
            last_exit_id,
            region_root.name,
            style=None,
            fillcolor=PROBABILISTIC_GATEWAY_COMPLETED_FILL_COLOR if is_completed else None
        )

        # Children
        for child, p in zip(region_root.children, region_root.distribution):
            child_code, child_entry_id, child_exit_id, exit_p = region_to_dot(child, impacts_names, status)
            code += child_code
            code += arc_to_dot(entry_id, child_entry_id, p)
            code += arc_to_dot(child_exit_id, last_exit_id, label=exit_p if exit_p != 1 else None)

        return code, entry_id, last_exit_id, 1.0
    elif isinstance(region_root, Sequential) or type_by_name == 'Sequential':
        code = ""
        entry_id = None
        last_exit_id = None
        last_exit_p = None

        for i, child in enumerate(region_root.children):
            child_code, child_entry_id, child_exit_id, exit_p = region_to_dot(child, impacts_names, status)
            code += child_code

            if last_exit_id is not None:
                arc = arc_to_dot(last_exit_id,
                                 child_entry_id,
                                 label=last_exit_p if last_exit_p is not None and last_exit_p != 1 else None)
            else:
                arc = ""
            if entry_id is None:
                entry_id = child_entry_id
                arc = ""

            last_exit_id = child_exit_id
            last_exit_p = exit_p
            code += arc

        return code, entry_id, last_exit_id, last_exit_p
    else:
        raise ValueError(f"Unknown type: {type_by_name}")
