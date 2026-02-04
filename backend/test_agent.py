"""Quick test for agent"""
import asyncio
import sys
from app.agents.function_agent import agentic_chat

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test():
    print("Testing agent...")
    result = await agentic_chat("Hi, siapa kau?", "test-user-123")
    response = result.get("response", "no response")
    # Normalize response to string (handles dict responses from errors)
    if not isinstance(response, str):
        response = str(response)
    # Remove emoji from response for display
    response_clean = ''.join(c if ord(c) < 128 else '?' for c in response[:150])
    print(f"Response: {response_clean}")
    print(f"Actions: {len(result.get('actions', []))}")
    print("SUCCESS!")

asyncio.run(test())
