import dash
from dash import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
from gui.src.model.etl import load_bpmn_dot
from gui.src.env import IMPACTS


def register_task_impacts_callbacks(tasks_callbacks):
	"""Register callbacks for task impact value updates.
	
	Bug #5 Note: We use MATCH pattern with impact-prefix filtering instead of
	a plain ALL pattern to avoid firing on unrelated pattern-matched inputs.
	The callback still uses ALL but filters by type prefix in the handler.
	"""
	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output({"type": "bpmn-svg-store", "index": "main"}, "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		# Bug #5: Keep ALL pattern but document why - Dash doesn't support regex in patterns
		# The filtering happens inside the callback via id_type.startswith('impact-')
		Input({'type': ALL, 'index': ALL}, 'value'),
		State({'type': ALL, 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_impacts(values, ids, bpmn_store):
		"""Update impact values in bpmn-store.
		
		Only processes inputs where type starts with 'impact-'.
		Other pattern-matched inputs are ignored.
		"""
		if not bpmn_store or IMPACTS not in bpmn_store:
			raise dash.exceptions.PreventUpdate
		
		updated = False
		for value, id_obj in zip(values, ids):
			id_type = id_obj.get('type', '')
			# Only process impact-related inputs (Bug #5 filter)
			if not id_type.startswith('impact-'):
				continue
				
			impact_name = id_type.replace('impact-', '')
			task = id_obj['index']

			if task not in bpmn_store[IMPACTS]:
				bpmn_store[IMPACTS][task] = {}
			
			try:
				new_value = float(value) if value is not None else 0.0
			except (ValueError, TypeError):
				new_value = 0.0
				
			if bpmn_store[IMPACTS][task].get(impact_name) != new_value:
				bpmn_store[IMPACTS][task][impact_name] = new_value
				updated = True

		if not updated:
			raise dash.exceptions.PreventUpdate

		try:
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

		return bpmn_store, bpmn_dot, ''

