"""
Upload Actions Module
Handles BPMN JSON file upload and validation.
"""
import base64
import json
import dash
from dash import no_update
import dash_bootstrap_components as dbc
from gui.src.env import EXPRESSION, IMPACTS, IMPACTS_NAMES, SESE_PARSER, extract_nodes
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.model.bpmn import validate_bpmn_dict
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.model.etl import reset_simulation_state


def upload_json_bpmn_logic(contents, filename, bound_store):
    """
    Process uploaded JSON BPMN file.
    
    Returns tuple of 12 values:
    (bpmn, bound, svg, petri, sim, impacts_tbl, durations_tbl, 
     choices_tbl, natures_tbl, loops_tbl, expression_value, alert)
    """
    NO_UPDATES = (no_update,) * 12
    
    if not contents:
        return NO_UPDATES
    
    def error_alert(msg):
        return (no_update,) * 11 + (dbc.Alert(msg, color="danger", dismissable=True),)

    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string).decode("utf-8")
        data = json.loads(decoded)

        new_bpmn = validate_bpmn_dict(data.get("bpmn", {}))

        if EXPRESSION not in new_bpmn:
            return error_alert("Missing 'expression' in BPMN")

        new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
        if new_bpmn[EXPRESSION] == '':
            return error_alert("Empty expression in BPMN")

        SESE_PARSER.parse(new_bpmn[EXPRESSION])
        tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(new_bpmn[EXPRESSION]))

        task_impacts = create_tasks_impacts_table(new_bpmn, tasks)
        task_durations = create_tasks_duration_table(new_bpmn, tasks)
        choice_table = create_choices_table(new_bpmn, choices)
        nature_table = create_natures_table(new_bpmn, natures)
        loop_table = create_loops_table(new_bpmn, loops)

        try:
            updated_bound_store = sync_bound_store_from_bpmn(new_bpmn, bound_store)
            bpmn_dot, petri_svg, sim_data = reset_simulation_state(new_bpmn, updated_bound_store)
            
            return (
                new_bpmn, updated_bound_store, bpmn_dot, petri_svg, sim_data,
                task_impacts, task_durations, choice_table, nature_table, loop_table,
                new_bpmn[EXPRESSION],
                dbc.Alert(f"{filename} uploaded successfully", color="success", dismissable=True)
            )
        except Exception as exception:
            return error_alert(f"Processing error: {str(exception)}")

    except Exception as e:
        return error_alert(f"Upload error: {e}")
