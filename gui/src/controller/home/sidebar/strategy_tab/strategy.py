import requests
from dash import Input, Output, State, html
from gui.src.controller.home.sidebar.strategy_tab.table.update_advaced_table import register_advance_table_callbacks
from gui.src.model.etl import load_strategy
from gui.src.env import IMPACTS_NAMES
import dash

from gui.src.view.home.sidebar.strategy_tab.strategy_result import strategy_results
import dash_bootstrap_components as dbc

def register_strategy_callbacks(strategy_callback):
	register_advance_table_callbacks(strategy_callback)

	# ------------------------------------------------------------------
	# NOTE: find_strategy callback migrated to store_manager.py
	# Logic now in gui/src/model/actions/strategy_actions.py
	# ------------------------------------------------------------------

