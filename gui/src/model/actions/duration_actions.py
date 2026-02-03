from gui.src.env import DURATIONS
from gui.src.model.etl import load_bpmn_dot
import dash_bootstrap_components as dbc
import dash

def update_durations_logic(min_values, max_values, ids, bpmn_store):
    """
    Updates the durations in the BPMN store based on table inputs.
    Returns: (bpmn_store, bpmn_dot, alert_message)
    """
    # If no inputs or any None, handle gracefully? 
    # The original loop implies lists.
    
    has_changes = False
    
    for min_v, max_v, id_obj in zip(min_values, max_values, ids):
        task = id_obj['index']
        # Original logic: [min_v or 0, max_v or 1]
        new_val = [min_v or 0, max_v or 1]
        
        # Check if actually changed to avoid unnecessary heavy DOT reload?
        if bpmn_store.get(DURATIONS, {}).get(task) != new_val:
             if DURATIONS not in bpmn_store:
                 bpmn_store[DURATIONS] = {}
             bpmn_store[DURATIONS][task] = new_val
             has_changes = True

    if not has_changes:
        # Return strict No Update to prevent cycles if nothing changed
        return dash.no_update, dash.no_update, dash.no_update

    try:
        bpmn_dot = load_bpmn_dot(bpmn_store)
        return bpmn_store, bpmn_dot, ''
    except Exception as exception:
        alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)
        return dash.no_update, dash.no_update, alert
