from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from app.agents.gemini_client import simple_generate
from app.agents.function_agent import agentic_chat
from app.db.supabase_client import get_supabase_client
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/chat", tags=["AI Chat"])
logger = logging.getLogger(__name__)


# ================================================
# REQUEST/RESPONSE MODELS
# ================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None
    user_id: str = "11111111-1111-1111-1111-111111111111"  # Default for testing
    image_data: Optional[str] = None  # Base64 string for multimodal


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    success: bool = True
    conversation_id: str
    message: str
    response: str


# ================================================
# CHAT ENDPOINTS
# ================================================

@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Send a message to AI assistant dan get response.
    Creates new conversation if conversation_id not provided.
    Requires: Authenticated user
    """
    supabase = get_supabase_client()
    conversation_id = request.conversation_id
    
    # Use authenticated user's ID
    user_id = current_user.id
    
    # Create new conversation if needed
    if not conversation_id:
        # Create new conversation in Supabase
        conv_result = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": request.message[:50]
        }).execute()
        
        if conv_result.data:
            conversation_id = conv_result.data[0]["id"]
            logger.info(f"📝 New conversation created: {conversation_id}")
        else:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
    else:
        # Check if conversation exists
        conv_check = supabase.table("conversations").select("id").eq("id", conversation_id).execute()
        if not conv_check.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get conversation history from Supabase
    history_result = supabase.table("messages").select(
        "role, content, metadata"
    ).eq("conversation_id", conversation_id).order("created_at").execute()
    
    history = [
        {"role": m["role"], "content": m["content"], "metadata": m.get("metadata")} 
        for m in history_result.data
    ]
    
    # Save user message to Supabase
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": "user",
        "content": request.message,
        "metadata": {"image_data": request.image_data} if request.image_data else None
    }).execute()
    
    # Use agentic chat with function calling
    agent_result = await agentic_chat(
        message=request.message,
        user_id=user_id,
        history=history,
        image_data=request.image_data
    )
    
    ai_response = agent_result["response"]
    actions_taken = agent_result.get("actions", [])
    
    # Log actions if any
    if actions_taken:
        logger.info(f"🤖 AI executed {len(actions_taken)} action(s)")
    
    # Save AI response to Supabase
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": ai_response,
        "metadata": {"actions": actions_taken} if actions_taken else None
    }).execute()
    
    # Update conversation timestamp
    supabase.table("conversations").update({
        "updated_at": datetime.now().isoformat()
    }).eq("id", conversation_id).execute()
    
    return ChatResponse(
        conversation_id=conversation_id,
        message=request.message,
        response=ai_response
    )


@router.get("/conversations")
async def get_conversations(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get all conversations for current user.
    Requires: Authenticated user
    """
    supabase = get_supabase_client()
    
    # Only return current user's conversations
    result = supabase.table("conversations").select("*").eq(
        "user_id", current_user.id
    ).order("updated_at", desc=True).execute()
    
    return {
        "success": True,
        "data": result.data,
        "total": len(result.data)
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get a specific conversation with its messages.
    Requires: Authenticated user (must own conversation)
    """
    supabase = get_supabase_client()
    
    conv_result = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    if not conv_result.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    conv = conv_result.data[0]
    if conv.get("user_id") != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Kau tak boleh view conversation orang lain! 🚫")
    
    messages_result = supabase.table("messages").select("*").eq(
        "conversation_id", conversation_id
    ).order("created_at").execute()
    
    conversation = conv_result.data[0]
    conversation["messages"] = messages_result.data
    
    return {
        "success": True,
        "data": conversation
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Delete a conversation and its messages.
    Requires: Authenticated user (must own conversation)
    """
    supabase = get_supabase_client()
    
    conv_result = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    if not conv_result.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    conv = conv_result.data[0]
    if conv.get("user_id") != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Kau tak boleh delete conversation orang lain! 🚫")
    
    # Delete messages first (foreign key constraint)
    supabase.table("messages").delete().eq("conversation_id", conversation_id).execute()
    
    # Delete conversation
    supabase.table("conversations").delete().eq("id", conversation_id).execute()
    
    return {
        "success": True,
        "message": "Conversation deleted 🗑️"
    }


# ================================================
# HELPER FUNCTIONS
# ================================================

def classify_intent(message: str) -> str:
    """
    Simple intent classification for model routing.
    TODO: Use more sophisticated NLU later.
    """
    message_lower = message.lower()
    
    # Greetings
    greetings = ["hi", "hello", "hey", "assalamualaikum", "salam", "morning", "petang"]
    if any(g in message_lower for g in greetings):
        return "greeting"
    
    # Status checks
    status_words = ["status", "check", "balance", "baki", "berapa"]
    if any(s in message_lower for s in status_words):
        return "status_check"
    
    # Leave related
    leave_words = ["cuti", "leave", "mc", "apply", "mohon"]
    if any(word in message_lower for word in leave_words):
        return "apply_leave"
    
    # Claims related
    claim_words = ["claim", "expense", "receipt", "resit", "bayar"]
    if any(c in message_lower for c in claim_words):
        return "submit_claim"
    
    # Room booking
    room_words = ["book", "room", "meeting", "bilik"]
    if any(r in message_lower for r in room_words):
        return "book_room"  # Complex task
    
    return "general"


# ================================================
# QUICK TEST ENDPOINT
# ================================================

@router.get("/test")
async def test_ai():
    """Quick test endpoint for AI without conversation."""
    response = await simple_generate("Say hello in Bahasa Malaysia with emoji!")
    return {
        "success": True,
        "response": response
    }
