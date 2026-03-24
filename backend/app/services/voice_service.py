"""
Agent Vaani - Voice Interface Service
Handles speech-to-text, text-to-speech using OpenAI APIs
English only
"""
import os
import base64
import tempfile
from typing import Optional, Dict
from openai import AsyncOpenAI
from core.logging import get_logger
from core.config import settings

logger = get_logger(__name__)

voice_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SUPPORTED_LANGUAGES = {
    "English": "en"
}

LANGUAGE_NAMES = {
    "en": "English"
}

async def transcribe_audio(audio_data: str, language: str = "English") -> Dict:
    """
    Transcribe audio to text using OpenAI Whisper API
    
    Args:
        audio_data: Base64 encoded audio data
        language: Language (English only)
    
    Returns:
        Dict with transcription, detected language, and confidence
    """
    try:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "CHANGE_OPENAI_API_KEY":
            logger.warning("OpenAI API key not configured, using fallback")
            return await _fallback_transcription(audio_data, language)

        audio_bytes = base64.b64decode(audio_data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as audio_file:
                transcript = await voice_client.audio.transcriptions.create(
                    model=settings.OPENAI_WHISPER_MODEL,
                    file=audio_file,
                    language="en",
                    response_format="verbose_json"
                )

            logger.info(f"Transcription successful: {transcript.text[:50]}...")

            return {
                "transcription": transcript.text,
                "detected_language": "English",
                "confidence": transcript.avg_logprob if hasattr(transcript, 'avg_logprob') else 0.95,
                "success": True,
                "stub": False
            }

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        return await _fallback_transcription(audio_data, language)

async def _fallback_transcription(audio_data: str, language: str) -> Dict:
    """Fallback when OpenAI is not available"""
    return {
        "transcription": "",
        "detected_language": "English",
        "confidence": 0.0,
        "error": "Voice transcription not available. Please configure OpenAI API key.",
        "success": False,
        "stub": True
    }

async def synthesize_speech(text: str, language: str = "English", voice: str = "alloy") -> Dict:
    """
    Synthesize speech from text using OpenAI TTS API
    
    Args:
        text: Text to convert to speech
        language: Target language (English only)
        voice: Voice type (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Dict with audio URL and duration
    """
    try:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "CHANGE_OPENAI_API_KEY":
            logger.warning("OpenAI API key not configured, using fallback")
            return await _fallback_synthesis(text, language)

        word_count = len(text.split())
        duration = (word_count / 150) * 60

        response = await voice_client.audio.speech.create(
            model=settings.OPENAI_TTS_MODEL,
            voice=settings.OPENAI_TTS_VOICE,
            input=text
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        logger.info(f"Speech synthesis successful: {text[:50]}...")

        return {
            "audio_url": f"/audio/temp/{os.path.basename(temp_file_path)}",
            "duration": duration,
            "success": True,
            "stub": False
        }

    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        return await _fallback_synthesis(text, language)

async def _fallback_synthesis(text: str, language: str) -> Dict:
    """Fallback when OpenAI is not available"""
    word_count = len(text.split())
    duration = (word_count / 150) * 60

    return {
        "audio_url": None,
        "duration": duration,
        "error": "Voice synthesis not available. Please configure OpenAI API key.",
        "success": False,
        "stub": True
    }

async def detect_language(text: str) -> str:
    """
    Always returns English
    
    Args:
        text: Input text
    
    Returns:
        "English"
    """
    return "English"

def get_supported_languages() -> list:
    """Get list of supported languages (English only)"""
    return list(SUPPORTED_LANGUAGES.keys())

def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """
    No translation needed - English only
    
    Args:
        text: Text to translate
        from_lang: Source language
        to_lang: Target language
    
    Returns:
        Original text
    """
    return text
