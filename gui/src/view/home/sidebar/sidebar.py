from dash import dcc, html

from gui.src.view.home.sidebar.bpmn_tab.tab import get_BPMN_CPI_tab
from gui.src.view.home.sidebar.llm_tab.tab import get_llm_tab
from gui.src.view.home.sidebar.simulator_tab.tab import get_simulator_tab
from gui.src.view.home.sidebar.strategy_tab.tab import get_strategy_tab


def get_sidebar():
    return html.Div(
        dcc.Tabs(
            id="bpmn-tabs",
            value="tab-bpmn",
            style={"display": "flex"},
            children=[
                get_BPMN_CPI_tab(),
                get_strategy_tab(),
                get_simulator_tab(),
                get_llm_tab(),
            ],
        ),
        id="sidebar-container",
        style={"height": "100%", "overflow": "auto"},
    )
