from dash import Input, Output, State
from gui.src.env import IMPACTS_NAMES

from gui.src.view.home.sidebar.simulator_tab.status_info import (
    update_status_info,
    update_task_status_table,
)


def register_status_info_callbacks(callback):
    @callback(
        Output("status-info-content", "children"),
        Output("task-status-content", "children"),
        Input("simulation-store", "data"),
        State("bpmn-store", "data"),
        prevent_initial_call=False,
    )
    def update(data, bpmn_data):
        if data is None:
            data = {}
        
        impacts = data.get("impacts", {})
        expected_values = data.get("expected_impacts", {})
        time = data.get("execution_time", 0.0)
        probability = data.get("probability", 1.0)
        task_statuses = data.get("task_statuses", {})
        
        # If impacts are empty (initial state), populate with 0 for all defined names
        if not impacts and bpmn_data and IMPACTS_NAMES in bpmn_data:
            for name in bpmn_data[IMPACTS_NAMES]:
                impacts[name] = 0.0
                expected_values[name] = 0.0

        return (
            update_status_info(impacts, expected_values, time, probability),
            update_task_status_table(task_statuses)
        )
