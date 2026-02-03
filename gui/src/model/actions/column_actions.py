from gui.src.env import IMPACTS_NAMES, extract_nodes, SESE_PARSER, EXPRESSION, IMPACTS
from gui.src.model.etl import load_bpmn_dot
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
import dash_bootstrap_components as dbc
import dash

def add_impact_column_logic(new_impact_name, bpmn_store, bound_store):
    if not new_impact_name or new_impact_name.strip() == '':
        return dash.no_update

    new_impact_name = new_impact_name.strip()
    if new_impact_name in bpmn_store[IMPACTS_NAMES]:
        # Return alert
        return dash.no_update, dash.no_update, dash.no_update, dbc.Alert(f"Impact '{new_impact_name}' already exists.", color="warning", dismissable=True), dash.no_update

    bpmn_store[IMPACTS_NAMES].append(new_impact_name)

    tasks, _, _, _ = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
    for task in tasks:
        if new_impact_name not in bpmn_store[IMPACTS][task]:
            bpmn_store[IMPACTS][task][new_impact_name] = 0.0

    tasks_table = create_tasks_impacts_table(bpmn_store, tasks)
    
    try:
        bpmn_dot = load_bpmn_dot(bpmn_store)
        updated_bound = sync_bound_store_from_bpmn(bpmn_store, bound_store)
        return bpmn_store, bpmn_dot, updated_bound, '', tasks_table
    except Exception as exception:
         return dash.no_update, dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True), dash.no_update

def remove_impact_column_logic(id_obj, bpmn_store, bound_store):
    """
    Removes an impact column.
    Args:
        id_obj: dict containing 'index' which is the impact name.
    """
    impact_to_remove = id_obj['index']
    if impact_to_remove in bpmn_store[IMPACTS_NAMES]:
        bpmn_store[IMPACTS_NAMES].remove(impact_to_remove)
    else:
        return dash.no_update

    # Bug #7 fix is inherent in sync_bound_store_from_bpmn which is called here
    try:
        tasks, _, _, _ = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
        tasks_table = create_tasks_impacts_table(bpmn_store, tasks)
        bpmn_dot = load_bpmn_dot(bpmn_store)
        updated_bound = sync_bound_store_from_bpmn(bpmn_store, bound_store)
        
        return bpmn_store, bpmn_dot, updated_bound, '', tasks_table
    except Exception as exception:
        alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)
        return dash.no_update, dash.no_update, dash.no_update, alert, dash.no_update
