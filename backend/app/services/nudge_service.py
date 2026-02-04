"""
Nudge Service - Proactive Employee Reminders.
Handles generation and delivery of AI-driven nudges.
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class NudgeService:
    """Service to manage proactive nudges."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_user_nudges(self, user_id: str, only_unread: bool = True) -> List[dict]:
        """Fetch nudges for a specific user."""
        query = self.supabase.table("nudges").select("*").eq("user_id", user_id)
        if only_unread:
            query = query.eq("is_read", False)
        
        result = query.order("created_at", desc=True).execute()
        return result.data
    
    async def mark_as_read(self, nudge_id: str):
        """Mark a nudge as read."""
        self.supabase.table("nudges").update({"is_read": True}).eq("id", nudge_id).execute()
        
    async def create_nudge(self, user_id: str, nudge_type: str, title: str, content: str, metadata: dict = None):
        """Create a new nudge for a user."""
        data = {
            "user_id": user_id,
            "type": nudge_type,
            "title": title,
            "content": content,
            "metadata": metadata or {}
        }
        result = self.supabase.table("nudges").insert(data).execute()
        return result.data[0] if result.data else None

    async def scan_for_nudges(self):
        """
        Background logic to scan DB and identify users who need nudging.
        Examples:
        - Pending claims > 7 days
        - Very high leave balance (un-used)
        - Room booking starting in 15 mins
        """
        logger.info("🤖 Nudge Engine: Scanning for work...")
        # 1. Check for old pending claims
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        old_claims = self.supabase.table("claims").select("*, users!claims_user_id_fkey(id, full_name)").eq("status", "pending").lt("created_at", seven_days_ago).execute()
        
        for claim in old_claims.data:
            user_id = claim["user_id"]
            claim_id = claim["id"]
            
            # Check if we already nudged for this claim recently
            existing = self.supabase.table("nudges").select("id").eq("user_id", user_id).eq("type", "claim_reminder").eq("metadata->>claim_id", claim_id).execute()
            
            if not existing.data:
                await self.create_nudge(
                    user_id=user_id,
                    nudge_type="claim_reminder",
                    title="Claim Belum Settle! 💸",
                    content=f"Eh {claim.get('users', {}).get('full_name', 'pawn')}, claim kau RM{claim['amount']} dah sangkut 7 hari ni. Dah submit resit ke belum?",
                    metadata={"claim_id": claim_id}
                )

# Singleton
_nudge_service: Optional[NudgeService] = None

def get_nudge_service() -> NudgeService:
    global _nudge_service
    if _nudge_service is None:
        _nudge_service = NudgeService()
    return _nudge_service
