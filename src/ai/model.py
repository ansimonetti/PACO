from datetime import timedelta
from pydantic import BaseModel

chat_histories = {}
SESSION_TIMEOUT = timedelta(days=1)

class LLMChatRequest(BaseModel):
    bpmn: dict
    message: str
    session_id: str | None = None
    max_attempts: int = 7
    reset: bool = False
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None


