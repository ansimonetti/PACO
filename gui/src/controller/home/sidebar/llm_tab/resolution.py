"""
LLM Resolution Callback
Handles the pending-message -> LLM response flow.
This is a SEPARATE callback from central_store_manager to avoid self-triggering issues.
"""
from dash import Output, Input, State, no_update, ctx

from gui.src.model.actions.chat_actions import resolve_llm_response


def register_llm_resolution_callback(callback):
    """
    Register the callback that resolves pending LLM messages.
    
    This callback is triggered when pending-message changes.
    It calls the LLM API and updates the chat history and BPMN stores.
    """
    @callback(
        Output('chat-history', 'data', allow_duplicate=True),
        Output('pending-message', 'data', allow_duplicate=True),
        Output('bpmn-store', 'data', allow_duplicate=True),
        Output('bound-store', 'data', allow_duplicate=True),
        Output({'type': 'bpmn-svg-store', 'index': 'main'}, 'data', allow_duplicate=True),
        Output({'type': 'petri-svg-store', 'index': 'main'}, 'data', allow_duplicate=True),
        Output('simulation-store', 'data', allow_duplicate=True),
        Output('task-impacts-table', 'children', allow_duplicate=True),
        Output('task-durations-table', 'children', allow_duplicate=True),
        Output('choice-table', 'children', allow_duplicate=True),
        Output('nature-table', 'children', allow_duplicate=True),
        Output('loop-table', 'children', allow_duplicate=True),
        Output('proposed-bpmn-store', 'data', allow_duplicate=True),
        Input('pending-message', 'data'),
        State('chat-history', 'data'),
        State('bpmn-store', 'data'),
        State('bound-store', 'data'),
        State('llm-provider', 'value'),
        State('llm-model', 'value'),
        State('llm-model-custom', 'value'),
        State('llm-api-key', 'value'),
        prevent_initial_call=True
    )
    def resolve_pending_message(
        pending_msg, chat_history, bpmn_store, bound_store,
        llm_provider, llm_model, llm_model_custom, llm_api_key
    ):
        # Only trigger if there's actually a pending message
        if not pending_msg:
            return (no_update,) * 13
        
        # print(f"DEBUG: resolve_pending_message triggered with msg={pending_msg}")
        
        res = resolve_llm_response(
            pending_msg, chat_history, bpmn_store, bound_store,
            llm_provider, llm_model, llm_model_custom, llm_api_key
        )
        
        # res is a tuple of 13 values:
        # (history, pending, bpmn, bound, bpmn_svg, petri_svg, sim, 
        #  impacts, durations, choices, natures, loops, proposed_bpmn)
        return res
