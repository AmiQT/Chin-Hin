"""
Central In-Memory Data Store
============================
Acts as the mock database for development — replaces Supabase in dev mode.
All agents and services read/write through this single store (per-user state).
Swap get_store() with a real DB service later without changing agent code.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional


class InMemoryStore:
    def __init__(self):
        # {user_id: {leave_type: remaining_days}}
        self._leave_balances: Dict[str, Dict[str, int]] = {}
        self._default_leave = {"Annual": 14, "Medical": 14, "Emergency": 5}

        # Leave application history
        self._leave_applications: List[dict] = []

        # Room bookings
        self._room_bookings: List[dict] = []

        # Claims per user
        self._claims: Dict[str, List[dict]] = {}

        # Transport bookings
        self._transport_bookings: List[dict] = []

        # Vehicle fleet config — updated by admin (type, capacity, emoji)
        self.transport_fleet: List[dict] = [
            {"type": "Van",   "capacity": "10 pax", "emoji": "🚐"},
            {"type": "MPV",   "capacity": "6 pax",  "emoji": "🚙"},
            {"type": "Sedan", "capacity": "4 pax",  "emoji": "🚗"},
        ]

        # Pending HITL confirmations per user_id
        self._pending_actions: Dict[str, dict] = {}

        # Static rooms catalogue — updated by admin
        self.rooms: List[dict] = [
            {"id": "room-1", "name": "Bilik Helang",   "capacity": 10, "floor": "L3", "is_active": True},
            {"id": "room-2", "name": "Bilik Merbok",   "capacity": 6,  "floor": "L2", "is_active": True},
            {"id": "room-3", "name": "Bilik Kelinci",  "capacity": 4,  "floor": "L1", "is_active": True},
            {"id": "room-4", "name": "Boardroom Utama","capacity": 20, "floor": "L4", "is_active": True},
        ]

        # Static claim categories
        self.claim_categories: List[dict] = [
            {"id": "cat-1", "name": "Meal",       "max_amount": 50.0,   "is_active": True},
            {"id": "cat-2", "name": "Travel",     "max_amount": 500.0,  "is_active": True},
            {"id": "cat-3", "name": "Parking",    "max_amount": 30.0,   "is_active": True},
            {"id": "cat-4", "name": "Stationery", "max_amount": 100.0,  "is_active": True},
            {"id": "cat-5", "name": "Medical",    "max_amount": 1000.0, "is_active": True},
        ]

        # Static leave types
        self.leave_types: List[dict] = [
            {"id": "lt-1", "name": "Annual",    "default_days": 14, "is_active": True},
            {"id": "lt-2", "name": "Medical",   "default_days": 14, "is_active": True},
            {"id": "lt-3", "name": "Emergency", "default_days": 5,  "is_active": True},
        ]

        # Daily menu — configuration data, updated by admin
        self.daily_menu: Dict[str, str] = {
            "Monday":    "Nasi Lemak Ayam Berempah + Teh Tarik 🍛",
            "Tuesday":   "Mee Goreng Mamak + Limau Ais 🍝",
            "Wednesday": "Chicken Chop + Mushroom Soup 🥩",
            "Thursday":  "Nasi Kandar + Sirap Bandung 🍛",
            "Friday":    "Laksa Utara + Cendol 🥣",
            "Saturday":  "Nasi Goreng Kampung + Teh O Ais 🍳",
            "Sunday":    "Nasi Ayam Hainan + Sup Sayur + Air Sirap Ros 🍚",
        }

        # Energy stats (kWh per month) — updated by facilities team
        self.energy_stats: Dict[str, int] = {
            "January": 4500, "February": 4800, "March": 4200,
            "April": 3900,   "May": 4100,      "June": 4300,
            "July": 4000,    "August": 4150,   "September": 4050,
            "October": 4250, "November": 4400, "December": 4600,
        }

        # ── Seed demo data for recording ──────────────────────────────────────
        _DEMO_USER = "11111111-1111-1111-1111-111111111111"

        # Leave balance — 3 days already used from Annual
        self._leave_balances[_DEMO_USER] = {"Annual": 11, "Medical": 14, "Emergency": 5}

        # Leave applications history
        self._leave_applications = [
            {
                "id": "lv-001",
                "user_id": _DEMO_USER,
                "leave_type": "Annual",
                "start_date": "2026-02-10",
                "end_date": "2026-02-12",
                "reason": "Family vacation",
                "days": 3,
                "status": "approved",
                "created_at": "2026-02-05T09:00:00",
            },
            {
                "id": "lv-002",
                "user_id": _DEMO_USER,
                "leave_type": "Medical",
                "start_date": "2026-03-15",
                "end_date": "2026-03-15",
                "reason": "Doctor appointment",
                "days": 1,
                "status": "pending",
                "created_at": "2026-03-07T10:30:00",
            },
        ]

        # Claims history
        self._claims[_DEMO_USER] = [
            {
                "id": "cl-001",
                "user_id": _DEMO_USER,
                "category_id": "cat-1",
                "category_name": "Meal",
                "amount": 45.50,
                "description": "Team lunch at Pizza Hut",
                "claim_date": "2026-02-20",
                "status": "approved",
                "created_at": "2026-02-20T13:00:00",
            },
            {
                "id": "cl-002",
                "user_id": _DEMO_USER,
                "category_id": "cat-2",
                "category_name": "Travel",
                "amount": 120.00,
                "description": "Grab ke customer site KL Sentral",
                "claim_date": "2026-03-05",
                "status": "pending",
                "created_at": "2026-03-05T17:00:00",
            },
        ]

        # Room bookings history
        self._room_bookings = [
            {
                "id": "bk-001",
                "user_id": _DEMO_USER,
                "room_name": "Bilik Helang",
                "date": "2026-03-09",
                "start_time": "10:00",
                "end_time": "12:00",
                "purpose": "Weekly team standup",
                "status": "confirmed",
                "created_at": "2026-03-07T08:00:00",
            },
        ]

    # ── Leave Balance ──────────────────────────────────────────────────────────

    def get_leave_balances(self, user_id: str) -> Dict[str, int]:
        """Get all leave type balances for a user. Auto-initialises with defaults."""
        if user_id not in self._leave_balances:
            self._leave_balances[user_id] = dict(self._default_leave)
        return self._leave_balances[user_id]

    def get_leave_balance(self, user_id: str, leave_type: str) -> int:
        return self.get_leave_balances(user_id).get(leave_type, 0)

    def deduct_leave(self, user_id: str, leave_type: str, days: int) -> int:
        """Deduct days from balance. Returns new balance."""
        bal = self.get_leave_balances(user_id)
        bal[leave_type] = max(0, bal.get(leave_type, 0) - days)
        return bal[leave_type]

    def add_leave_application(
        self,
        user_id: str,
        leave_type: str,
        start_date: str,
        end_date: str,
        reason: str,
        days: int,
    ) -> dict:
        record = {
            "id": str(uuid.uuid4())[:8],
            "user_id": user_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
            "days": days,
            "status": "approved",
            "created_at": datetime.now().isoformat(),
        }
        self._leave_applications.append(record)
        return record

    def get_leave_applications(self, user_id: str, status: Optional[str] = None) -> List[dict]:
        apps = [a for a in self._leave_applications if a["user_id"] == user_id]
        if status:
            apps = [a for a in apps if a["status"] == status]
        return apps

    def get_all_leave_applications(self, status: Optional[str] = None) -> List[dict]:
        apps = list(self._leave_applications)
        if status:
            apps = [a for a in apps if a["status"] == status]
        return apps

    def update_leave_application(self, leave_id: str, status: str, actor_id: str) -> Optional[dict]:
        for app in self._leave_applications:
            if app["id"] == leave_id:
                app["status"] = status
                app["actioned_by"] = actor_id
                app["actioned_at"] = datetime.now().isoformat()
                # If rejecting, restore days to balance
                if status == "rejected":
                    self._leave_balances.get(app["user_id"], {})
                    balances = self.get_leave_balances(app["user_id"])
                    balances[app["leave_type"]] = balances.get(app["leave_type"], 0) + app.get("days", 0)
                return app
        return None

    # ── Room Bookings ──────────────────────────────────────────────────────────

    def is_room_available(
        self, room_name: str, date: str, start_time: str, end_time: str
    ) -> bool:
        for b in self._room_bookings:
            if b["room_name"].lower() == room_name.lower() and b["date"] == date:
                # Overlap check: two slots overlap if not (end1<=start2 or start1>=end2)
                if not (end_time <= b["start_time"] or start_time >= b["end_time"]):
                    return False
        return True

    def get_room_bookings(self, room_name: str, date: str) -> List[dict]:
        return [
            b for b in self._room_bookings
            if b["room_name"].lower() == room_name.lower() and b["date"] == date
        ]

    def add_room_booking(
        self,
        user_id: str,
        room_name: str,
        date: str,
        start_time: str,
        end_time: str,
        purpose: str,
    ) -> dict:
        record = {
            "id": str(uuid.uuid4())[:8],
            "user_id": user_id,
            "room_name": room_name,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "purpose": purpose,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
        }
        self._room_bookings.append(record)
        return record

    def get_all_room_bookings(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
        bookings = list(self._room_bookings)
        if user_id:
            bookings = [b for b in bookings if b["user_id"] == user_id]
        if status:
            bookings = [b for b in bookings if b.get("status") == status]
        return bookings

    def cancel_room_booking(self, booking_id: str) -> Optional[dict]:
        for b in self._room_bookings:
            if b["id"] == booking_id:
                b["status"] = "cancelled"
                return b
        return None

    def get_room_booking_by_id(self, booking_id: str) -> Optional[dict]:
        return next((b for b in self._room_bookings if b["id"] == booking_id), None)

    def get_room_by_id(self, room_id: str) -> Optional[dict]:
        return next((r for r in self.rooms if r["id"] == room_id), None)

    # ── Claims ─────────────────────────────────────────────────────────────────

    def get_claims(self, user_id: str, status: Optional[str] = None) -> List[dict]:
        claims = self._claims.get(user_id, [])
        if status:
            claims = [c for c in claims if c["status"] == status]
        return claims

    def get_all_claims(self, status: Optional[str] = None, user_id: Optional[str] = None) -> List[dict]:
        all_claims = [c for claims in self._claims.values() for c in claims]
        if user_id:
            all_claims = [c for c in all_claims if c["user_id"] == user_id]
        if status:
            all_claims = [c for c in all_claims if c["status"] == status]
        return all_claims

    def add_claim(self, user_id: str, category_id: str = "", category_name: str = "", amount: float = 0.0, description: str = "", claim_date: str = "", claim_type: str = "") -> dict:
        record = {
            "id": str(uuid.uuid4())[:8],
            "user_id": user_id,
            "category_id": category_id,
            "category_name": category_name or claim_type,
            "amount": amount,
            "description": description,
            "claim_date": claim_date or datetime.now().strftime("%Y-%m-%d"),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        self._claims.setdefault(user_id, []).append(record)
        return record

    def update_claim_status(self, claim_id: str, status: str, actor_id: str) -> Optional[dict]:
        for claims in self._claims.values():
            for c in claims:
                if c["id"] == claim_id:
                    c["status"] = status
                    c["actioned_by"] = actor_id
                    c["actioned_at"] = datetime.now().isoformat()
                    return c
        return None

    def get_claim_by_id(self, claim_id: str) -> Optional[dict]:
        for claims in self._claims.values():
            for c in claims:
                if c["id"] == claim_id:
                    return c
        return None

    # ── Transport Bookings ─────────────────────────────────────────────────────

    def add_transport_booking(
        self,
        user_id: str,
        vehicle_type: str,
        destination: str,
        date: str,
        time: str,
        reason: str,
    ) -> dict:
        record = {
            "id": str(uuid.uuid4())[:8],
            "user_id": user_id,
            "vehicle": vehicle_type,
            "destination": destination,
            "date": date,
            "time": time,
            "reason": reason,
            "created_at": datetime.now().isoformat(),
        }
        self._transport_bookings.append(record)
        return record

    # ── Pending HITL ───────────────────────────────────────────────────────────

    def set_pending(self, user_id: str, action: dict) -> None:
        self._pending_actions[user_id] = action

    def pop_pending(self, user_id: str) -> Optional[dict]:
        return self._pending_actions.pop(user_id, None)

    def has_pending(self, user_id: str) -> bool:
        return user_id in self._pending_actions


# Singleton — shared across all requests in the process
_store = InMemoryStore()


def get_store() -> InMemoryStore:
    """Return the singleton data store."""
    return _store
