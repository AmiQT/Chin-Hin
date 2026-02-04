"""
🔥 SUPER AGENTIC AI - Chin Hin Employee Assistant
Uses LangGraph for stateful, multi-step reasoning with loops.

Features:
- Multi-step reasoning with ReAct pattern
- Conversation memory
- Error recovery & retry
- Clarification loops
- Complex query handling
- Model rotation on quota errors
"""

import logging
import os
from typing import TypedDict, Annotated, Sequence, Literal, Optional, Any
from datetime import date, datetime
import json
import operator

# Disable google SDK internal retry BEFORE import
os.environ["GOOGLE_API_PYTHON_CLIENT_NO_RETRY"] = "1"

import google.generativeai as genai
from google.api_core import retry as google_retry

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.config import get_settings
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


# ================================================
# STATE DEFINITION
# ================================================

class AgentState(TypedDict):
    """State for the agent graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_id: str
    actions_taken: list
    retry_count: int
    needs_clarification: bool
    clarification_question: str


# ================================================
# TOOLS - Super powered! 🔧
# ================================================

@tool
def get_leave_balance(user_id: str) -> dict:
    """
    Get user's leave balance for current year.
    Call this when user asks about remaining leave, cuti balance, or baki cuti.
    
    Args:
        user_id: The user's UUID
    
    Returns:
        Dictionary with leave balances by type including remaining days
    """
    try:
        supabase = get_supabase_client()
        year = datetime.now().year
        
        types_result = supabase.table("leave_types").select("*").eq("is_active", True).execute()
        
        balances = []
        total_remaining = 0
        for leave_type in types_result.data:
            balance_result = supabase.table("leave_balances").select("*").eq(
                "user_id", user_id
            ).eq("leave_type_id", leave_type["id"]).eq("year", year).execute()
            
            if balance_result.data:
                balance = balance_result.data[0]
            else:
                balance = {
                    "total_days": leave_type.get("default_days", 14),
                    "used_days": 0,
                    "pending_days": 0
                }
            
            remaining = balance["total_days"] - balance["used_days"] - balance["pending_days"]
            total_remaining += remaining
            balances.append({
                "type": leave_type["name"],
                "total": balance["total_days"],
                "used": balance["used_days"],
                "pending": balance["pending_days"],
                "remaining": remaining
            })
        
        return {
            "success": True, 
            "balances": balances,
            "summary": f"Total remaining leave: {total_remaining} days"
        }
    except Exception as e:
        logger.error(f"get_leave_balance error: {e}")
        return {"success": False, "error": str(e)}


@tool
def apply_leave(
    user_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str = ""
) -> dict:
    """
    Apply for leave on behalf of user. 
    Call this when user wants to apply cuti, mohon cuti, or request leave.
    
    Args:
        user_id: The user's UUID
        leave_type: Type of leave - Annual, MC (medical), Emergency, Unpaid
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format  
        reason: Optional reason for leave
    
    Returns:
        Result with success status and leave details
    """
    try:
        supabase = get_supabase_client()
        
        # Find leave type
        type_result = supabase.table("leave_types").select("*").ilike("name", f"%{leave_type}%").execute()
        if not type_result.data:
            available = supabase.table("leave_types").select("name").execute()
            types_list = [t["name"] for t in available.data]
            return {
                "success": False, 
                "error": f"Leave type '{leave_type}' not found",
                "available_types": types_list,
                "suggestion": "Please specify one of the available leave types"
            }
        
        leave_type_id = type_result.data[0]["id"]
        leave_type_name = type_result.data[0]["name"]
        
        # Parse and validate dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "success": False,
                "error": "Invalid date format. Please use YYYY-MM-DD format",
                "suggestion": "Example: 2026-02-01"
            }
        
        total_days = (end - start).days + 1
        
        if total_days <= 0:
            return {"success": False, "error": "End date must be after start date"}
        
        if start < date.today():
            return {"success": False, "error": "Cannot apply leave for past dates"}
        
        # Check balance
        year = datetime.now().year
        balance_result = supabase.table("leave_balances").select("*").eq(
            "user_id", user_id
        ).eq("leave_type_id", leave_type_id).eq("year", year).execute()
        
        if balance_result.data:
            balance = balance_result.data[0]
            remaining = balance["total_days"] - balance["used_days"] - balance["pending_days"]
            if total_days > remaining:
                return {
                    "success": False, 
                    "error": f"Insufficient {leave_type_name} balance!",
                    "requested": total_days,
                    "remaining": remaining,
                    "suggestion": f"You only have {remaining} days. Consider applying for fewer days or different leave type."
                }
            
            # Update pending days
            supabase.table("leave_balances").update({
                "pending_days": balance["pending_days"] + total_days
            }).eq("id", balance["id"]).execute()
        
        # Create leave request
        new_leave = {
            "user_id": user_id,
            "leave_type_id": leave_type_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "reason": reason,
            "status": "pending"
        }
        
        result = supabase.table("leave_requests").insert(new_leave).execute()
        
        return {
            "success": True,
            "message": f"✅ {leave_type_name} leave applied successfully!",
            "details": {
                "type": leave_type_name,
                "start": start_date,
                "end": end_date,
                "days": total_days,
                "status": "pending",
                "leave_id": result.data[0]["id"] if result.data else None
            }
        }
    except Exception as e:
        logger.error(f"apply_leave error: {e}")
        return {"success": False, "error": str(e)}


@tool
def get_my_leaves(user_id: str, status: str = "all") -> dict:
    """
    Get user's leave requests history.
    Call when user asks about their leave history, pending leaves, or past requests.
    
    Args:
        user_id: The user's UUID
        status: Filter by status - all, pending, approved, rejected
    
    Returns:
        List of leave requests with details
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("leave_requests").select(
            "*, leave_types(name)"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(10)
        
        if status != "all":
            query = query.eq("status", status)
        
        result = query.execute()
        
        leaves = []
        for leave in result.data:
            leaves.append({
                "id": leave["id"],
                "type": leave["leave_types"]["name"] if leave.get("leave_types") else "Unknown",
                "start": leave["start_date"],
                "end": leave["end_date"],
                "days": leave["total_days"],
                "status": leave["status"],
                "reason": leave.get("reason", "")
            })
        
        return {
            "success": True,
            "leaves": leaves,
            "count": len(leaves)
        }
    except Exception as e:
        logger.error(f"get_my_leaves error: {e}")
        return {"success": False, "error": str(e)}


@tool  
def list_rooms() -> dict:
    """
    List all available meeting rooms with details.
    Call when user asks what rooms are available, bilik mesyuarat, or meeting rooms.
    
    Returns:
        List of rooms with name, capacity, location and amenities
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("rooms").select("*").eq("is_active", True).execute()
        
        rooms = []
        for room in result.data:
            rooms.append({
                "id": room["id"],
                "name": room["name"],
                "capacity": room.get("capacity", "N/A"),
                "location": room.get("location", "N/A"),
                "amenities": room.get("amenities", [])
            })
        
        return {"success": True, "rooms": rooms, "count": len(rooms)}
    except Exception as e:
        logger.error(f"list_rooms error: {e}")
        return {"success": False, "error": str(e)}


@tool
def check_room_availability(room_name: str, date: str, start_time: str, end_time: str) -> dict:
    """
    Check if a room is available at specified time.
    Call before booking to verify availability.
    
    Args:
        room_name: Name of the room to check
        date: Date to check YYYY-MM-DD
        start_time: Start time HH:MM
        end_time: End time HH:MM
    
    Returns:
        Availability status and any conflicts
    """
    try:
        supabase = get_supabase_client()
        
        # Find room
        room_result = supabase.table("rooms").select("*").ilike("name", f"%{room_name}%").execute()
        if not room_result.data:
            return {"success": False, "error": f"Room '{room_name}' not found"}
        
        room = room_result.data[0]
        
        # Build datetime strings
        start_dt = f"{date}T{start_time}:00"
        end_dt = f"{date}T{end_time}:00"
        
        # Check conflicts
        bookings = supabase.table("room_bookings").select("*").eq(
            "room_id", room["id"]
        ).eq("status", "confirmed").execute()
        
        conflicts = []
        for booking in bookings.data:
            b_start = booking["start_time"][:16]
            b_end = booking["end_time"][:16]
            
            # Simple overlap check
            if not (end_dt <= b_start or start_dt >= b_end):
                conflicts.append({
                    "title": booking["title"],
                    "time": f"{b_start} - {b_end}"
                })
        
        if conflicts:
            return {
                "success": True,
                "available": False,
                "room": room["name"],
                "conflicts": conflicts,
                "suggestion": "Try a different time slot"
            }
        
        return {
            "success": True,
            "available": True,
            "room": room["name"],
            "time_slot": f"{start_time} - {end_time}"
        }
    except Exception as e:
        logger.error(f"check_room_availability error: {e}")
        return {"success": False, "error": str(e)}


@tool
def book_room(
    user_id: str,
    room_name: str,
    title: str,
    date: str,
    start_time: str,
    end_time: str,
    description: str = ""
) -> dict:
    """
    Book a meeting room.
    Call when user wants to book/reserve a room for meeting.
    
    Args:
        user_id: The user's UUID
        room_name: Name of the room
        title: Meeting title/purpose
        date: Date YYYY-MM-DD
        start_time: Start time HH:MM (24h format)
        end_time: End time HH:MM (24h format)
        description: Optional meeting description
    
    Returns:
        Booking confirmation with details
    """
    try:
        supabase = get_supabase_client()
        
        # Find room
        room_result = supabase.table("rooms").select("*").ilike("name", f"%{room_name}%").execute()
        if not room_result.data:
            all_rooms = supabase.table("rooms").select("name").execute()
            room_names = [r["name"] for r in all_rooms.data]
            return {
                "success": False, 
                "error": f"Room '{room_name}' not found",
                "available_rooms": room_names
            }
        
        room = room_result.data[0]
        
        # Build datetime
        start_dt = f"{date}T{start_time}:00"
        end_dt = f"{date}T{end_time}:00"
        
        # Validate time
        if start_time >= end_time:
            return {"success": False, "error": "End time must be after start time"}
        
        # Check conflicts
        bookings = supabase.table("room_bookings").select("*").eq(
            "room_id", room["id"]
        ).eq("status", "confirmed").execute()
        
        for booking in bookings.data:
            b_start = booking["start_time"][:16]
            b_end = booking["end_time"][:16]
            if not (end_dt <= b_start or start_dt >= b_end):
                return {
                    "success": False,
                    "error": f"Room already booked: {booking['title']} ({b_start} - {b_end})"
                }
        
        # Create booking
        new_booking = {
            "room_id": room["id"],
            "user_id": user_id,
            "title": title,
            "start_time": start_dt,
            "end_time": end_dt,
            "description": description,
            "status": "confirmed"
        }
        
        result = supabase.table("room_bookings").insert(new_booking).execute()
        
        return {
            "success": True,
            "message": f"✅ Room booked successfully!",
            "details": {
                "room": room["name"],
                "title": title,
                "date": date,
                "time": f"{start_time} - {end_time}",
                "booking_id": result.data[0]["id"] if result.data else None
            }
        }
    except Exception as e:
        logger.error(f"book_room error: {e}")
        return {"success": False, "error": str(e)}


@tool
def get_my_bookings(user_id: str) -> dict:
    """
    Get user's room bookings.
    Call when user asks about their bookings or scheduled meetings.
    
    Args:
        user_id: The user's UUID
    
    Returns:
        List of upcoming and recent bookings
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("room_bookings").select(
            "*, rooms(name)"
        ).eq("user_id", user_id).order("start_time", desc=True).limit(10).execute()
        
        bookings = []
        for b in result.data:
            bookings.append({
                "room": b["rooms"]["name"] if b.get("rooms") else "Unknown",
                "title": b["title"],
                "start": b["start_time"],
                "end": b["end_time"],
                "status": b["status"]
            })
        
        return {"success": True, "bookings": bookings, "count": len(bookings)}
    except Exception as e:
        logger.error(f"get_my_bookings error: {e}")
        return {"success": False, "error": str(e)}


@tool
def get_claim_categories() -> dict:
    """
    Get available expense claim categories with limits.
    Call when user asks about claim types or expense categories.
    
    Returns:
        List of categories with max amounts
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("claim_categories").select("*").eq("is_active", True).execute()
        
        categories = []
        for cat in result.data:
            categories.append({
                "id": cat["id"],
                "name": cat["name"],
                "max_amount": float(cat["max_amount"]) if cat.get("max_amount") else None,
                "description": cat.get("description", "")
            })
        
        return {"success": True, "categories": categories}
    except Exception as e:
        logger.error(f"get_claim_categories error: {e}")
        return {"success": False, "error": str(e)}


@tool
def submit_claim(
    user_id: str,
    category: str,
    amount: float,
    description: str
) -> dict:
    """
    Submit an expense claim.
    Call when user wants to claim expenses, submit claim, or reimburse.
    
    Args:
        user_id: The user's UUID
        category: Category name - Transport, Meals, Parking, etc
        amount: Claim amount in RM
        description: What the expense was for
    
    Returns:
        Claim submission result
    """
    try:
        supabase = get_supabase_client()
        
        # Find category
        cat_result = supabase.table("claim_categories").select("*").ilike("name", f"%{category}%").execute()
        if not cat_result.data:
            all_cats = supabase.table("claim_categories").select("name, max_amount").execute()
            return {
                "success": False,
                "error": f"Category '{category}' not found",
                "available_categories": [
                    {"name": c["name"], "max": c.get("max_amount")} 
                    for c in all_cats.data
                ]
            }
        
        cat = cat_result.data[0]
        
        # Check max amount
        max_amount = cat.get("max_amount")
        if max_amount and amount > float(max_amount):
            return {
                "success": False,
                "error": f"Amount RM{amount:.2f} exceeds limit",
                "max_allowed": float(max_amount),
                "suggestion": f"Maximum for {cat['name']} is RM{float(max_amount):.2f}"
            }
        
        if amount <= 0:
            return {"success": False, "error": "Amount must be positive"}
        
        # Create claim
        new_claim = {
            "user_id": user_id,
            "category_id": cat["id"],
            "amount": amount,
            "description": description,
            "claim_date": date.today().isoformat(),
            "status": "pending"
        }
        
        result = supabase.table("claims").insert(new_claim).execute()
        
        return {
            "success": True,
            "message": f"✅ Claim submitted!",
            "details": {
                "category": cat["name"],
                "amount": f"RM{amount:.2f}",
                "description": description,
                "status": "pending",
                "claim_id": result.data[0]["id"] if result.data else None
            }
        }
    except Exception as e:
        logger.error(f"submit_claim error: {e}")
        return {"success": False, "error": str(e)}


@tool
def get_my_claims(user_id: str, status: str = "all") -> dict:
    """
    Get user's expense claims history.
    Call when user asks about their claims, pending reimbursements, or past expenses.
    
    Args:
        user_id: The user's UUID
        status: Filter - all, pending, approved, rejected
    
    Returns:
        List of claims with details
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("claims").select(
            "*, claim_categories(name)"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(10)
        
        if status != "all":
            query = query.eq("status", status)
        
        result = query.execute()
        
        claims = []
        total_pending = 0
        for claim in result.data:
            amount = float(claim["amount"])
            if claim["status"] == "pending":
                total_pending += amount
            claims.append({
                "category": claim["claim_categories"]["name"] if claim.get("claim_categories") else "Unknown",
                "amount": f"RM{amount:.2f}",
                "description": claim.get("description", ""),
                "date": claim["claim_date"],
                "status": claim["status"]
            })
        
        return {
            "success": True,
            "claims": claims,
            "count": len(claims),
            "total_pending": f"RM{total_pending:.2f}"
        }
    except Exception as e:
        logger.error(f"get_my_claims error: {e}")
        return {"success": False, "error": str(e)}


@tool
def get_today_info() -> dict:
    """
    Get current date and time info.
    Call when you need to know today's date for relative date calculations.
    
    Returns:
        Current date, day of week, and time info
    """
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
        "time": now.strftime("%H:%M"),
        "year": now.year,
        "month": now.strftime("%B"),
        "week_number": now.isocalendar()[1]
    }


@tool
def search_policy(query: str) -> dict:
    """
    Search company handbook/policies (RAG).
    Call this when user asks about rules, benefits, MC limits, working hours, etc.
    
    Args:
        query: Search query in English or Malay
    
    Returns:
        Relevant policy snippets
    """
    logger.info(f"🔍 AI is searching policy for: {query}")
    print(f"\n[DEBUG] search_policy query: {query}")
    
    try:
        from app.services.embedding_service import get_embedding_service
        import asyncio
        
        # Get embedding
        embedding_service = get_embedding_service()
        
        # Safely run async code in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            # If we are in a loop (like FastAPI), we need a different approach
            # Using a trick to run async in running loop for simple call
            import nest_asyncio
            nest_asyncio.apply()
            vector = asyncio.run(embedding_service.get_embeddings(query))
        else:
            vector = loop.run_until_complete(embedding_service.get_embeddings(query))
        
        if not vector:
            print("[DEBUG] ❌ Failed to generate vector")
            return {"success": False, "error": "Gagal menjana carian AI. Cuba lagi jap lagi."}
            
        print(f"[DEBUG] ✅ Vector generated (len: {len(vector)})")
        
        supabase = get_supabase_client()
        result = supabase.rpc("match_knowledge_base", {
            "query_embedding": vector,
            "match_threshold": 0.4, # Lowered slightly for better recall
            "match_count": 5        # Increased count
        }).execute()
        
        if not result.data:
            print("[DEBUG] ⚠️ No results found in Supabase")
            return {"success": True, "info": "Tiada polisi dijumpai berkaitan query tersebut dalam handbook."}
            
        snippets = []
        for r in result.data:
            snippets.append({
                "content": r["content"],
                "similarity": round(r.get("similarity", 0) * 100, 1)
            })
            
        print(f"[DEBUG] ✅ Found {len(snippets)} results")
        return {
            "success": True, 
            "results": snippets,
            "count": len(snippets)
        }
    except Exception as e:
        logger.error(f"search_policy error: {e}")
        print(f"[DEBUG] ❌ Error in search_policy: {e}")
        return {"success": False, "error": str(e)}


@tool
def get_my_nudges(user_id: str) -> dict:
    """
    Get proactive reminders/notifications for the user.
    Call this to check if there are pending actions, reminders, or system alerts.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        List of active nudges
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("nudges").select("*").eq("user_id", user_id).eq("is_read", False).execute()
        
        nudges = []
        for n in result.data:
            nudges.append({
                "id": n["id"],
                "type": n["type"],
                "title": n["title"],
                "content": n["content"],
                "created_at": n["created_at"]
            })
            
        return {
            "success": True, 
            "nudges": nudges,
            "count": len(nudges)
        }
    except Exception as e:
        logger.error(f"get_my_nudges error: {e}")
        return {"success": False, "error": str(e)}


# ================================================
# ALL TOOLS
# ================================================

ALL_TOOLS = [
    get_leave_balance,
    apply_leave,
    get_my_leaves,
    list_rooms,
    check_room_availability,
    book_room,
    get_my_bookings,
    get_claim_categories,
    submit_claim,
    get_my_claims,
    get_today_info,
    search_policy,
    get_my_nudges,
]


# ================================================
# SYSTEM PROMPT
# ================================================

SYSTEM_PROMPT = """Kau Chin Hin AI Assistant aka "Bestie" office. BM/EN sempoi, Gen Z vibe (guna emoji, slang macam cun, ngam, bestie). 🤖✨

VIBE:
- Relax tapi pro. Jangan skema sangat. 🤙
- Guna "Bestie", "Beb", "Bro" atau "Sis" ikut kesesuaian.

RULES:
1. TOOLS IS KING: JANGAN ASUMME. Guna tools untuk check data.
2. USER_ID: Dah ada dalam context, jangan tanya lagi. Terus buat kerja.
3. EYES: Boleh "tengok" resit/invoice. Extract baki, merchant, date untuk claim submission.
4. KNOWLEDGE: Guna search_policy untuk apa-apa soalan pasal handbook/rules Chin Hin.
5. PROACTIVE: Kalau nampak unread notifications, "menyampit" sikit kat user sebagai friendly reminder.
6. ERROR: Kalau tool fail, explain chill-chill & suggest plan B.
7. CONFIRM: Confirm setiap action dengan details yang clear.

TOOLS: Leave (balance/apply/history), Rooms (list/book), Claims (submit/history), Policy (search), Date info, Nudges (list).
"""


# Token optimization: limit conversation history
MAX_HISTORY_MESSAGES = 6  # Keep last 6 messages (3 turns)


# ================================================
# MODEL ROTATION CONFIG 🔄
# ================================================

# ALL models to try (ordered by preference) - each has separate quota!
MODELS_TO_TRY = [
    # Gemini Flash family (best for agentic)
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite", 
    "gemini-2.0-flash",
    
    # Gemma models (separate quota, may not support all tools)
    "gemma-3-27b-it",
    "gemma-3-12b-it", 
    "gemma-3-4b-it",
    "gemma-3-2b-it",
]

# Track current model/key index (persistent across requests)
_current_model_index = 0
_current_key_index = 0
_failed_models = set()  # Track models that failed this session


def get_next_model_config():
    """Get next available model with API key rotation, skipping failed models."""
    global _current_model_index, _current_key_index
    
    settings = get_settings()
    api_keys = settings.gemini_api_keys
    
    if not api_keys:
        raise ValueError("No Gemini API keys configured!")
    
    # Find next model that hasn't failed
    attempts = 0
    while attempts < len(MODELS_TO_TRY):
        model = MODELS_TO_TRY[_current_model_index % len(MODELS_TO_TRY)]
        if model not in _failed_models:
            api_key = api_keys[_current_key_index % len(api_keys)]
            return model, api_key
        _current_model_index += 1
        attempts += 1
    
    # All models failed, reset and try with next key
    _failed_models.clear()
    _current_key_index += 1
    if _current_key_index >= len(api_keys):
        _current_key_index = 0
        logger.warning("⚠️ All models and API keys exhausted! Resetting...")
    
    model = MODELS_TO_TRY[0]
    api_key = api_keys[_current_key_index % len(api_keys)]
    return model, api_key


def rotate_to_next_model(failed_model: str = None):
    """Rotate to next model, marking current as failed."""
    global _current_model_index, _current_key_index, _failed_models
    
    if failed_model:
        _failed_models.add(failed_model)
        logger.info(f"❌ Marked model as failed: {failed_model}")
    
    _current_model_index += 1
    
    model, api_key = get_next_model_config()
    logger.info(f"🔄 Rotated to model: {model} (failed: {len(_failed_models)}/{len(MODELS_TO_TRY)})")
    return model, api_key


def reset_model_rotation():
    """Reset rotation state (call at start of each request)."""
    global _failed_models
    # Don't reset - keep tracking failed models until quota resets
    pass


# ================================================
# AGENT GRAPH WITH ROTATION
# ================================================

def create_agent(model_name: str = None, api_key: str = None):
    """Create the LangGraph agent with specified or default model."""
    settings = get_settings()
    
    # Use provided or get from rotation
    if not model_name or not api_key:
        model_name, api_key = get_next_model_config()
    
    logger.info(f"🤖 Creating agent with model: {model_name}")
    
    # Configure google genai with NO retry
    genai.configure(
        api_key=api_key,
    )
    
    # Initialize LLM with DISABLED built-in retry
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True,
        max_retries=0,      # Disable langchain retry
        timeout=15,         # 15 second timeout (min 10s required)
        max_output_tokens=2048,  # Limit output for speed
    )
    
    # Bind tools
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    
    # Define nodes
    def agent_node(state: AgentState) -> dict:
        """Main agent reasoning node."""
        messages = list(state["messages"])
        user_id = state.get("user_id", "Unknown")
        
        # dynamic system prompt with user identity
        current_system_prompt = f"{SYSTEM_PROMPT}\n\nCURRENT USER ID: {user_id}\nGunakan ID ini untuk semua tool calls yang memerlukan user_id."
        
        # Add system message if not present or update it
        system_msg_index = -1
        for i, m in enumerate(messages):
            if isinstance(m, SystemMessage):
                system_msg_index = i
                break
        
        if system_msg_index != -1:
            messages[system_msg_index] = SystemMessage(content=current_system_prompt)
        else:
            messages = [SystemMessage(content=current_system_prompt)] + messages
        
        # Sliding window: keep only recent messages (token optimization)
        # IMPORTANT: Must preserve paired messages (AIMessage with tool_calls + ToolMessage)
        if len(messages) > MAX_HISTORY_MESSAGES + 1:  # +1 for system msg
            system_msg = messages[0]
            recent_msgs = messages[-(MAX_HISTORY_MESSAGES):]
            
            # Ensure we don't start with a ToolMessage (orphan response)
            # Find safe starting point - should be HumanMessage or clean AIMessage
            safe_start = 0
            for i, m in enumerate(recent_msgs):
                if isinstance(m, ToolMessage):
                    safe_start = i + 1  # Skip orphan tool messages
                elif isinstance(m, AIMessage) and hasattr(m, 'tool_calls') and m.tool_calls:
                    # Check if corresponding ToolMessage exists after this
                    has_response = False
                    for j in range(i + 1, len(recent_msgs)):
                        if isinstance(recent_msgs[j], ToolMessage):
                            has_response = True
                            break
                        if isinstance(recent_msgs[j], HumanMessage):
                            break
                    if not has_response:
                        safe_start = i + 1  # Skip orphan tool calls
                else:
                    break
            
            messages = [system_msg] + recent_msgs[safe_start:]
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Decide whether to use tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
    
    def tool_node(state: AgentState) -> dict:
        """Execute tools and track actions."""
        messages = state["messages"]
        last_message = messages[-1]
        
        actions = state.get("actions_taken", [])
        tool_node_executor = ToolNode(ALL_TOOLS)
        
        # Execute tools
        result = tool_node_executor.invoke(state)
        
        # Track actions
        if hasattr(last_message, "tool_calls"):
            for tc in last_message.tool_calls:
                actions.append({
                    "tool": tc["name"],
                    "args": tc.get("args", {}),
                })
        
        return {
            "messages": result["messages"],
            "actions_taken": actions
        }
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )
    
    workflow.add_edge("tools", "agent")  # Loop back after tools
    
    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# ================================================
# GLOBAL AGENT INSTANCE
# ================================================

_agent = None
_agent_model = None  # Track which model the current agent uses


def get_agent(force_new: bool = False):
    """Get or create agent instance."""
    global _agent, _agent_model
    
    current_model, current_key = get_next_model_config()
    
    # Recreate if model changed or forced
    if _agent is None or force_new or _agent_model != current_model:
        _agent = create_agent(current_model, current_key)
        _agent_model = current_model
        
    return _agent


def is_retryable_error(error: Exception) -> bool:
    """Check if error should trigger model rotation (quota, rate limit, or model not found)."""
    error_str = str(error).lower()
    return any(x in error_str for x in [
        "quota", "rate_limit", "resource_exhausted", 
        "429", "too many requests", "exceeded",
        "not_found", "404", "not found"  # Also rotate on model not found
    ])


# # ================================================
# MAIN INTERFACE (backward compatible)
# ================================================

MAX_ROTATION_RETRIES = 7  # Try all 7 models before giving up

async def agentic_chat(
    message: str,
    user_id: str,
    conversation_id: str = "default",
    history: Optional[list] = None,
    image_data: Optional[str] = None
) -> dict:
    """
    Main chat function with multi-step reasoning.
    Backward compatible with existing chat.py interface.
    
    Features auto-rotation on quota errors!
    
    Args:
        message: User's message
        user_id: Current user ID
        conversation_id: For memory persistence
        history: Previous messages (optional)
    
    Returns:
        Response dict with 'response' and 'actions' keys
    """
    global _agent
    
    # Build messages (only once, reuse on retries)
    messages = []
    
    # Proactive: Check for nudges to inject into context
    try:
        supabase = get_supabase_client()
        nudge_result = supabase.table("nudges").select("title, content").eq("user_id", user_id).eq("is_read", False).limit(3).execute()
        if nudge_result.data:
            nudge_context = "\n".join([f"- {n['title']}: {n['content']}" for n in nudge_result.data])
            messages.append(SystemMessage(content=f"IMPORTANT: The user has UNREAD NOTIFICATIONS that require action:\n{nudge_context}\n\nYou MUST proactively mention these to the user in your response (e.g., 'By the way, I noticed you have...'). Do not ignore this context."))
    except Exception as e:
        logger.warning(f"Failed to fetch nudges for context: {e}")

    if history:
        # Only keep last N messages from history
        recent_history = history[-(MAX_HISTORY_MESSAGES - 1):] if len(history) > MAX_HISTORY_MESSAGES - 1 else history
        for h in recent_history:
            if h.get("role") == "user":
                meta = h.get("metadata")
                if meta and meta.get("image_data"):
                    # Reconstruct multimodal history
                    content = [
                        {"type": "text", "text": h["content"]},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{meta['image_data']}"}
                    ]
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(HumanMessage(content=h["content"]))
            elif h.get("role") == "assistant":
                messages.append(AIMessage(content=h["content"]))
    
    if image_data:
        # Multimodal message
        messages.append(HumanMessage(content=[
            {"type": "text", "text": message},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
        ]))
    else:
        messages.append(HumanMessage(content=message))
    
    # Initial state
    initial_state = {
        "messages": messages,
        "user_id": user_id,
        "actions_taken": [],
        "retry_count": 0,
        "needs_clarification": False,
        "clarification_question": "",
    }
    
    # Config for memory
    config = {"configurable": {"thread_id": conversation_id}}
    
    # Retry loop with model rotation
    last_error = None
    for attempt in range(MAX_ROTATION_RETRIES):
        try:
            agent = get_agent(force_new=(attempt > 0))  # Force new on retries
            current_model, _ = get_next_model_config()
            
            logger.info(f"🚀 Attempt {attempt + 1}/{MAX_ROTATION_RETRIES} with model: {current_model}")
            
            # Run agent
            result = agent.invoke(initial_state, config=config)
            
            # Extract response
            final_messages = result["messages"]
            raw_response = ""
            for msg in reversed(final_messages):
                if isinstance(msg, AIMessage) and msg.content:
                    raw_response = msg.content
                    break
            
            # Format response as string
            if isinstance(raw_response, list):
                ai_response = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in raw_response])
            else:
                ai_response = str(raw_response)
            
            return {
                "response": ai_response or "Done! ✅",
                "actions": result.get("actions_taken", []),
                "conversation_id": conversation_id,
                "model_used": current_model  # Include which model was used
            }
            
        except Exception as e:
            last_error = e
            current_model, _ = get_next_model_config()
            logger.error(f"Agent error (attempt {attempt + 1}): {e}")
            
            # Check if retryable error - if so, rotate and retry
            if is_retryable_error(e) and attempt < MAX_ROTATION_RETRIES - 1:
                logger.info(f"🔄 Error detected, rotating from {current_model}...")
                rotate_to_next_model(current_model)  # Mark this model as failed
                _agent = None  # Force recreate agent
                continue
            else:
                # Non-quota error or last attempt - give up
                break
    
    # All retries exhausted
    logger.error(f"All {MAX_ROTATION_RETRIES} attempts failed. Last error: {last_error}")
    return {
        "response": f"❌ Alamak, semua model dah exceed quota. Cuba lagi dalam beberapa minit! Error: {str(last_error)}",
        "actions": [],
        "error": str(last_error)
    }
