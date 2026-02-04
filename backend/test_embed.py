import asyncio
from app.services.embedding_service import get_embedding_service

async def test():
    print("Testing Embedding Service...")
    svc = get_embedding_service()
    vec = await svc.get_embeddings("Hello Chin Hin!")
    print(f"Vector length: {len(vec)}")
    if vec:
        print("✅ Embeddings work!")
    else:
        print("❌ Embeddings failed!")

if __name__ == "__main__":
    asyncio.run(test())
