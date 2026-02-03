import dash
from dash import Output, Input, ALL, State, ctx
from gui.src.env import IMPACTS_NAMES
from gui.src.view.home.sidebar.strategy_tab.table.create_advance_table import render_table


def register_advance_table_callbacks(table_callback):
	@table_callback(
		Output("guaranteed-table", "children"),
		Output("sort_store_guaranteed", "data", allow_duplicate=True),
		Input({"type": "sort-header", "column": ALL, "table": "guaranteed"}, "n_clicks"),
		State("sort_store_guaranteed", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def update_guaranteed_table(_, store, bpmn_store):
		if not ctx.triggered_id or ctx.triggered_id.get("table") != "guaranteed":
			raise dash.exceptions.PreventUpdate

		sort_by = ctx.triggered_id["column"]
		
		store = store or {}
		current = store.get("sort_by")
		order = store.get("sort_order", "asc")
		data = store.get("data", [])
		
		new_order = "desc" if sort_by == current and order == "asc" else "asc"
		
		g = { "sort_by": sort_by, "sort_order": new_order, "data": data}

		return render_table(
			sorted(bpmn_store.get(IMPACTS_NAMES, [])), data,
			include_button=True, button_prefix="selected_bound",
			sort_by=sort_by, sort_order=new_order, table="guaranteed"
		), g

	@table_callback(
		Output("possible_min-table", "children"),
		Output("sort_store_possible_min", "data", allow_duplicate=True),
		Input({"type": "sort-header", "column": ALL, "table": "possible_min"}, "n_clicks"),
		State("sort_store_possible_min", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def update_possible_min_table(_, store, bpmn_store):
		if not ctx.triggered_id or ctx.triggered_id.get("table") != "possible_min":
			raise dash.exceptions.PreventUpdate

		sort_by = ctx.triggered_id["column"]
		
		store = store or {}
		current = store.get("sort_by")
		order = store.get("sort_order", "asc")
		data = store.get("data", [])

		new_order = "desc" if sort_by == current and order == "asc" else "asc"

		p = { "sort_by": sort_by, "sort_order": new_order, "data": data}

		return render_table(
			sorted(bpmn_store.get(IMPACTS_NAMES, [])), data,
			include_button=True, button_prefix="selected_bound",
			sort_by=sort_by, sort_order=new_order, table="possible_min"
		), p

