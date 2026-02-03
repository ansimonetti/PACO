import dash
from dash import Input, Output, State, ALL

from gui.src.model.etl import load_bpmn_dot
from gui.src.env import PROBABILITIES, LOOP_PROBABILITY, LOOP_ROUND, DELAYS
import dash_bootstrap_components as dbc

def register_gateway_callbacks(gateway_callbacks):
	@gateway_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output({"type": "bpmn-svg-store", "index": "main"}, "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'choice-delay', 'index': ALL}, 'value'),
		State({'type': 'choice-delay', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_choices(values, ids, bpmn_store):
		for value, id_obj in zip(values, ids):
			bpmn_store[DELAYS][id_obj['index']] = value

		try:
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

		return bpmn_store, bpmn_dot, ''

	@gateway_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output({"type": "bpmn-svg-store", "index": "main"}, "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'nature-prob', 'index': ALL}, 'value'),
		State({'type': 'nature-prob', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_natures(values, ids, bpmn_store):
		for value, id_obj in zip(values, ids):
			bpmn_store[PROBABILITIES][id_obj['index']] = float(value)

		try:
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

		return bpmn_store, bpmn_dot, ''


	@gateway_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output({"type": "bpmn-svg-store", "index": "main"}, "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'loop-prob', 'index': ALL}, 'value'),
		Input({'type': 'loop-round', 'index': ALL}, 'value'),
		State({'type': 'loop-prob', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_loops(probs, rounds, ids, bpmn_store):
		for p, r, id_obj in zip(probs, rounds, ids):
			loop = id_obj['index']
			bpmn_store[LOOP_PROBABILITY][loop] = float(p)
			bpmn_store[LOOP_ROUND][loop] = r

		try:
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

		return bpmn_store, bpmn_dot, ''

