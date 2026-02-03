"""
Bound Actions Module
Handles bound-store updates from user input.
"""
import dash
from dash import no_update
from gui.src.env import BOUND, IMPACTS_NAMES


def update_bound_logic(trigger_id, values, ids, bound_store):
    """
    Update a single bound value from user input.
    
    Returns: bound_store or PreventUpdate
    """
    if not values or not ids:
        return no_update
    
    # Find the triggered value
    t_type = trigger_id.get('type')
    t_index = trigger_id.get('index')
    
    if t_type != 'bound-input':
        return no_update
    
    # Find the matching value
    for value, id_obj in zip(values, ids):
        if id_obj.get('index') == t_index:
            try:
                new_val = float(value)
                if bound_store[BOUND].get(t_index) != new_val:
                    bound_store[BOUND][t_index] = new_val
                    return bound_store
            except (ValueError, TypeError):
                pass
    
    return no_update


def update_bound_from_selection_logic(selected_bound, bound_store, bpmn_store):
    """
    Update bounds from strategy table selection (guaranteed or possible_min).
    
    Returns: bound_store or PreventUpdate
    """
    if not selected_bound:
        return no_update
    
    for name, value in zip(sorted(bpmn_store[IMPACTS_NAMES]), selected_bound):
        bound_store[BOUND][name] = float(value)
    
    return bound_store
