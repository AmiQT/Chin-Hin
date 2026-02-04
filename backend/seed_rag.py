import asyncio
from app.services.embedding_service import get_embedding_service
from app.db.supabase_client import get_supabase_client

HR_POLICIES = [
    {
        "content": "Pekerja Chin Hin layak mendapat 14 hari cuti sakit (MC) setahun untuk perkhidmatan kurang 2 tahun, 18 hari untuk 2-5 tahun, dan 22 hari untuk lebih 5 tahun.",
        "metadata": {"category": "Medical", "topic": "Sick Leave"}
    },
    {
        "content": "Claim makan (Meals) mempunyai had maksimum RM50 sehari selagi mempunyai resit yang sah. Alkhohol tidak boleh di-claim.",
        "metadata": {"category": "Claims", "topic": "Meal Allowance"}
    },
    {
        "content": "Waktu bekerja rasmi HQ Chin Hin adalah dari 8:30 AM hingga 5:30 PM, Isnin hingga Jumaat.",
        "metadata": {"category": "General", "topic": "Working Hours"}
    },
    {
        "content": "Bagi tuntutan perjalanan (Mileage), kadar adalah RM0.60 per KM untuk kereta dan RM0.30 per KM untuk motorsikal.",
        "metadata": {"category": "Claims", "topic": "Mileage"}
    }
]

async def seed_knowledge_base():
    print("🌱 Seeding HR Policy Knowledge Base...")
    embedding_service = get_embedding_service()
    supabase = get_supabase_client()
    
    for policy in HR_POLICIES:
        print(f"Propcessing: {policy['content'][:50]}...")
        vector = await embedding_service.get_embeddings(policy['content'])
        
        if vector:
            data = {
                "content": policy['content'],
                "metadata": policy['metadata'],
                "embedding": vector
            }
            try:
                supabase.table("knowledge_base").insert(data).execute()
                print("✅ Inserted!")
            except Exception as e:
                print(f"❌ Supabase Error: {e}")
                print("⚠️ Make sure you have run the SQL migration 003_knowledge_base.sql in Supabase Dashboard first!")
                break
        else:
            print("❌ Failed to get embedding")

if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
