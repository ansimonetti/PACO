import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_split_pane import DashSplitPane
from gui.src.controller.home.sidebar.bpmn_tab.download import register_download_callbacks
from gui.src.controller.home.sidebar.bpmn_tab.example_load import register_example_load_callbacks
from gui.src.controller.home.sidebar.bpmn_tab.table.tasks_impacts_names import register_task_impacts_names_callbacks
from gui.src.controller.home.sidebar.bpmn_tab.upload import register_upload_callbacks
from gui.src.controller.home.sidebar.llm_tab.chat import register_llm_callbacks
from gui.src.controller.home.sidebar.sidebar import register_sidebar_callbacks
from gui.src.controller.home.sidebar.simulator_tab.pending_decisions import register_pending_decision_callbacks
from gui.src.controller.home.sidebar.simulator_tab.simulate_control import register_simulator_callbacks
from gui.src.controller.home.sidebar.simulator_tab.status_info import register_status_info_callbacks
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import register_bound_callbacks
from gui.src.env import DELAYS, DURATIONS, H, IMPACTS, EXPRESSION, IMPACTS_NAMES, PROBABILITIES, LOOP_ROUND, \
    LOOP_PROBABILITY, BOUND
from gui.src.controller.home.sidebar.bpmn_tab.expression import register_expression_callbacks
from gui.src.controller.home.sidebar.bpmn_tab.table.gateways_table import register_gateway_callbacks
from gui.src.controller.home.sidebar.bpmn_tab.table.tasks_impacts_table import register_task_impacts_callbacks
from gui.src.controller.home.sidebar.bpmn_tab.table.tasks_duration_table import register_task_durations_callbacks
from gui.src.controller.home.sidebar.strategy_tab.strategy import register_strategy_callbacks
from gui.src.view.home.sidebar.sidebar import get_sidebar
from gui.src.view.visualizer.RenderSVG import RenderSvg
from gui.src.controller.home.view_control import register_view_callbacks
from gui.src.controller.store_manager import register_store_manager_callbacks


def layout():
    sidebar_min_width = 450
    bpmn_visualizer = RenderSvg(type="bpmn-svg", index="main", zoom_min=0.1, zoom_max=5.5)
    petri_visualizer = RenderSvg(type="petri-svg", index="main", zoom_min=0.1, zoom_max=5.5)

    return html.Div([
        dcc.Store(id='bpmn-store', data={
            EXPRESSION: '',
            H: 0,
            IMPACTS: {},
            DURATIONS: {},
            IMPACTS_NAMES: [],
            DELAYS: {},
            PROBABILITIES: {},
            LOOP_PROBABILITY: {},
            LOOP_ROUND: {},
        }, storage_type='session'),
        dcc.Store(id='proposed-bpmn-store', data=None, storage_type='session'),
        dcc.Store(id={"type": "bpmn-svg-store", "index": "main"}, data="", storage_type='session'),
        dcc.Store(id={"type": "petri-svg-store", "index": "main"}, data="", storage_type='session'),
        dcc.Store(id="view-mode", data="bpmn", storage_type='session'),
        
        dcc.Store(id="sort_store_guaranteed", data={"sort_by": None, "sort_order": "asc", "data": []}, storage_type='session'),
        dcc.Store(id="sort_store_possible_min", data={"sort_by": None, "sort_order": "asc", "data": []}, storage_type='session'),

        dcc.Store(id='bound-store', data={BOUND: {}}, storage_type='session'),

        dcc.Store(id='chat-history', data=[], storage_type='session'),
        dcc.Store(id='pending-message', data=None, storage_type='session'),
        dcc.Store(id='reset-trigger', data=False, storage_type='session'),

        dcc.Store(id="sidebar-visible", data=True, storage_type='session'),
        dcc.Store(id="sidebar-width", data=sidebar_min_width, storage_type='session'),

        DashSplitPane(
            id="split-pane",
            split="vertical",
            resizerStyle={"width": "20px"},
            minSize=sidebar_min_width,
            size=sidebar_min_width,
            children=[
                get_sidebar(),
                html.Div([
                    dbc.Button("Switch to PetriNet", id="view-toggle-btn", size="sm", color="dark", style={
                        "position": "absolute",
                        "top": "1rem",
                        "left": "1rem",
                        "zIndex": 100,
                    }),
                    html.Div(bpmn_visualizer.get_visualizer(), id="bpmn-container", style={"height": "100%", "width": "100%"}),
                    html.Div(petri_visualizer.get_visualizer(), id="petri-container", style={"display": "none", "height": "100%", "width": "100%"})
                ], style={"position": "relative", "width": "100%", "height": "100%", "display": "flex", "flexDirection": "column"})
            ],
            style={"height": "calc(100vh - 60px)", "display": "flex", "flexDirection": "row"}

    )
    ])


RenderSvg.register_callbacks(dash.callback, "bpmn-svg")
RenderSvg.register_callbacks(dash.callback, "petri-svg")
RenderSvg.register_callbacks(dash.callback, "bdd")
# register_task_impacts_callbacks(dash.callback)
# register_task_durations_callbacks(dash.callback)
register_store_manager_callbacks(dash.callback)
# register_task_impacts_names_callbacks(dash.callback)
# register_gateway_callbacks(dash.callback)
register_expression_callbacks(dash.callback)
register_bound_callbacks(dash.callback)
register_strategy_callbacks(dash.callback)
register_sidebar_callbacks(dash.callback)
register_llm_callbacks(dash.callback, dash.clientside_callback)
register_upload_callbacks(dash.callback)
register_download_callbacks(dash.callback)
register_example_load_callbacks(dash.callback)

register_pending_decision_callbacks(dash.callback)
register_status_info_callbacks(dash.callback)
register_simulator_callbacks(dash.callback)
register_view_callbacks(dash.callback)
