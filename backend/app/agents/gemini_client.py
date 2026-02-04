"""
Gemini AI Client for Chin Hin Employee Assistant.
Handles chat completions using new google-genai SDK.
"""

from google import genai
from google.genai import types
from typing import Optional, List, Dict
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

# System prompt untuk employee assistant
SYSTEM_PROMPT = """Kau adalah Chin Hin AI Assistant - pembantu pintar untuk pekerja Chin Hin! 🤖

## Personality
- Friendly dan helpful, macam bestie kat office
- Boleh cakap BM dan English (mix pun ok!)
- Quick dan efficient - tak banyak cakap kosong

## Capabilities
Kau boleh bantu dengan:
1. **Leave Management** - Apply cuti, check balance, view requests
2. **Room Booking** - Book meeting room, check availability
3. **Expense Claims** - Submit claims, upload receipt, check status

## Response Style
- Guna emoji bila sesuai 😊
- Keep it short dan sweet
- Confirm sebelum buat action penting
- Kalau tak pasti, tanya balik

## Current Context
- Company: Chin Hin
- Users: Malaysian employees
- Timezone: Asia/Kuala_Lumpur (UTC+8)

Jom bantu users dengan tasks mereka! 💪
"""

# Cached client instance
_client: Optional[genai.Client] = None


def get_gemini_client() -> Optional[genai.Client]:
    """Get or create Gemini client instance."""
    global _client
    
    if _client is not None:
        return _client
    
    settings = get_settings()
    api_keys = settings.gemini_api_key_list
    
    if not api_keys:
        logger.warning("⚠️ No Gemini API keys configured!")
        return None
    
    # Use first key for general client, rotation is handled in function_agent for chat
    _client = genai.Client(api_key=api_keys[0])
    logger.info("✅ Gemini client initialized")
    return _client


def get_model(task_type: str = "general") -> str:
    """
    Smart model routing - use Flash for simple tasks, Pro for complex.
    """
    # Simple tasks → Gemini Flash (cheaper, faster)
    simple_tasks = ["greeting", "status_check", "balance_check", "list_items"]
    
    # Complex tasks → Gemini Pro (smarter)
    complex_tasks = ["apply_leave", "submit_claim", "multi_step", "analysis"]
    
    if task_type in simple_tasks:
        model_name = "gemini-2.5-flash"
    elif task_type in complex_tasks:
        model_name = "gemini-2.5-flash"  # Using flash for cost, can upgrade to pro
    else:
        model_name = "gemini-2.5-flash"  # Default to Flash
    
    logger.info(f"🤖 Using model: {model_name} for task: {task_type}")
    return model_name


async def chat_completion(
    message: str,
    history: Optional[List[Dict]] = None,
    task_type: str = "general"
) -> str:
    """
    Send message to Gemini and get response.
    
    Args:
        message: User's message
        history: Previous conversation history [{role, content}, ...]
        task_type: Type of task for model routing
    
    Returns:
        AI response string
    """
    client = get_gemini_client()
    
    if client is None:
        return "⚠️ Gemini API belum di-configure. Sila set GEMINI_API_KEY dalam .env"
    
    try:
        model_name = get_model(task_type)
        
        # Create chat with system instruction
        chat = client.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
        
        # Replay history if exists (to rebuild context)
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    # Send user message to rebuild context
                    chat.send_message(content)
        
        # Send current message
        response = chat.send_message(message)
        
        logger.info(f"✅ Gemini response received ({len(response.text)} chars)")
        return response.text
        
    except Exception as e:
        logger.error(f"❌ Gemini error: {str(e)}")
        return f"❌ Maaf, ada error: {str(e)}"


async def simple_generate(prompt: str) -> str:
    """
    Simple one-shot generation without history.
    Good for quick tasks like summarization.
    """
    client = get_gemini_client()
    
    if client is None:
        return "⚠️ Gemini API belum di-configure"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        logger.error(f"❌ Generate error: {str(e)}")
        return f"❌ Error: {str(e)}"
