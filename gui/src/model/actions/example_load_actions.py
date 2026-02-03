"""
Example Load Actions Module
Handles loading BPMN examples from files.
"""
import json
from urllib.parse import parse_qs
from dash import no_update
import dash_bootstrap_components as dbc
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.env import BOUND, EXPRESSION, SESE_PARSER, extract_nodes
from gui.src.example_registry import EXAMPLE_PATHS
from gui.src.model.bpmn import validate_bpmn_dict
from gui.src.model.etl import load_bpmn_dot
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table


def load_example_logic(search, bound_store):
    """
    Load BPMN example from URL query parameter.
    
    Returns tuple of 10 values:
    (bpmn, bound, svg, impacts_tbl, durations_tbl, choices_tbl, natures_tbl, loops_tbl, expression_val, alert)
    """
    NO_UPDATES = (no_update,) * 10
    
    def error_alert(msg, color="danger"):
        return (no_update,) * 9 + (dbc.Alert(msg, color=color, dismissable=True),)

    if not search:
        return NO_UPDATES

    query = parse_qs(search.lstrip("?"))
    example_keys = query.get("example")
    if not example_keys:
        return NO_UPDATES

    example_key = example_keys[0]
    example_path = EXAMPLE_PATHS.get(example_key)
    if not example_path:
        return error_alert(f"Unknown example '{example_key}'.", color="warning")

    try:
        with open(example_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        new_bpmn = validate_bpmn_dict(data.get("bpmn", {}))
        if EXPRESSION not in new_bpmn:
            return error_alert("Missing 'expression' in BPMN")

        new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
        if new_bpmn[EXPRESSION] == "":
            return error_alert("Empty expression in BPMN")

        SESE_PARSER.parse(new_bpmn[EXPRESSION])
        tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(new_bpmn[EXPRESSION]))

        task_impacts = create_tasks_impacts_table(new_bpmn, tasks)
        task_durations = create_tasks_duration_table(new_bpmn, tasks)
        choice_table = create_choices_table(new_bpmn, choices)
        nature_table = create_natures_table(new_bpmn, natures)
        loop_table = create_loops_table(new_bpmn, loops)

        if not bound_store or BOUND not in bound_store:
            bound_store = {BOUND: {}}
            
        updated_bound_store = sync_bound_store_from_bpmn(new_bpmn, bound_store)
        bpmn_dot, petri_svg, sim_data = reset_simulation_state(new_bpmn, updated_bound_store)

        return (
            new_bpmn,
            updated_bound_store,
            bpmn_dot,
            petri_svg, 
            sim_data,
            task_impacts,
            task_durations,
            choice_table,
            nature_table,
            loop_table,
            new_bpmn[EXPRESSION],
            dbc.Alert("Example loaded successfully", color="success", dismissable=True),
        )

    except Exception as exception:
        return error_alert(f"Example load error: {exception}")
