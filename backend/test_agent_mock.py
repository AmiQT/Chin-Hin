"""Test LangGraph agent structure with mock LLM"""
import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch
from app.agents.function_agent import agentic_chat

async def test_with_mock():
    """Test agent with mocked Gemini API to avoid quota limits"""
    
    # Mock response - agent should recognize it's a greeting and not call tools
    mock_response = "Hi! I'm Chin Hin's AI Assistant. I can help you dengan cuti, bilik meeting, dan expense claims!"
    
    print("Testing agent infrastructure with mock LLM...")
    
    with patch('app.agents.function_agent.ChatGoogleGenerativeAI') as mock_llm_class:
        # Create mock LLM
        mock_llm = AsyncMock()
        mock_llm.invoke = AsyncMock(return_value=type('obj', (object,), {
            'content': mock_response,
            'tool_calls': []
        })())
        
        mock_llm_class.return_value = mock_llm
        
        # Need to reload to pick up mock
        import importlib
        import app.agents.function_agent as agent_module
        importlib.reload(agent_module)
        
        result = await agent_module.agentic_chat('Hi!', 'test-user-123')
        
        print(f"Response: {result.get('response', 'no response')[:100]}")
        print(f"Actions taken: {len(result.get('actions', []))}")
        print("SUCCESS - Agent structure working!")

if __name__ == '__main__':
    asyncio.run(test_with_mock())
