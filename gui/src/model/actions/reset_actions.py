"""
Reset Actions Module
Handles chat reset logic.
"""


def reset_chat_logic():
    """
    Clear chat history and trigger UI reset.
    
    Returns tuple of 3 values:
    (chat_history, pending_message, reset_trigger)
    """
    return [], None, False


def acknowledge_reset_logic(trigger):
    """
    Acknowledge reset completion.
    
    Returns: reset_trigger (False) or None to prevent update
    """
    if trigger:
        return False
    return None  # Indicates PreventUpdate
