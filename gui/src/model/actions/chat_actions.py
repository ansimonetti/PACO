"""
Chat Actions Module
Handles LLM response processing logic, separated from Dash callbacks.
"""
import dash
from gui.src.model.etl import load_bpmn_dot, reset_simulation_state
from gui.src.model.llm import llm_response
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
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


def resolve_llm_response(pending_id, history, bpmn_store, bound_store, 
                         provider, model_choice, custom_model, api_key):
    """
    Process LLM response and update BPMN model.
    
    Note (Bug #3 - By Design): The LLM generates a complete new BPMN model.
    This will REPLACE the current bpmn-store entirely, not merge with it.
    
    Returns tuple of 10 values:
    (chat_history, pending_message, bpmn_store, bound_store, bpmn_svg,
     impacts_table, durations_table, choices_table, natures_table, loops_table)
    """
    NO_UPDATE = dash.no_update

    if not pending_id or not history:
        return (NO_UPDATE,) * 13
    
    replaced = False
    msg_index = -1
    is_error = False
    
    # print(f"DEBUG: resolving pending msg {pending_id}")

    for i in range(len(history) - 1, -1, -1):
        if history[i].get('id') == pending_id:
            # print(f"DEBUG: Found pending msg at index {i}. Calling llm_response...")
            history[i]['text'], new_bpmn, is_error = llm_response(
                bpmn_store,
                history[i - 1]['text'],
                provider,
                model_choice,
                custom_model,
                api_key,
            )
            # print("DEBUG: llm_response returned.")
            del history[i]['id']
            replaced = True
            msg_index = i
            break

    if not replaced:
        return (NO_UPDATE,) * 13

    if is_error:
        return history, None, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, None

    # Default no-updates
    tasks_impacts_table = NO_UPDATE
    tasks_duration_table = NO_UPDATE
    choices_table = NO_UPDATE
    natures_table = NO_UPDATE
    loops_table = NO_UPDATE
    bpmn_dot = NO_UPDATE

    if EXPRESSION not in new_bpmn:
        history[msg_index]['text'] += "\nNo expression found in the BPMN"
        return history, None, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, None

    new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
    if new_bpmn[EXPRESSION] == '':
        history[msg_index]['text'] += "\nEmpty expression found in the BPMN"
        return history, None, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, None

    try:
        SESE_PARSER.parse(new_bpmn[EXPRESSION])
    except Exception as e:
        history[msg_index]['text'] += f"\nParsing error: {str(e)}"
        history[msg_index]['text'] += f"\nParsing error: {str(e)}"
        return history, None, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, None

    # Proposal Mode: Do NOT generate tables or reset simulation yet.
    # Just validate parsing and return proposal.
    
    # Update History with Proposal Flag (+ preview SVG)
    new_history = [msg.copy() for msg in history]
    if new_history:
        target_idx = msg_index if msg_index >= 0 else -1
        proposal_svg = None
        # Ensure required fields before generating preview SVG
        new_bpmn.setdefault(H, 0)
        new_bpmn.setdefault(IMPACTS_NAMES, [])
        new_bpmn.setdefault(IMPACTS, {})
        new_bpmn.setdefault(DURATIONS, {})
        new_bpmn.setdefault(DELAYS, {})
        new_bpmn.setdefault(PROBABILITIES, {})
        new_bpmn.setdefault(LOOP_PROBABILITY, {})
        new_bpmn.setdefault(LOOP_ROUND, {})

        if not isinstance(new_bpmn.get(IMPACTS), dict):
            new_bpmn[IMPACTS] = {}
        if not isinstance(new_bpmn.get(DURATIONS), dict):
            new_bpmn[DURATIONS] = {}
        if not isinstance(new_bpmn.get(DELAYS), dict):
            new_bpmn[DELAYS] = {}
        if not isinstance(new_bpmn.get(PROBABILITIES), dict):
            new_bpmn[PROBABILITIES] = {}
        if not isinstance(new_bpmn.get(LOOP_PROBABILITY), dict):
            new_bpmn[LOOP_PROBABILITY] = {}
        if not isinstance(new_bpmn.get(LOOP_ROUND), dict):
            new_bpmn[LOOP_ROUND] = {}

        tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(new_bpmn[EXPRESSION]))

        if not new_bpmn.get(IMPACTS_NAMES):
            inferred_impacts = None
            impacts_val = new_bpmn.get(IMPACTS)
            if isinstance(impacts_val, dict) and impacts_val:
                for val in impacts_val.values():
                    if isinstance(val, dict) and val:
                        inferred_impacts = list(val.keys())
                        break
                    if isinstance(val, (list, tuple)) and val:
                        inferred_impacts = None
                        break
            new_bpmn[IMPACTS_NAMES] = inferred_impacts or ["kWh"]

        impacts_dict = new_bpmn[IMPACTS]
        for task in tasks:
            val = impacts_dict.get(task)
            if isinstance(val, dict):
                for name in new_bpmn[IMPACTS_NAMES]:
                    val.setdefault(name, 0.0)
                impacts_dict[task] = val
            elif isinstance(val, (list, tuple)):
                impacts_dict[task] = {
                    name: float(val[idx]) if idx < len(val) else 0.0
                    for idx, name in enumerate(new_bpmn[IMPACTS_NAMES])
                }
            else:
                impacts_dict[task] = {name: 0.0 for name in new_bpmn[IMPACTS_NAMES]}

        durations_dict = new_bpmn[DURATIONS]
        for task in tasks:
            val = durations_dict.get(task)
            if isinstance(val, (list, tuple)) and len(val) >= 2:
                durations_dict[task] = (val[0], val[1])
            else:
                durations_dict[task] = (0, 1)

        delays_dict = new_bpmn[DELAYS]
        for choice in choices:
            delays_dict.setdefault(choice, 0)

        probs_dict = new_bpmn[PROBABILITIES]
        for nature in natures:
            probs_dict.setdefault(nature, 0.5)

        loops_prob_dict = new_bpmn[LOOP_PROBABILITY]
        loops_round_dict = new_bpmn[LOOP_ROUND]
        for loop in loops:
            loops_prob_dict.setdefault(loop, 0.5)
            loops_round_dict.setdefault(loop, 1)

        try:
            proposal_svg = load_bpmn_dot(new_bpmn)
        except Exception as exc:
            print(f"ERROR: Failed to generate proposal SVG: {exc}")
        new_history[target_idx]['is_proposal'] = True
        new_history[target_idx]['text'] += "\n\n💡 **Proposal Ready**. Review and Accept."
        if proposal_svg:
            new_history[target_idx]['proposal_svg'] = proposal_svg

    # Return 13 values:
    # 0: history
    # 1: pending
    # 2: bpmn_store (NO UPDATE)
    # 3: bound_store (NO UPDATE)
    # 4: bpmn_svg (NO UPDATE)
    # 5: petri_svg (NO UPDATE)
    # 6: sim_data (NO UPDATE)
    # 7-11: Tables (NO UPDATE)
    # 12: proposed_bpmn (NEW)

    return (
        new_history, 
        None, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE,
        new_bpmn # proposed_bpmn
    )
