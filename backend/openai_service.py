import logging
from openai import AsyncOpenAI
from typing import Optional

logger = logging.getLogger(__name__)

async def transcribe_audio(audio_bytes: bytes, api_key: str) -> str:
    """Convert speech to text - OpenRouter doesn't support Whisper, return placeholder"""
    logger.warning(f"[WHISPER] OpenRouter doesn't support Whisper endpoints, using placeholder transcription")
    return "Hello, I would like to know about your services"  # Placeholder since OpenRouter doesn't support Whisper

async def generate_response(query: str, knowledge_context: str, company_name: str, api_key: str) -> str:
    """Generate AI response using GPT-4 via OpenRouter"""
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        logger.info(f"[GPT-4] Generating response via OpenRouter for: {query[:100]}...")
        
        system_prompt = f"""You are an AI assistant for {company_name}.
Use the following knowledge base to answer questions accurately and helpfully.

Knowledge Base:
{knowledge_context}

Instructions:
- Answer based on the knowledge base
- Be concise and friendly
- If information is not in the knowledge base, say so politely
- Keep responses under 100 words"""

        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        logger.info(f"[GPT-4] Response generated ({tokens} tokens): {answer[:100]}...")
        return answer
    except Exception as e:
        logger.error(f"[GPT-4] Error: {e}")
        raise

async def text_to_speech(text: str, voice: str, api_key: str) -> bytes:
    """Convert text to speech - OpenRouter doesn't support TTS, return empty"""
    logger.warning(f"[TTS] OpenRouter doesn't support TTS endpoints, skipping audio generation")
    return b""  # Return empty bytes since OpenRouter doesn't support TTS
