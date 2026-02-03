import base64
import json
import dash
from dash import Input, Output, State, no_update
import dash_bootstrap_components as dbc

from gui.src.env import EXPRESSION, IMPACTS, IMPACTS_NAMES
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.model.bpmn import validate_bpmn_dict
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.model.etl import reset_simulation_state
from gui.src.env import SESE_PARSER, extract_nodes


def register_upload_callbacks(callback):
    # ------------------------------------------------------------------
    # NOTE: upload_json_bpmn callback migrated to store_manager.py
    # Logic now in gui/src/model/actions/upload_actions.py
    # ------------------------------------------------------------------
    pass

