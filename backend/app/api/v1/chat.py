"""Chat endpoint - AI conversation handler. In-memory store, no Supabase."""

import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict

from app.agents.azure_client import simple_generate
from app.agents.function_agent import agentic_chat
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/chat", tags=["AI Chat"])
logger = logging.getLogger(__name__)

_conversations: dict = {}
_messages: dict = {}


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: str = "11111111-1111-1111-1111-111111111111"
    image_data: Optional[str] = None
    history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    success: bool = True
    conversation_id: str
    message: str
    response: str
    actions: Optional[list] = []


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.id
    conversation_id = request.conversation_id

    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        _conversations[conversation_id] = {"user_id": user_id, "title": request.message[:50], "updated_at": datetime.now().isoformat()}
        _messages[conversation_id] = []
    else:
        if conversation_id not in _conversations:
            _conversations[conversation_id] = {"user_id": user_id, "title": request.message[:50], "updated_at": datetime.now().isoformat()}
            _messages[conversation_id] = []

    if conversation_id not in _messages:
        _messages[conversation_id] = []

    _messages[conversation_id].append({"role": "user", "content": request.message, "created_at": datetime.now().isoformat()})

    effective_history = request.history if request.history else [
        {"role": m["role"], "content": m["content"]} for m in _messages.get(conversation_id, [])
    ]

    agent_result = await agentic_chat(
        message=request.message,
        user_id=user_id,
        conversation_id=conversation_id,
        history=effective_history,
        image_data=request.image_data,
    )

    ai_response = agent_result["response"]
    actions_taken = agent_result.get("actions", [])

    _messages[conversation_id].append({"role": "assistant", "content": ai_response, "created_at": datetime.now().isoformat()})
    if conversation_id in _conversations:
        _conversations[conversation_id]["updated_at"] = datetime.now().isoformat()

    return ChatResponse(conversation_id=conversation_id, message=request.message, response=ai_response, actions=actions_taken)


@router.get("/conversations")
async def get_conversations(current_user: CurrentUser = Depends(get_current_user)):
    user_convs = [{"id": cid, **cdata} for cid, cdata in _conversations.items() if cdata.get("user_id") == current_user.id]
    user_convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return {"success": True, "data": user_convs, "total": len(user_convs)}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, current_user: CurrentUser = Depends(get_current_user)):
    conv = _conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.get("user_id") != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Tak boleh view conversation orang lain!")
    return {"success": True, "data": {"id": conversation_id, **conv, "messages": _messages.get(conversation_id, [])}}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, current_user: CurrentUser = Depends(get_current_user)):
    conv = _conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.get("user_id") != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Tak boleh delete conversation orang lain!")
    _conversations.pop(conversation_id, None)
    _messages.pop(conversation_id, None)
    return {"success": True, "message": "Conversation deleted"}


@router.get("/test")
async def test_ai():
    response = await simple_generate("Say hello in Bahasa Malaysia with emoji!")
    return {"success": True, "response": response}
