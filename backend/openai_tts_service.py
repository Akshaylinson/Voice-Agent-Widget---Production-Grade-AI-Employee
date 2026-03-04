import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "nova")

class OpenAITTSService:
    """OpenAI Text-to-Speech service for audio generation"""
    
    @staticmethod
    async def generate_audio(text: str, voice: Optional[str] = None) -> bytes:
        """
        Generate audio from text using OpenAI TTS API
        
        Args:
            text: Text to convert to speech
            voice: Voice model (nova, alloy, echo, fable, onyx, shimmer)
        
        Returns:
            MP3 audio bytes
        """
        if not OPENAI_API_KEY:
            logger.error("[OPENAI-TTS] API key not configured")
            return b""
        
        voice = voice or DEFAULT_VOICE
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": OPENAI_TTS_MODEL,
                        "input": text[:4096],  # OpenAI limit
                        "voice": voice,
                        "response_format": "mp3"
                    }
                )
                response.raise_for_status()
                
                audio_bytes = response.content
                logger.info(f"[OPENAI-TTS] Generated {len(audio_bytes)} bytes with voice: {voice}")
                return audio_bytes
                
        except Exception as e:
            logger.error(f"[OPENAI-TTS] Generation failed: {e}")
            return b""
