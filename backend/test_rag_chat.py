import asyncio
from app.agents.function_agent import agentic_chat

async def test_rag():
    print("🔍 Testing RAG (Policy Search)...")
    user_id = "11111111-1111-1111-1111-111111111111"
    
    # Question about sick leave (was in seed data)
    question = "Berapa hari saya boleh dapat MC setahun?"
    print(f"User: {question}")
    
    response = await agentic_chat(question, user_id)
    print(f"AI: {response['response']}")
    
    if "14 hari" in response['response'] or "MC" in response['response']:
        print("\n✅ RAG works! AI fetched the policy.")
    else:
        print("\n❌ RAG might have issues. AI didn't seem to fetch the correct policy.")

if __name__ == "__main__":
    asyncio.run(test_rag())
