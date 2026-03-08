"""
Azure OpenAI Client for Chin Hin Employee Assistant.
Menggantikan Gemini client - guna Azure OpenAI SDK.
"""

from openai import AzureOpenAI
from typing import Optional, List, Dict
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

# System prompt untuk employee assistant
SYSTEM_PROMPT = """Kau adalah Chin Hin AI Assistant - pembantu pintar untuk pekerja Chin Hin! 🤖

## Personality
- Friendly dan helpful, macam bestie kat office
- Boleh cakap BM dan English (mix pun ok!)
- Gen Z vibe — guna emoji, slang sempoi

## Capabilities
Kau boleh bantu dengan:
1. **Leave Management** - Apply cuti, check balance, view requests
2. **Room Booking** - Book meeting room, check availability
3. **Expense Claims** - Submit claims, check status

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

# Cached client
_client: Optional[AzureOpenAI] = None


def get_azure_client() -> Optional[AzureOpenAI]:
    """Get or create Azure OpenAI client instance."""
    global _client

    if _client is not None:
        return _client

    settings = get_settings()

    if not settings.azure_openai_api_key:
        logger.warning("⚠️ Azure OpenAI API Key belum dikonfigure!")
        return None

    if not settings.azure_openai_endpoint:
        logger.warning("⚠️ Azure OpenAI Endpoint belum dikonfigure!")
        return None

    _client = AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
    )

    logger.info("✅ Azure OpenAI client initialized")
    return _client


async def chat_completion(
    message: str,
    history: Optional[List[Dict]] = None,
    task_type: str = "general"
) -> str:
    """
    Send message to Azure OpenAI and get response.

    Args:
        message: User's message
        history: Previous conversation history [{role, content}, ...]
        task_type: Type of task (tidak digunakan, untuk compatibility)

    Returns:
        AI response string
    """
    client = get_azure_client()
    settings = get_settings()

    if client is None:
        return "⚠️ Azure OpenAI API belum di-configure. Sila set dalam .env"

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Tambah history kalau ada
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"]:
                    messages.append({"role": role, "content": content})

        # Tambah message semasa
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        result = response.choices[0].message.content
        logger.info(f"✅ Azure OpenAI response received ({len(result)} chars)")
        return result

    except Exception as e:
        logger.error(f"❌ Azure OpenAI error: {str(e)}")
        return f"❌ Maaf, ada error: {str(e)}"


async def simple_generate(prompt: str) -> str:
    """
    Simple one-shot generation tanpa history.
    Good untuk quick tasks macam summarization.
    """
    client = get_azure_client()
    settings = get_settings()

    if client is None:
        return "⚠️ Azure OpenAI API belum di-configure"

    try:
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"❌ Generate error: {str(e)}")
        return f"❌ Error: {str(e)}"
