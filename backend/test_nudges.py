import asyncio
from datetime import datetime, timedelta
from app.db.supabase_client import get_supabase_client
from app.services.nudge_service import get_nudge_service
from app.agents.function_agent import agentic_chat

async def test_proactive_nudges():
    print("🔔 Testing Proactive Nudges...")
    supabase = get_supabase_client()
    nudge_service = get_nudge_service()
    
    # 1. Setup: Ensure we have a user and a 'stuck' claim
    user_id = "11111111-1111-1111-1111-111111111111"
    
    print("🧹 Cleaning up old test data...")
    supabase.table("nudges").delete().eq("user_id", user_id).execute()
    supabase.table("claims").delete().eq("user_id", user_id).eq("description", "Lunch with Client (Stuck Test)").execute()
    
    # Backdate a claim to 8 days ago
    eight_days_ago = (datetime.now() - timedelta(days=8)).isoformat()
    
    print("📍 Creating a stuck claim (8 days old)...")
    # We'll just manually insert a nudge for testing purposes if scanning is complex to trigger
    # But let's try to trigger the scan
    
    # Insert a dummy pending claim
    claim_data = {
        "user_id": user_id,
        "amount": 250.00,
        "description": "Lunch with Client (Stuck Test)",
        "status": "pending",
        "created_at": eight_days_ago
    }
    # Note: This might fail if constraints are strict, but let's try
    try:
        claim_result = supabase.table("claims").insert(claim_data).execute()
        print("✅ Stuck claim created!")
    except Exception as e:
        print(f"⚠️ Could not create stuck claim (maybe categories missing?): {e}")

    # 2. Run Nudge Scanner
    print("🤖 Running Nudge Scanner...")
    await nudge_service.scan_for_nudges()
    
    # 3. Check if nudge exists
    nudges = await nudge_service.get_user_nudges(user_id)
    print(f"📬 Unread nudges for user: {len(nudges)}")
    for n in nudges:
        print(f"  - [{n['type']}] {n['title']}: {n['content']}")

    # 4. Test AI Proactivity
    if nudges:
        print("\n💬 Testing AI Proactivity in Chat...")
        response = await agentic_chat("Hi AI, apa khabar?", user_id)
        print(f"AI Response: {response['response']}")
        
        if "claim" in response['response'].lower() or "RM250" in response['response']:
            print("\n🔥 SUCCESS: AI was proactive and mentioned the nudge!")
        else:
            print("\n⚠️ AI responded but didn't mention the nudge. Check system prompt or context injection.")
    else:
        print("\n❌ FAILED: No nudges generated. Check scan_for_nudges logic.")

if __name__ == "__main__":
    asyncio.run(test_proactive_nudges())
