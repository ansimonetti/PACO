"""
Simulation Actions Module
Handles simulation stepping and reset logic.
"""
import logging
from dash import no_update
from gui.src.model.etl import (
    bpmn_snapshot_to_dot,
    dot_to_base64svg,
    update_bpmn_dot,
    load_execution_tree,
    set_actual_execution,
    execute_decisions,
    get_simulation_data,
    preview_petri_net_svg,
)
from gui.src.model.execution_tree import get_prev_execution_node
from gui.src.env import EXPRESSION

logger = logging.getLogger(__name__)


def reset_simulation_logic(bpmn_store, sim_store, bound_store):
    """
    Reset simulation when expression changes.
    Returns: simulation-store data or no_update
    """
    if not bpmn_store:
        return no_update
    
    current_expr = bpmn_store.get(EXPRESSION)
    saved_expr = sim_store.get("expression") if sim_store else None
    
    if current_expr == saved_expr:
        return no_update

    if not current_expr:
        return {"expression": current_expr}

    logger.debug(f"Simulation reset: expression changed")
    data = get_simulation_data(bpmn_store, bound_store)
    data["expression"] = current_expr
    return data


def step_simulation_logic(step, bpmn_store, gateway_values, sim_data, 
                          bpmn_svg_store, petri_svg_store, time_step, bound_store):
    """
    Step simulation forward or backward.
    
    Args:
        step: -1 for back, 1 for forward, 0 for no change
        
    Returns: (simulation_data, bpmn_svg, petri_svg)
    """
    if time_step is None or time_step <= 0:
        time_step = 1.0

    if step == -1:
        # Go back
        execution_tree, actual_execution = load_execution_tree(bpmn_store)
        prev_exec_node = get_prev_execution_node(execution_tree, actual_execution)
        if prev_exec_node is None:
            return sim_data, bpmn_svg_store, petri_svg_store

        set_actual_execution(bpmn_store, prev_exec_node['id'])
        bpmn_dot = bpmn_snapshot_to_dot(bpmn_store)
        dot_svg = dot_to_base64svg(bpmn_dot)
        update_bpmn_dot(bpmn_store, dot_svg)
        petri_svg = preview_petri_net_svg(bpmn_store)

        data = get_simulation_data(bpmn_store, bound_store)
        data["expression"] = bpmn_store.get(EXPRESSION)
        return data, dot_svg, petri_svg
        
    elif step == 1:
        # Go forward
        new_sim_data, petri_svg = execute_decisions(
            bpmn_store, gateway_values, time_step=time_step, bound_store=bound_store
        )
        bpmn_dot = bpmn_snapshot_to_dot(bpmn_store)
        dot_svg = dot_to_base64svg(bpmn_dot)
        update_bpmn_dot(bpmn_store, dot_svg)
        new_sim_data["expression"] = bpmn_store.get(EXPRESSION)
        return new_sim_data, dot_svg, petri_svg
    
    return sim_data, bpmn_svg_store, petri_svg_store


def refresh_petri_logic(view_mode, bpmn_store):
    """Refresh Petri net SVG when switching to Petri view."""
    if view_mode != "petri" or not bpmn_store or bpmn_store.get(EXPRESSION, "") == "":
        return no_update
    return preview_petri_net_svg(bpmn_store)
