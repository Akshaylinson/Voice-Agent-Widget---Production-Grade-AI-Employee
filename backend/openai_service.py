import logging
import httpx
import base64
import os
from typing import Optional

logger = logging.getLogger(__name__)

# OpenRouter Configuration
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_LLM_MODEL = os.getenv("OPENROUTER_LLM_MODEL", "openai/gpt-4o-mini")
OPENROUTER_TTS_MODEL = os.getenv("OPENROUTER_TTS_MODEL", "openai/gpt-4o-audio-preview")
OPENROUTER_HTTP_REFERER = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost:8000")
OPENROUTER_APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "Codeless AI Voice Platform")

async def transcribe_audio(audio_bytes: bytes, api_key: str) -> str:
    """Browser handles STT via Web Speech API - this is placeholder"""
    logger.info("[STT] Using browser Web Speech API for transcription")
    return ""  # Not used - browser sends transcribed text directly

async def generate_response(query: str, knowledge_context: str, company_name: str, api_key: str) -> str:
    """Generate AI response using GPT-4o-mini via OpenRouter"""
    try:
        logger.info(f"[LLM] Generating response for: {query[:100]}...")
        
        system_prompt = f"""You are an AI assistant for {company_name}.
Use the following knowledge base to answer questions accurately and helpfully.

Knowledge Base:
{knowledge_context}

Instructions:
- Answer based on the knowledge base
- Be concise and friendly
- If information is not in the knowledge base, say so politely
- Keep responses under 100 words"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": OPENROUTER_HTTP_REFERER,
            "X-Title": OPENROUTER_APP_TITLE,
            "Content-Type": "application/json"
        }

        payload = {
            "model": OPENROUTER_LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        answer = data["choices"][0]["message"]["content"]
        logger.info(f"[LLM] Response generated: {answer[:100]}...")
        return answer

    except Exception as e:
        logger.error(f"[LLM] Error: {e}")
        raise

async def text_to_speech(text: str, voice: str, api_key: str) -> bytes:
    """Convert text to speech using OpenRouter GPT-4o Audio Preview"""
    try:
        logger.info(f"[TTS] Converting text to speech: {text[:100]}...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": OPENROUTER_HTTP_REFERER,
            "X-Title": OPENROUTER_APP_TITLE,
            "Content-Type": "application/json"
        }

        # GPT-4o Audio Preview with audio modality
        payload = {
            "model": OPENROUTER_TTS_MODEL,
            "modalities": ["text", "audio"],
            "audio": {"voice": voice, "format": "mp3"},
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ]
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        # Extract audio from response
        audio_data = None
        
        # Check for audio in message content
        if "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0].get("message", {})
            
            # Audio might be in content array
            if isinstance(message.get("content"), list):
                for item in message["content"]:
                    if item.get("type") == "audio":
                        audio_data = item.get("data")
                        break
            
            # Or directly in audio field
            elif "audio" in message:
                audio_data = message["audio"].get("data")

        if not audio_data:
            logger.error("[TTS] No audio data in response")
            raise ValueError("No audio data returned from OpenRouter")

        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)
        logger.info(f"[TTS] Audio generated: {len(audio_bytes)} bytes")
        
        return audio_bytes

    except Exception as e:
        logger.error(f"[TTS] Error: {e}")
        raise
