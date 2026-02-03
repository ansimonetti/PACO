from datetime import datetime
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from src.ai.model import chat_histories, SESSION_TIMEOUT, LLMChatRequest
from src.ai.llm_utils import run_llm_on_bpmn
from src.paco.parser.bpmn import validate_bpmn_dict
from src.utils.check_syntax import check_bpmn_syntax


def register_api_llm(app: FastAPI):
    @app.get("/get_chat_history")
    async def get_chat_history(session_id: str) -> list:
        if not isinstance(session_id, str):
            raise HTTPException(status_code=400, detail="Invalid input")
        try:
            return chat_histories[session_id]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def clean_old_sessions():
        now = datetime.now()
        expired = [sid for sid, meta in chat_histories.items()
                   if (now - meta["last_active"]) > SESSION_TIMEOUT]
        for sid in expired:
            del chat_histories[sid]

    @app.post("/llm_bpmn_chat")
    async def llm_bpmn_chat(req: LLMChatRequest):
        clean_old_sessions()

        session_id = req.session_id or str(uuid4())

        if req.reset or session_id not in chat_histories:
            chat_histories[session_id] = {
                "history": [],
                "last_active": datetime.now()
            }

        try:
            validate_bpmn_dict(req.bpmn)
            check_bpmn_syntax(req.bpmn)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid input BPMN: {e}")

        try:
            result = run_llm_on_bpmn(
                bpmn_dict=req.bpmn,
                message=req.message,
                session_id=session_id,
                max_attempts=req.max_attempts,
                provider=req.provider,
                model=req.model,
                api_key=req.api_key,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        chat_histories[session_id]["history"].append({
            "user": req.message,
            "assistant": result["message"]
        })
        chat_histories[session_id]["last_active"] = datetime.now()

        result["session_id"] = session_id
        return result
