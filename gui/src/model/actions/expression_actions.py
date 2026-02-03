"""
Expression Actions Module
Handles BPMN expression evaluation - the PRIMARY generator for BPMN models.
"""
import dash
import dash_bootstrap_components as dbc
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.model.etl import reset_simulation_state
from gui.src.env import EXPRESSION, SESE_PARSER, extract_nodes, IMPACTS_NAMES, BOUND, IMPACTS
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table


def evaluate_expression_logic(current_expression, bpmn_store, bound_store):
    """
    Evaluates a BPMN expression and generates the complete model.
    
    This is the PRIMARY BPMN generator. Returns tuple of 11 values:
    (bpmn_store, bpmn_svg, petri_svg, simulation_data, bound_store, alert,
     impacts_table, durations_table, choices_table, natures_table, loops_table)
    """
    NO_UPDATE = dash.no_update
    
    # Default no-update values
    alert = ''
    tasks_impacts_table = NO_UPDATE
    tasks_duration_table = NO_UPDATE
    choices_table = NO_UPDATE
    natures_table = NO_UPDATE
    loops_table = NO_UPDATE

    if current_expression is None:
        return (NO_UPDATE,) * 11

    # Clean expression
    current_expression = current_expression.replace("\n", "").replace("\t", "").strip().replace(" ", "")
    
    if current_expression == '':
        return (
            bpmn_store, NO_UPDATE, NO_UPDATE, NO_UPDATE, 
            sync_bound_store_from_bpmn(bpmn_store, bound_store),
            dbc.Alert("The expression is empty", color="warning", dismissable=True),
            tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
        )

    # Parse if expression changed
    if current_expression != bpmn_store.get(EXPRESSION, ''):
        try:
            SESE_PARSER.parse(current_expression)
        except Exception as e:
            return (
                NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE,
                dbc.Alert(f"Parsing error: {str(e)}", color="danger", dismissable=True),
                tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
            )
        bpmn_store[EXPRESSION] = current_expression

    if bpmn_store[EXPRESSION] == '':
        return (
            NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE,
            sync_bound_store_from_bpmn(bpmn_store, bound_store),
            alert, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
        )

    # Extract nodes from expression
    try:
        tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
        # print(f"DEBUG: Extracted Tasks: {tasks}")
    except Exception as e:
        print(f"ERROR: Extraction Error: {e}")
        return (NO_UPDATE,) * 11

    # Initialize default impact if none exist
    if not bpmn_store.get(IMPACTS_NAMES):
        # print("DEBUG: Initializing default impacts")
        impacts_names = 'kWh'
        bound_store[BOUND][impacts_names] = 0.0
        bpmn_store[IMPACTS_NAMES] = [impacts_names]

    # Create tables
    # print(f"DEBUG: Creating tables for tasks: {tasks}")
    tasks_impacts_table = create_tasks_impacts_table(bpmn_store, tasks)
    # print(f"DEBUG: Created Impacts Table type: {type(tasks_impacts_table)}")
    tasks_duration_table = create_tasks_duration_table(bpmn_store, tasks)
    choices_table = create_choices_table(bpmn_store, choices)
    natures_table = create_natures_table(bpmn_store, natures)
    loops_table = create_loops_table(bpmn_store, loops)

    try:
        updated_bound_store = sync_bound_store_from_bpmn(bpmn_store, bound_store)
        bpmn_dot, petri_svg, sim_data = reset_simulation_state(bpmn_store, updated_bound_store)
        
        return (
            bpmn_store, bpmn_dot, petri_svg, sim_data, updated_bound_store,
            alert, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
        )
    except Exception as exception:
        alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)
        return (
            bpmn_store, NO_UPDATE, NO_UPDATE, NO_UPDATE,
            sync_bound_store_from_bpmn(bpmn_store, bound_store),
            alert, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
        )
