from gui.src.env import PROBABILITIES, LOOP_PROBABILITY, LOOP_ROUND, DELAYS
from gui.src.model.etl import load_bpmn_dot
import dash_bootstrap_components as dbc
import dash

def update_gateway_logic(id_obj, value, bpmn_store):
    """
    Updates gateway properties (Delay, Probability, Loop).
    """
    g_type = id_obj.get('type')
    node_id = id_obj['index']
    
    updated = False
    
    if g_type == 'choice-delay':
        bpmn_store[DELAYS][node_id] = value
        updated = True
    elif g_type == 'nature-prob':
        bpmn_store[PROBABILITIES][node_id] = float(value)
        updated = True
    elif g_type == 'loop-prob':
        bpmn_store[LOOP_PROBABILITY][node_id] = float(value)
        updated = True
    elif g_type == 'loop-round':
        bpmn_store[LOOP_ROUND][node_id] = int(value)
        updated = True
        
    if not updated:
        return dash.no_update

    try:
        bpmn_dot = load_bpmn_dot(bpmn_store)
        return bpmn_store, bpmn_dot, ''
    except Exception as exception:
        alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)
        return dash.no_update, dash.no_update, alert
