import logging
from dash import Input, Output, State, ctx, ALL, no_update

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


def register_simulator_callbacks(callback):
    @callback(
        Output("btn-back", "disabled"),
        Output("btn-forward", "disabled"),
        Input("bpmn-store", "data"),
    )
    def toggle_simulation_controls(bpmn_store):
        is_disabled = not bpmn_store or bpmn_store.get(EXPRESSION, "") == ""
        return is_disabled, is_disabled

    # ------------------------------------------------------------------
    # NOTE: The following callbacks have been migrated to store_manager.py
    # Logic now in gui/src/model/actions/simulation_actions.py
    # - reset_simulation_data
    # - run_simulation_on_step
    # - refresh_petri_on_view
    # ------------------------------------------------------------------

