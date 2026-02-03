"""
Strategy Actions Module
Handles strategy computation logic.
"""
import dash
from dash import html, no_update
import dash_bootstrap_components as dbc
import requests
from gui.src.model.etl import load_strategy
from gui.src.env import IMPACTS_NAMES
from gui.src.view.home.sidebar.strategy_tab.strategy_result import strategy_results


def find_strategy_logic(bpmn_store, bound_store):
    """
    Compute strategy for the given BPMN and bounds.
    
    Returns tuple of 2 values:
    (strategy_output, alert)
    
    Note: sort_store_guaranteed and sort_store_possible_min are managed
    by update_advaced_table.py's callbacks, not by StoreManager.
    """
    try:
        alert = ''
        try:
            result, expected_impacts, guaranteed_bounds, possible_min_solution, bdds = load_strategy(bpmn_store, bound_store)
        except ValueError as e:
            alert = dbc.Alert(str(e), color="warning", dismissable=True)
            return html.Div(), alert

        results = strategy_results(
            result, expected_impacts,
            guaranteed_bounds, possible_min_solution, bdds,
            sorted(bpmn_store[IMPACTS_NAMES]))

        return results, alert, guaranteed_bounds, possible_min_solution

    except requests.exceptions.HTTPError as e:
        alert = dbc.Alert(f"HTTP Error ({e})", color="danger", dismissable=True)
        return html.Div(), alert, [], []
