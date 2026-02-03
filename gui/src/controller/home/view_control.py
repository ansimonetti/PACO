from dash import Input, Output, State, no_update
import dash

def register_view_callbacks(view_callbacks):
    @view_callbacks(
        Output("view-mode", "data"),
        Output("view-toggle-btn", "children"),
        Input("view-toggle-btn", "n_clicks"),
        State("view-mode", "data"),
        prevent_initial_call=True
    )
    def toggle_view(n_clicks, current_mode):
        if not n_clicks:
            return no_update, no_update
        
        new_mode = "petri" if current_mode == "bpmn" else "bpmn"
        text = "Switch to BPMN" if new_mode == "petri" else "Switch to PetriNet"
        return new_mode, text

    @view_callbacks(
        Output("bpmn-container", "style"),
        Output("petri-container", "style"),
        Input("view-mode", "data")
    )
    def update_visibility(view_mode):
        if view_mode == "petri":
            return {"display": "none", "height": "100%", "width": "100%"}, {"display": "block", "height": "100%", "width": "100%"}
        return {"display": "block", "height": "100%", "width": "100%"}, {"display": "none", "height": "100%", "width": "100%"}
