import json
from urllib.parse import parse_qs

import dash
from dash import Input, Output, State, no_update
import dash_bootstrap_components as dbc

from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.env import BOUND, EXPRESSION, SESE_PARSER, extract_nodes
from gui.src.example_registry import EXAMPLE_PATHS
from gui.src.model.bpmn import validate_bpmn_dict
from gui.src.model.etl import load_bpmn_dot
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table


def register_example_load_callbacks(callback):
	# ------------------------------------------------------------------
	# NOTE: load_example_from_query callback migrated to store_manager.py
	# Logic now in gui/src/model/actions/example_load_actions.py
	# ------------------------------------------------------------------
	pass

