from gui.src.env import IMPACTS
from gui.src.model.etl import load_bpmn_dot
import dash_bootstrap_components as dbc
import dash

def update_impacts_logic(id_obj, value, bpmn_store):
    """
    Updates a single impact value. 
    Args:
        id_obj: dict with 'type' and 'index'. type should be 'impact-<name>'.
        value: the new float value.
        bpmn_store: method mutates this store.
    """
    id_type = id_obj.get('type', '')
    if not id_type.startswith('impact-'):
        return dash.no_update, dash.no_update, dash.no_update

    impact_name = id_type.replace('impact-', '')
    task = id_obj['index']

    if IMPACTS not in bpmn_store:
         bpmn_store[IMPACTS] = {}

    if task not in bpmn_store[IMPACTS]:
        bpmn_store[IMPACTS][task] = {}

    try:
        new_value = float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        new_value = 0.0

    current = bpmn_store[IMPACTS][task].get(impact_name)
    if current == new_value:
        return dash.no_update, dash.no_update, dash.no_update

    bpmn_store[IMPACTS][task][impact_name] = new_value

    try:
        bpmn_dot = load_bpmn_dot(bpmn_store)
        return bpmn_store, bpmn_dot, ''
    except Exception as exception:
        alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)
        return dash.no_update, dash.no_update, alert
