import os
import logging
import asyncio
from typing import Optional
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "en-US-Neural2-F")

# Voice mapping: OpenAI-style names to Google Cloud voices
VOICE_MAPPING = {
    "nova": "en-US-Neural2-F",
    "shimmer": "en-US-Neural2-C",
    "alloy": "en-US-Neural2-E",
    "onyx": "en-US-Neural2-D",
    "fable": "en-US-Neural2-A",
    "echo": "en-US-Neural2-J",
}

class GoogleTTSService:
    """Google Cloud Text-to-Speech service"""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get or create TTS client"""
        if cls._client is None:
            try:
                cls._client = texttospeech.TextToSpeechClient()
                logger.info("[GOOGLE-TTS] Client initialized")
            except Exception as e:
                logger.error(f"[GOOGLE-TTS] Client initialization failed: {e}")
                raise
        return cls._client
    
    @staticmethod
    async def generate_audio(
        text: str, 
        voice_name: str,
        gender: str = "female",
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> bytes:
        """
        Generate audio from text using Google Cloud TTS
        
        Args:
            text: Text to convert to speech
            voice_name: Google Cloud voice name (e.g., 'en-US-Neural2-F')
            gender: Voice gender ('male' or 'female')
            speaking_rate: Speech rate (0.25 to 4.0)
            pitch: Voice pitch (-20.0 to 20.0)
        
        Returns:
            MP3 audio bytes
        """
        try:
            # Determine gender from voice name or parameter
            if gender.lower() == "female":
                ssml_gender = texttospeech.SsmlVoiceGender.FEMALE
            else:
                ssml_gender = texttospeech.SsmlVoiceGender.MALE
            
            client = GoogleTTSService.get_client()
            
            # Set the text input
            synthesis_input = texttospeech.SynthesisInput(text=text[:5000])
            
            # Build voice parameters
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=voice_name,
                ssml_gender=ssml_gender
            )
            
            # Select audio config with tenant settings
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=max(0.25, min(4.0, speaking_rate)),
                pitch=max(-20.0, min(20.0, pitch))
            )
            
            # Perform TTS request in thread pool
            response = await asyncio.to_thread(
                client.synthesize_speech,
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )
            
            audio_bytes = response.audio_content
            logger.info(f"[GOOGLE-TTS] Generated {len(audio_bytes)} bytes with voice: {voice_name} (rate={speaking_rate}, pitch={pitch})")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"[GOOGLE-TTS] Generation failed: {e}")
            return b""
