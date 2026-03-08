"""
Azure AI Foundry - Managed Agent
Guna azure-ai-agents SDK (auto-installed dengan azure-ai-projects)
"""
import logging
import asyncio
from typing import Optional
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, RunStatus
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from app.config import get_settings
from app.services.data_store import get_store

logger = logging.getLogger(__name__)

# ================================================
# TOOL FUNCTIONS (Agent boleh panggil ni)
# Data comes from shared InMemoryStore — no hardcoded responses.
# ================================================

_DEV_USER = "dev-user"  # Foundry agent default user in dev mode

def check_leave_balance(leave_type: str = "Annual") -> str:
    """Check baki cuti user. Guna bila user tanya berapa baki cuti."""
    balance = get_store().get_leave_balance(_DEV_USER, leave_type)
    return f"Baki cuti {leave_type}: {balance} hari tersedia."

def apply_leave(leave_type: str, start_date: str, end_date: str, reason: str) -> str:
    """Mohon cuti untuk user. Guna bila user nak apply cuti."""
    from datetime import datetime as _dt
    try:
        d1 = _dt.strptime(start_date, "%Y-%m-%d")
        d2 = _dt.strptime(end_date, "%Y-%m-%d")
        total_days = max(1, (d2 - d1).days + 1)
    except Exception:
        total_days = 1
    store = get_store()
    new_balance = store.deduct_leave(_DEV_USER, leave_type, total_days)
    store.add_leave_application(_DEV_USER, leave_type, start_date, end_date, reason, total_days)
    return f"Permohonan cuti {leave_type} dari {start_date} hingga {end_date} ({total_days} hari) berjaya dihantar! Baki baru: {new_balance} hari."

def check_room_availability(room_name: str, date: str, start_time: str, end_time: str) -> str:
    """Semak sama ada bilik mesyuarat available."""
    store = get_store()
    available = store.is_room_available(room_name, date, start_time, end_time)
    if available:
        return f"Bilik {room_name} available pada {date} dari {start_time} hingga {end_time}."
    existing = store.get_room_bookings(room_name, date)
    taken = ", ".join(f"{b['start_time']}-{b['end_time']}" for b in existing)
    return f"Bilik {room_name} tidak available pada {date}. Slot yang ditempah: {taken}."

def book_room(room_name: str, date: str, start_time: str, end_time: str, purpose: str) -> str:
    """Book bilik mesyuarat."""
    store = get_store()
    if not store.is_room_available(room_name, date, start_time, end_time):
        return f"Maaf, bilik {room_name} dah ditempah pada {date} ({start_time}-{end_time})."
    record = store.add_room_booking(_DEV_USER, room_name, date, start_time, end_time, purpose)
    return f"Bilik {room_name} berjaya dibooking (ID: {record['id']}) pada {date} ({start_time}-{end_time})."

def check_claim_status() -> str:
    """Semak status claims yang pending."""
    store = get_store()
    pending = store.get_claims(_DEV_USER, status="pending")
    if not pending:
        return "Tiada claim yang pending."
    total = sum(c["amount"] for c in pending)
    return f"Kau ada {len(pending)} claim pending, jumlah RM{total:.2f}. Claim terkini: RM{pending[-1]['amount']:.2f} ({pending[-1]['type']})."


class FoundryAgentManager:
    """Manager untuk Azure AI Foundry Managed Agent guna azure-ai-agents SDK."""

    def __init__(self):
        settings = get_settings()
        self.endpoint = settings.azure_openai_endpoint
        self.deployment = settings.azure_openai_deployment or "gpt-4o"
        self._client: Optional[AgentsClient] = None
        self._agent_id: Optional[str] = None

    def _get_client(self) -> AgentsClient:
        if self._client:
            return self._client
        settings = get_settings()
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT missing!")
        # Guna InteractiveBrowserCredential — akan buka browser sekali untuk login
        from azure.identity import InteractiveBrowserCredential
        credential = InteractiveBrowserCredential()
        self._client = AgentsClient(
            endpoint=self.endpoint,
            credential=credential
        )
        return self._client

    def get_or_create_agent(self):
        """Create Managed Agent kat Azure AI Foundry."""
        client = self._get_client()

        # Register tools
        functions = FunctionTool(functions=[
            check_leave_balance,
            apply_leave,
            check_room_availability,
            book_room,
            check_claim_status,
        ])
        toolset = ToolSet()
        toolset.add(functions)

        agent = client.create_agent(
            model=self.deployment,
            name="ChinHin-AI-Bestie",
            instructions="""Kau adalah AI Bestie untuk staff Chin Hin Group.
Tugas kau: tolong staff uruskan Cuti, Bilik Meeting, dan Claims.
Guna Bahasa Melayu dengan gaya yang friendly dan helpful.
Sentiasa guna tools yang ada untuk semak info sebenar.""",
            toolset=toolset
        )
        self._agent_id = agent.id
        logger.info(f"Azure Managed Agent created: {agent.id}")
        return agent

    def create_thread(self):
        """Create conversation thread."""
        client = self._get_client()
        return client.create_thread()

    def process_message(self, thread_id: str, message: str, agent_id: str) -> str:
        """Hantar message dan tunggu response dari agent."""
        client = self._get_client()

        # Hantar message dan process dalam satu call
        run = client.create_thread_and_process_run(
            assistant_id=agent_id,
            thread={
                "messages": [{"role": "user", "content": message}]
            }
        )

        if run.status == RunStatus.COMPLETED:
            messages = client.list_messages(thread_id=run.thread_id)
            for msg in messages:
                if msg.role == "assistant":
                    return msg.content[0].text.value
            return "Agent selesai tapi tiada response."
        else:
            return f"Agent status: {run.status}"


# ================================================
# SINGLETON
# ================================================
_foundry_manager: Optional[FoundryAgentManager] = None

def get_foundry_manager() -> FoundryAgentManager:
    global _foundry_manager
    if _foundry_manager is None:
        _foundry_manager = FoundryAgentManager()
    return _foundry_manager
