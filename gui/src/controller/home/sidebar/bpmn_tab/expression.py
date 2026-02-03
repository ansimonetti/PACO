import dash
from dash import Output, Input, State
import dash_bootstrap_components as dbc
from dash import ctx
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.model.etl import reset_simulation_state
from gui.src.env import EXPRESSION, SESE_PARSER, extract_nodes, IMPACTS_NAMES, BOUND, IMPACTS
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table


def register_expression_callbacks(expression_callbacks):
    # ------------------------------------------------------------------
    # NOTE: evaluate_expression callback has been migrated to store_manager.py
    # The logic is now in gui/src/model/actions/expression_actions.py
    # StoreManager is now the SOLE writer for bpmn-store.
    # ------------------------------------------------------------------
    # @expression_callbacks(
    #     Output('bpmn-store', 'data'),
    #     ... (see store_manager.py for full implementation)
    # )
    # def evaluate_expression(...): ...
    # ------------------------------------------------------------------

    # Keep sync callback as utility (reads from store, doesn't write to main stores)


    @expression_callbacks(
        Output('expression-bpmn', 'value', allow_duplicate=True),
        Input('bpmn-store', 'data'),
        State('expression-bpmn', 'value'),
        prevent_initial_call='initial_duplicate'
    )
    def sync_input_with_store(store_data, current_value):
        if not current_value:#if empty
            return store_data[EXPRESSION]
        return dash.no_update
