from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import voice_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# VOICE ENDPOINTS (Agent Vaani)
# ============================================================================

@router.post("/transcribe", response_model=schemas.VoiceTranscribeResponse)
async def transcribe_audio(
    request: schemas.VoiceTranscribeRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Transcribe audio using OpenAI Whisper"""
    result = await voice_service.transcribe_audio(
        request.audio_data,
        request.language
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Transcription failed"))

    return {
        "transcription": result["transcription"],
        "detected_language": result["detected_language"],
        "confidence": result["confidence"]
    }

@router.post("/synthesize", response_model=schemas.VoiceSynthesizeResponse)
async def synthesize_speech(
    request: schemas.VoiceSynthesizeRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Convert text to speech using OpenAI TTS"""
    result = await voice_service.synthesize_speech(
        request.text,
        request.language,
        request.voice
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Speech synthesis failed"))

    return {
        "audio_url": result["audio_url"],
        "duration_seconds": result["duration"]
    }

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages (English only)"""
    return {
        "languages": ["English"],
        "voice_types": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    }
