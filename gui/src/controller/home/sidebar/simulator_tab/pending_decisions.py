import random

from dash import Input, Output, State, ctx, no_update
from dash.dependencies import ALL

from gui.src.view.home.sidebar.simulator_tab.pending_decisions import (
    update_pending_decisions,
)


def register_pending_decision_callbacks(callback):
    @callback(
        Output("pending-decisions-body", "children"),
        Output("pending-decisions-card-container", "style"),
        Input("simulation-store", "data"),
        prevent_initial_call=False,
    )
    def populate_pending_decisions(simulator_data):
        if not simulator_data:
            return [], {"display": "none"}

        gateway_decisions = simulator_data.get("gateway_decisions") or {}
        if not gateway_decisions:
            return [], {"display": "none"}

        return update_pending_decisions(gateway_decisions), {}

    @callback(
        Output({"type": "gateway", "id": ALL}, "value"),
        Input({"type": "random-button", "id": ALL}, "n_clicks"),
        Input("global-random", "n_clicks"),
        State({"type": "gateway", "id": ALL}, "id"),
        State("simulation-store", "data"),
        prevent_initial_call=True
    )
    def update_random_decisions(individual_clicks, global_click, gateway_ids, sim_data):
        triggered = ctx.triggered_id
        if not sim_data or not sim_data.get("gateway_decisions"):
            return [no_update] * len(gateway_ids or [])

        result = []

        for i, gw_obj in enumerate(gateway_ids):
            gw = gw_obj["id"]
            if triggered == {"type": "random-button", "id": gw} or triggered == "global-random":
                options = []
                weights = []
                for opt, val in sim_data["gateway_decisions"][gw].items():
                    if opt == "__explainer__":
                        continue
                    options.append(val["transition_id"])
                    weights.append(val["probability"])
                
                if options:
                    result.append(random.choices(options, weights=weights)[0])
                else:
                    result.append(no_update)
            else:
                result.append(no_update)

        return result
