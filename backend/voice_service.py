import httpx
from config import settings

async def transcribe_audio(audio_file) -> str:
    """Convert speech to text using OpenAI Whisper"""
    if not settings.openai_api_key:
        return "Hello, how can I help you?"
    
    try:
        audio_content = await audio_file.read()
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {'file': ('audio.webm', audio_content, 'audio/webm')}
            data = {'model': 'whisper-1'}
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()["text"]
    except Exception as e:
        print(f"Transcription error: {e}")
        return "Hello, how can I help you?"

async def generate_speech(text: str, voice: str = "alloy") -> bytes:
    """Convert text to speech using OpenAI TTS"""
    if not settings.openai_api_key:
        return b""
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tts-1",
                    "input": text[:4096],
                    "voice": voice
                }
            )
            response.raise_for_status()
            return response.content
    except Exception as e:
        print(f"TTS error: {e}")
        return b""

async def generate_response(user_query: str, knowledge_context: str, company_name: str) -> str:
    """Generate AI response based on company knowledge"""
    system_prompt = f"""You are an AI employee for {company_name}. Answer questions using ONLY the provided company knowledge.
Be concise, conversational, and voice-optimized. If information isn't in the knowledge base, say you don't have that information and offer to connect them with support.

Company Knowledge:
{knowledge_context}"""

    async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
