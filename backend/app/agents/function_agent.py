"""
🔥 AGENTIC AI - Chin Hin Employee Assistant
Implementation with Chain of Thought (CoT) and Human-in-the-Loop (HITL).
Uses Local Mock Data for testing (bypassing Supabase for now).
"""

import logging
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from contextvars import ContextVar

from openai import AzureOpenAI, BadRequestError
from app.config import get_settings
from app.services.data_store import get_store

# Current user context — set in agentic_chat before calling process_chat
_user_ctx: ContextVar[str] = ContextVar("user_id", default="dev-user")

logger = logging.getLogger(__name__)

# ================================================
# TOOL FUNCTIONS
# Data comes from InMemoryStore (data_store.py) — no hardcoded values here.
# User identity is injected via _user_ctx ContextVar set in agentic_chat().
# ================================================

# ================================================
# TOOLS (MOCK FUNCTIONS)
# ================================================

def get_all_leave_balances() -> str:
    """Return ALL leave balances at once — guna bila user tanya secara umum."""
    store = get_store()
    uid = _user_ctx.get()
    balances = store.get_leave_balances(uid)
    lines = [f"- {k}: {v} hari" for k, v in balances.items()]
    return "Baki cuti kau:\n" + "\n".join(lines)

def check_leave_balance(leave_type: str = "Annual") -> str:
    store = get_store()
    uid = _user_ctx.get()
    balance = store.get_leave_balance(uid, leave_type)
    return f"Baki cuti {leave_type} kau ada {balance} hari lagi bro. 🌴"

def apply_leave(leave_type: str, start_date: str, end_date: str, reason: str) -> str:
    try:
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(end_date, "%Y-%m-%d")
        total_days = max(1, (d2 - d1).days + 1)  # inclusive, minimum 1
    except Exception:
        total_days = 1
    store = get_store()
    uid = _user_ctx.get()
    new_balance = store.deduct_leave(uid, leave_type, total_days)
    store.add_leave_application(uid, leave_type, start_date, end_date, reason, total_days)
    return f"Cun! Cuti {leave_type} dari {start_date} ke {end_date} ({total_days} hari) dah didaftarkan! Baki baru: {new_balance} hari. 🤞"

def check_room_availability(room_name: str, date: str, start_time: str, end_time: str) -> str:
    store = get_store()
    available = store.is_room_available(room_name, date, start_time, end_time)
    if available:
        return f"Bilik {room_name} available pada {date} ({start_time}-{end_time}). Nak book terus? 🏢✅"
    existing = store.get_room_bookings(room_name, date)
    taken_slots = ", ".join(f"{b['start_time']}-{b['end_time']}" for b in existing)
    return f"Bilik {room_name} dah ada booking pada {date} untuk slot {taken_slots}. Cuba masa atau bilik lain? 🏢⚠️"

def book_room(room_name: str, date: str, start_time: str, end_time: str, purpose: str) -> str:
    store = get_store()
    uid = _user_ctx.get()
    if not store.is_room_available(room_name, date, start_time, end_time):
        return f"Alamak, bilik {room_name} dah clash dengan booking lain pada {date} ({start_time}-{end_time}). Cuba slot atau bilik lain! 🏢❌"
    record = store.add_room_booking(uid, room_name, date, start_time, end_time, purpose)
    return f"Settled! Bilik {room_name} dah dibooking (ID: {record['id']}) pada {date} ({start_time}-{end_time}). 🗓️✅"

def check_claim_status() -> str:
    store = get_store()
    uid = _user_ctx.get()
    pending = store.get_claims(uid, status="pending")
    all_claims = store.get_claims(uid)
    if not pending:
        total = len(all_claims)
        if total == 0:
            return "Kau takde claim langsung lagi. Nak submit claim baru? 💸"
        return f"Semua {total} claim kau dah setel! Takde yang pending. 💸✅"
    total_pending = sum(c["amount"] for c in pending)
    return f"Kau ada {len(pending)} claim pending (jumlah RM{total_pending:.2f}). Claim terkini: RM{pending[-1]['amount']:.2f} untuk {pending[-1]['type']}. 💸"

def get_transport_options() -> str:
    store = get_store()
    fleet = store.transport_fleet
    options = ", ".join(f"{v['type']} ({v['capacity']})" for v in fleet)
    return f"Kita ada {options}. Semua ready to go! 🚐💨"

def book_transport(vehicle_type: str, destination: str, date: str, time: str, reason: str) -> str:
    store = get_store()
    uid = _user_ctx.get()
    record = store.add_transport_booking(uid, vehicle_type, destination, date, time, reason)
    return f"Onz! Transport {vehicle_type} ke {destination} pada {date} ({time}) dah dibooking (ID: {record['id']})! Driver akan contact kau nanti. 🚐✨"

def get_daily_menu() -> str:
    store = get_store()
    today = datetime.now().strftime("%A")
    menu = store.daily_menu.get(today, "Menu belum update untuk hari ni. 😋")
    return f"Menu Cafe Chin Hin harini ({today}): **{menu}**. Jemput makan bro! 🍛"

def get_energy_consumption(month: str = "March") -> str:
    store = get_store()
    usage = store.energy_stats.get(month, 0)
    if usage == 0:
        return f"Data energy untuk bulan {month} belum ada lagi. ⚡"
    return f"Usage energy office bulan {month} adalah {usage} kWh. Jimat sikit aircond tu k? ⚡🔋"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_all_leave_balances",
            "description": "Get ALL leave balances (Annual, Medical, Emergency) at once. Use this when user asks 'berapa cuti aku ada', 'check cuti', 'leave balance' or any general leave inquiry WITHOUT specifying a type. Do NOT ask for leave type — just call this immediately."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_leave_balance",
            "description": "Check leave days for ONE specific leave type. Only use if user EXPLICITLY mentions a specific type (Annual/Medical/Emergency).",
            "parameters": {
                "type": "object",
                "properties": {
                    "leave_type": {"type": "string", "enum": ["Annual", "Medical", "Emergency"]}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_leave",
            "description": "Apply for leave. SENSITIVE: Needs confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "leave_type": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["leave_type", "start_date", "end_date", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_room_availability",
            "description": "Check if a room is available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_name": {"type": "string"},
                    "date": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_room",
            "description": "Book a room. SENSITIVE: Needs confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_name": {"type": "string"},
                    "date": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "purpose": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_claim_status",
            "description": "Check pending claims."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_transport_options",
            "description": "Check available transport vehicles (Van, MPV, Sedan)."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_transport",
            "description": "Book a transport vehicle. SENSITIVE: Needs confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_type": {"type": "string"},
                    "destination": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["vehicle_type", "destination", "date", "time", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_menu",
            "description": "Get today's cafe menu at Chin Hin office."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_energy_consumption",
            "description": "Get monthly energy consumption data for the office.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {"type": "string"}
                }
            }
        }
    }
]

SENSITIVE_TOOLS = ["apply_leave", "book_room", "book_transport"]

# ================================================
# CARD DATA GENERATORS (for interactive UI cards)
# ================================================

def _get_card_action(fn_name: str, fn_args: dict) -> Optional[dict]:
    """Returns structured card data for info tools to render interactive UI cards."""
    if fn_name in ("get_all_leave_balances", "check_leave_balance"):
        store = get_store()
        uid = _user_ctx.get()
        return {
            "type": "leave_balance_card",
            "balances": store.get_leave_balances(uid),
            "quick_replies": [
                "Apply Annual Leave 🏖️",
                "Apply Medical Leave 💊",
                "Apply Emergency Leave 🚨"
            ]
        }
    elif fn_name == "get_transport_options":
        store = get_store()
        return {
            "type": "vehicle_picker",
            "vehicles": store.transport_fleet,
        }
    elif fn_name == "get_daily_menu":
        store = get_store()
        today = datetime.now().strftime("%A")
        return {
            "type": "menu_card",
            "day": today,
            "menu": store.daily_menu.get(today, "Menu belum update untuk hari ni 😋")
        }
    elif fn_name == "get_energy_consumption":
        store = get_store()
        month = fn_args.get("month", "March")
        return {
            "type": "energy_card",
            "current_month": month,
            "current_usage": store.energy_stats.get(month, 0),
            "all_stats": store.energy_stats
        }
    elif fn_name == "check_claim_status":
        store = get_store()
        uid = _user_ctx.get()
        return {
            "type": "claims_card",
            "claims": store.get_claims(uid)
        }
    elif fn_name == "check_room_availability":
        room = fn_args.get("room_name", "bilik ini")
        return {
            "type": "quick_replies",
            "replies": [
                f"Book {room} sekarang ✅",
                "Check masa lain 🕐",
                "Check bilik lain 🏢"
            ]
        }
    return None

# ================================================
# AGENT MANAGER
# ================================================

class ChatAgentManager:
    def __init__(self):
        self._settings = None
        self._client = None
        self.system_prompt = """# Role & Persona
Kau adalah "CHEA" (Chin Hin Employee Assistant) — AI assistant yang smart, helpful, dan friendly untuk semua staff Chin Hin Group! 🚀

## Personality
- Tone: Professional tapi conversational. Guna Gen Z casual dalam Bahasa Melayu. Emoji bila sesuai (🚀, 🚐, 🍽️, ⚡).
- Bahasa: Utama Bahasa Melayu, mix dengan English secara natural dan Gen Z.
- Jangan over-formal. Cakap macam bestie kat office yang bijak.

## ⚠️ CRITICAL: Context Retention (MOST IMPORTANT RULE)
Kau MESTI ingat context dari mesej-mesej sebelum ini dalam conversation:
- Kalau user sedang dalam proses apply leave, dan dia hantar tarikh atau maklumat lain → ANGGAP ia untuk leave tu, JANGAN tanya balik tujuan.
- Kalau user sedang proses book transport dan dia hantar tarikh → ANGGAP untuk transport booking tu.
- Kalau kau dah tanya soalan spesifik (e.g., "Tarikh mula?") dan user reply dengan tarikh → TERUS sambung, jangan minta penjelasan lagi.
- NEVER reset conversation context. Kalau user bagi info step by step, kumpul info tu sampai lengkap.
- Kalau rasa context lost, refer balik ke mesej awal conversation, bukan tanya dari scratch.

## Thinking Process (Chain of Thought)
ALWAYS fikir step-by-step sebelum jawab:
1. **Analisis**: Tengok full conversation history. Apa yang user nak dari AWAL? Jangan judge dari mesej terakhir je.
2. **Context Check**: Ada ongoing request ke? (e.g., tengah gather dates untuk leave, atau destination untuk transport?)
3. **Info Gathering**: Kalau info masih tak lengkap, tanya SATU soalan je pada satu masa. Jangan tanya semua sekali gus.
4. **Tool Decision**: Bila semua info dah ada → call tool.
   - SENSITIVE (apply_leave, book_room, book_transport): MESTI call tool, biar sistem tunjuk confirmation card.
   - TIDAK SENSITIVE (check_leave_balance, get_daily_menu, dll): Execute terus.
5. **Response**: Ringkas, friendly, actionable.

## Implementation Modules & Tools

### 1. Leave Management 🏖️
- Tools: `check_leave_balance` (immediate), `apply_leave` (SENSITIVE).
- Logic: Check baki cuti dulu sebelum apply. Kumpul: leave_type, start_date, end_date, reason. Bila dah lengkap, CALL `apply_leave`.
- **Gather info satu soalan masa**: Tanya leave_type dulu → then start_date → then end_date → then reason.

### 2. Room Booking 🏢
- Tools: `check_room_availability` (immediate), `book_room` (SENSITIVE).
- Kumpul: room_name, date, start_time, end_time, purpose.

### 3. Transport Booking 🚐
- Tools: `get_transport_options` (immediate), `book_transport` (SENSITIVE).
- Kumpul: vehicle_type, destination, date, time, reason.
- MESTI tanya destination kalau takde.

### 4. Daily Menu 🍛
- Tool: `get_daily_menu` (immediate).

### 5. Energy Consumption ⚡
- Tool: `get_energy_consumption` (immediate).

### 6. Claims 💸
- Tool: `check_claim_status` (immediate).

## Human-in-the-Loop (HITL) Logic 🛡️
Untuk SENSITIVE tools:
1. CALL THE TOOL — jangan execute dalam kepala kau.
2. Selepas call: "Okay, aku dah sediakan details. Kau check dulu kat card bawah ni, kalau betul tekan 'Confirm' k? 😎"
3. TUNGGU user click button.

## Guardrails
- Kalau user cakap "Confirm" / "Proceed" → acknowledge dan process.
- Kalau user cakap "Cancel" → stop dan inform.
- ONLY guna tools yang provided. JANGAN hallucinate data.
- Semua date format: YYYY-MM-DD, time format: HH:MM.
- Jangan tanya soalan yang dah user jawab dalam mesej sebelumnya.
"""

    @property
    def settings(self):
        if self._settings is None:
            self._settings = get_settings()
        return self._settings

    @property
    def client(self):
        if self._client is None:
            self._client = AzureOpenAI(
                api_key=self.settings.azure_openai_api_key,
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_version=self.settings.azure_openai_api_version
            )
        return self._client

    def process_chat(self, history: List[Dict], user_id: str) -> Dict[str, Any]:
        client = self.client
        deployment = self.settings.azure_openai_deployment
        
        # 1. Detect Confirmation (More robust check)
        last_msg = history[-1]["content"].lower()
        keywords = ["confirm", "yes", "jadi", "boleh", "proceed", "teruskan", "setuju"]
        is_confirmation = any(word in last_msg for word in keywords)

        store = get_store()
        if is_confirmation and store.has_pending(user_id):
            pending = store.pop_pending(user_id)
            tool_name = pending["name"]
            tool_args = pending["args"]
            
            logger.info(f"✅ User Confirmed! Executing {tool_name}")
            
            fn_map = {
                "apply_leave": apply_leave,
                "book_room": book_room,
                "book_transport": book_transport
            }
            result = fn_map[tool_name](**tool_args)
            return {"response": result, "actions": []}

        # 2. Main AI Loop
        try:
            response = client.chat.completions.create(
                model=deployment,
                messages=history,
                tools=TOOLS,
                tool_choice="auto"
            )
        except BadRequestError as e:
            # Handle Azure content filter gracefully
            error_body = e.response.json() if hasattr(e, 'response') else {}
            inner = error_body.get('error', {}).get('innererror', {})
            if inner.get('code') == 'ResponsibleAIPolicyViolation':
                logger.warning(f"⚠️ Azure content filter triggered: {inner}")
                return {
                    "response": "Alamak, soalan kau terkena content filter Azure OpenAI. Cuba ayat semula dengan cara yang lebih neutral ya bestie. 🙏",
                    "actions": []
                }
            raise
        
        ai_msg = response.choices[0].message
        
        if ai_msg.tool_calls:
            actions = []
            for tool_call in ai_msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                
                # Check for sensitive tools
                if fn_name in SENSITIVE_TOOLS:
                    # Store as pending
                    get_store().set_pending(user_id, {"name": fn_name, "args": fn_args})
                    actions.append({
                        "type": "confirmation",
                        "tool": fn_name,
                        "args": fn_args,
                        "prompt": f"Betul ke nak {fn_name.replace('_', ' ')} ni? Sila tekan Confirm kat bawah k? ✨"
                    })
                else:
                    # Execute immediate
                    fn_map = {
                        "get_all_leave_balances": get_all_leave_balances,
                        "check_leave_balance": check_leave_balance,
                        "check_room_availability": check_room_availability,
                        "check_claim_status": check_claim_status,
                        "get_transport_options": get_transport_options,
                        "get_daily_menu": get_daily_menu,
                        "get_energy_consumption": get_energy_consumption
                    }
                    if fn_name in fn_map:
                        result = fn_map[fn_name](**fn_args)
                        card_action = _get_card_action(fn_name, fn_args)
                        card_actions = [card_action] if card_action else []
                        return {"response": result, "actions": card_actions}
            
            if actions:
                # Get the content from AI msg if it exists, otherwise use a generic prompt
                content = ai_msg.content or f"Ok bestie, aku dah plan nak {actions[0]['tool'].replace('_', ' ')}. Tapi kena verify dulu k? ✨"
                return {
                    "response": content,
                    "actions": actions
                }

        return {"response": ai_msg.content, "actions": []}

_manager = ChatAgentManager()

# ================================================
# MAIN INTERFACE
# ================================================

_history_cache: Dict[str, List[Dict]] = {}

async def agentic_chat(
    message: str,
    user_id: str,
    conversation_id: str = None,
    history: Optional[list] = None,
    image_data: Optional[str] = None
) -> dict:
    conv_id = conversation_id or "default"
    _user_ctx.set(user_id)  # Inject user identity into tool functions via ContextVar

    # Build history — always with system prompt at front
    if history:
        # History dari client (Flutter) — check if system prompt already there
        has_system = any(m.get("role") == "system" for m in history)
        base = history if has_system else [{"role": "system", "content": _manager.system_prompt}] + history
        current_history = base + [{"role": "user", "content": message}]
    else:
        if conv_id not in _history_cache:
            _history_cache[conv_id] = [{"role": "system", "content": _manager.system_prompt}]
        _history_cache[conv_id].append({"role": "user", "content": message})
        current_history = _history_cache[conv_id]
    
    try:
        result = _manager.process_chat(current_history, user_id)
        response_text = result["response"]
        actions = result.get("actions", [])
        
        if not history:
            _history_cache[conv_id].append({"role": "assistant", "content": response_text})
        
        return {
            "response": response_text,
            "actions": actions, 
            "conversation_id": conv_id
        }
        
    except BadRequestError as e:
        error_body = e.response.json() if hasattr(e, 'response') else {}
        inner = error_body.get('error', {}).get('innererror', {})
        if inner.get('code') == 'ResponsibleAIPolicyViolation':
            logger.warning(f"⚠️ Content filter triggered at top level: {inner}")
            return {
                "response": "Alamak, soalan kau terkena content filter Azure OpenAI. Cuba ayat semula dengan cara yang lebih neutral ya bestie. 🙏",
                "actions": [],
                "conversation_id": conv_id
            }
        logger.error(f"Azure BadRequestError: {e}")
        return {
            "response": "❌ Ada masalah dengan AI service sekarang. Cuba sekali lagi ya!",
            "actions": [],
            "error": "bad_request"
        }
    except Exception as e:
        logger.error(f"Chat Agent error: {e}")
        return {
            "response": "❌ Alamak, ada error jap. Cuba balik sekejap lagi ya! 🙏",
            "actions": [],
            "error": str(type(e).__name__)
        }
