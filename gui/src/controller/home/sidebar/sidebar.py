from dash import Output, Input, State


def register_sidebar_callbacks(callback):

    @callback(
        Output("sidebar-visible", "data"),
        Output("sidebar-width", "data"),
        Input("toggle-sidebar", "n_clicks"),
        State("sidebar-visible", "data"),
        State("sidebar-width", "data"),
        State("split-pane", "size"),
        prevent_initial_call=True
    )
    def toggle_sidebar(n, current_state, old_width, current_size):
        if current_state:
            return False, current_size  # save width before hiding
        else:
            return True, old_width      # restore previous width

    @callback(
        Output("split-pane", "size"),
        Input("sidebar-visible", "data"),
        State("sidebar-width", "data")
    )
    def update_split_pane_size(visible, width):
        return width if visible else 0

