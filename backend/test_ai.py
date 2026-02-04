import asyncio
import sys
from app.agents.function_agent import agentic_chat

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    print('?? AI AGENT TEST: Checking Leave Balance...')
    print('=' * 40)
    
    # Query: Baki cuti tahunan
    # User: Ahmad bin Hassan
    user_id = '11111111-1111-1111-1111-111111111111'
    query = 'Berapa baki cuti tahunan saya?'
    
    result = await agentic_chat(query, user_id)
    
    # Extract clean text from response
    raw_response = result.get("response")
    clean_text = ""
    if isinstance(raw_response, list):
        for msg in raw_response:
            if isinstance(msg, dict) and msg.get("type") == "text":
                clean_text += msg.get("text", "")
            else:
                clean_text += str(msg)
    else:
        clean_text = str(raw_response)

    print(f'\n💬 User: {query}')
    print(f'🤖 AI: {clean_text}')
    
    actions = result.get("actions", [])
    print(f'\n???  Actions Count: {len(actions)}')
    for i, action in enumerate(actions, 1):
        print(f'   {i}. Tool: {action.get("tool")}')
        print(f'      Args: {action.get("args")}')
    
    print('=' * 40)
    print('? AI AGENT VERIFIED!')

if __name__ == "__main__":
    asyncio.run(main())
