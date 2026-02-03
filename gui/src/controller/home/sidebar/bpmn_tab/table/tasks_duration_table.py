import dash
from dash import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from gui.src.env import DURATIONS
from gui.src.model.etl import load_bpmn_dot


def register_task_durations_callbacks(tasks_callbacks):
	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output({"type": "bpmn-svg-store", "index": "main"}, "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'min-duration', 'index': ALL}, 'value'),
		Input({'type': 'max-duration', 'index': ALL}, 'value'),
		State({'type': 'min-duration', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_durations(min_values, max_values, ids, bpmn_store):
		for min_v, max_v, id_obj in zip(min_values, max_values, ids):
			task = id_obj['index']
			bpmn_store[DURATIONS][task] = [min_v or 0, max_v or 1]

		try:
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

		return bpmn_store, bpmn_dot, ''