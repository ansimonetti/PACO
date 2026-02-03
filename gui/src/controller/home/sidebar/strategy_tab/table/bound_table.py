import dash
from dash import Input, Output, State, ALL, ctx
from gui.src.env import IMPACTS_NAMES, BOUND, EXPRESSION
from gui.src.view.home.sidebar.strategy_tab.table.bound_table import get_bound_table
from dash import html


def sync_bound_store_from_bpmn(bpmn_store, bound_store):
	"""Synchronize bound-store with bpmn-store impact names.
	
	This function:
	- Adds default bounds (1.0) for new impact names
	- Removes bounds for impact names that no longer exist (Bug #7 fix)
	- Preserves existing user-set bound values (Bug #2: non-destructive)
	"""
	if not bpmn_store or IMPACTS_NAMES not in bpmn_store:
		return bound_store
	
	if not bound_store or BOUND not in bound_store:
		bound_store = {BOUND: {}}
	
	current_impacts = set(bpmn_store[IMPACTS_NAMES])
	
	# Add new impacts with default value
	for name in current_impacts:
		if name not in bound_store[BOUND]:
			bound_store[BOUND][name] = 1.0
	
	# Remove obsolete impacts (Bug #7 fix)
	obsolete_keys = set(bound_store[BOUND].keys()) - current_impacts
	for key in obsolete_keys:
		del bound_store[BOUND][key]

	return bound_store


def register_bound_callbacks(bound_callbacks):
	@bound_callbacks(
		Output("bound-table", "children"),
		Input("bound-store", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def regenerate_bound_table(bound_store, bpmn_store):
		# Bug #12 fix: safe dict access with .get()
		if not bpmn_store or bpmn_store.get(EXPRESSION, '') == '' or not bound_store or BOUND not in bound_store:
			return html.Div()

		return get_bound_table(bound_store, sorted(bpmn_store.get(IMPACTS_NAMES, [])))

	# ------------------------------------------------------------------
	# NOTE: The following callbacks have been migrated to store_manager.py
	# Logic now in gui/src/model/actions/bound_actions.py
	# - update_bounds
	# - update_bound_from_guaranteed
	# - update_bound_from_possible_min
	# ------------------------------------------------------------------


