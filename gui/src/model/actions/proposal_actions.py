"""
Proposal Actions Module
Handles logic for Accepting or Rejecting BPMN proposals.
"""
from dash import no_update
from gui.src.model.etl import reset_simulation_state
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import (
    create_choices_table,
    create_natures_table,
    create_loops_table,
)
from gui.src.env import (
    EXPRESSION,
    SESE_PARSER,
    extract_nodes,
    H,
    IMPACTS_NAMES,
    IMPACTS,
    DURATIONS,
    DELAYS,
    PROBABILITIES,
    LOOP_PROBABILITY,
    LOOP_ROUND,
)

def accept_proposal_logic(proposed_bpmn, history, bound_store):
    """
    Promote proposed BPMN to active BPMN, reset simulation, clear proposal.
    """
    if not proposed_bpmn or not history:
        return (no_update,) * 13

    # Ensure required BPMN fields exist before sim reset
    if EXPRESSION not in proposed_bpmn:
        return (no_update,) * 13

    proposed_bpmn.setdefault(H, 0)
    proposed_bpmn.setdefault(IMPACTS_NAMES, [])
    proposed_bpmn.setdefault(IMPACTS, {})
    proposed_bpmn.setdefault(DURATIONS, {})
    proposed_bpmn.setdefault(DELAYS, {})
    proposed_bpmn.setdefault(PROBABILITIES, {})
    proposed_bpmn.setdefault(LOOP_PROBABILITY, {})
    proposed_bpmn.setdefault(LOOP_ROUND, {})
    if not isinstance(proposed_bpmn.get(IMPACTS), dict):
        proposed_bpmn[IMPACTS] = {}
    if not isinstance(proposed_bpmn.get(DURATIONS), dict):
        proposed_bpmn[DURATIONS] = {}
    if not isinstance(proposed_bpmn.get(DELAYS), dict):
        proposed_bpmn[DELAYS] = {}
    if not isinstance(proposed_bpmn.get(PROBABILITIES), dict):
        proposed_bpmn[PROBABILITIES] = {}
    if not isinstance(proposed_bpmn.get(LOOP_PROBABILITY), dict):
        proposed_bpmn[LOOP_PROBABILITY] = {}
    if not isinstance(proposed_bpmn.get(LOOP_ROUND), dict):
        proposed_bpmn[LOOP_ROUND] = {}

    # Update history: remove buttons, add "Accepted" status
    new_history = [msg.copy() for msg in history]
    if new_history:
        last_msg = new_history[-1]
        if last_msg.get('is_proposal'):
            del last_msg['is_proposal']
            last_msg['text'] += "\n\nProposal Accepted"

    # Build required defaults before simulation
    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(proposed_bpmn[EXPRESSION]))

    if not proposed_bpmn.get(IMPACTS_NAMES):
        inferred_impacts = None
        impacts_val = proposed_bpmn.get(IMPACTS)
        if isinstance(impacts_val, dict) and impacts_val:
            for val in impacts_val.values():
                if isinstance(val, dict) and val:
                    inferred_impacts = list(val.keys())
                    break
                if isinstance(val, (list, tuple)) and val:
                    inferred_impacts = None
                    break
        proposed_bpmn[IMPACTS_NAMES] = inferred_impacts or ["kWh"]

    # Normalize impacts/durations shapes to avoid parser errors
    impacts_dict = proposed_bpmn[IMPACTS]
    for task, val in list(impacts_dict.items()):
        if isinstance(val, dict):
            continue
        if isinstance(val, (list, tuple)):
            impacts_dict[task] = {
                name: float(val[idx]) if idx < len(val) else 0.0
                for idx, name in enumerate(proposed_bpmn[IMPACTS_NAMES])
            }
        else:
            impacts_dict[task] = {}

    durations_dict = proposed_bpmn[DURATIONS]
    for task, val in list(durations_dict.items()):
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            durations_dict[task] = (val[0], val[1])
        else:
            durations_dict[task] = (0, 1)

    tasks_impacts_table = create_tasks_impacts_table(proposed_bpmn, tasks)
    tasks_duration_table = create_tasks_duration_table(proposed_bpmn, tasks)
    choices_table = create_choices_table(proposed_bpmn, choices)
    natures_table = create_natures_table(proposed_bpmn, natures)
    loops_table = create_loops_table(proposed_bpmn, loops)

    updated_bound_store = sync_bound_store_from_bpmn(proposed_bpmn, bound_store)

    # Generate all artifacts (Sim, SVG, Tables)
    bpmn_dot, petri_svg, sim_data = reset_simulation_state(proposed_bpmn, updated_bound_store)

    return (
        None,           # proposed-bpmn-store (Clear it)
        no_update,      # pending-message
        proposed_bpmn,  # bpmn-store (Update)
        updated_bound_store, # bound-store
        bpmn_dot,       # bpmn-svg
        petri_svg,      # petri-svg
        sim_data,       # sim-store
        tasks_impacts_table,
        tasks_duration_table,
        choices_table,
        natures_table,
        loops_table,
        new_history     # chat-history
    )

def reject_proposal_logic(history):
    """
    Clear proposal, update history.
    """
    if not history:
        return (no_update,) * 13

    new_history = [msg.copy() for msg in history]
    if new_history:
        last_msg = new_history[-1]
        if last_msg.get('is_proposal'):
            del last_msg['is_proposal']
            last_msg['text'] += "\n\nProposal Rejected"

    return (
        None,           # proposed-bpmn-store (Clear it)
        no_update,      # pending-message
        no_update,      # bpmn-store
        no_update,      # bound-store
        no_update,      # bpmn-svg
        no_update,      # petri-svg
        no_update,      # sim-store
        no_update, no_update, no_update, no_update, no_update, # Tables
        new_history     # chat-history
    )
