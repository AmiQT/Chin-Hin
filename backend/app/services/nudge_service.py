"""Nudge Service - Proactive Employee Reminders. In-memory, no Supabase."""

import uuid
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# No pre-seeded nudges with hardcoded data.
# Nudges are generated dynamically via scan_for_nudges() using real data_store values.
_nudges: list = []


class NudgeService:
    async def get_user_nudges(self, user_id: str, only_unread: bool = True) -> List[dict]:
        result = [n for n in _nudges if n["user_id"] == user_id]
        if only_unread:
            result = [n for n in result if not n.get("is_read", False)]
        return sorted(result, key=lambda x: x.get("created_at", ""), reverse=True)

    async def mark_as_read(self, nudge_id: str):
        for n in _nudges:
            if n["id"] == nudge_id:
                n["is_read"] = True
                break

    async def create_nudge(self, user_id: str, nudge_type: str, title: str, content: str, metadata: dict = None) -> dict:
        nudge = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": nudge_type,
            "title": title,
            "content": content,
            "is_read": False,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        _nudges.append(nudge)
        logger.info(f"Nudge created for {user_id}: {title}")
        return nudge

    async def scan_for_nudges(self):
        """Scan data_store for conditions that warrant a nudge and auto-create them."""
        from app.services.data_store import get_store
        store = get_store()
        logger.info("Nudge Engine: Scanning all users...")

        # Check each user who has leave balance data
        for user_id, balances in store._leave_balances.items():
            existing_ids = {n["type"] + n["user_id"] for n in _nudges if not n["is_read"]}

            # Nudge: Annual leave still high (>= 10 days) — remind them to use it
            annual = balances.get("Annual", 0)
            if annual >= 10 and f"leave_reminder{user_id}" not in existing_ids:
                await self.create_nudge(
                    user_id=user_id,
                    nudge_type="leave_reminder",
                    title="Baki Cuti Masih Banyak!",
                    content=f"Eh, kau ada {annual} hari cuti tahunan lagi. Jangan bagi expired! 🌴",
                    metadata={"leave_type": "Annual", "balance": annual},
                )

            # Nudge: Medical leave very low (<= 2 days)
            medical = balances.get("Medical", 0)
            if medical <= 2 and f"medical_low{user_id}" not in existing_ids:
                await self.create_nudge(
                    user_id=user_id,
                    nudge_type="medical_low",
                    title="Cuti Sakit Hampir Habis!",
                    content=f"Cuti Medical kau tinggal {medical} hari je lagi. Jaga kesihatan tau! 💚",
                    metadata={"leave_type": "Medical", "balance": medical},
                )

        logger.info(f"Nudge Engine: Done. Total nudges: {len(_nudges)}")


_nudge_service: Optional[NudgeService] = None


def get_nudge_service() -> NudgeService:
    global _nudge_service
    if _nudge_service is None:
        _nudge_service = NudgeService()
    return _nudge_service
