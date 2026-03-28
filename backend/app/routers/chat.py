from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import AsyncGenerator
import json
import asyncio
import uuid
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services.orchestrator import (
    process_chat_query, 
    stream_agent_response, 
    determine_agent,
    save_chat_message
)
from core.config import settings

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# CHAT ENDPOINTS (Agent Orchestrator)
# ============================================================================

@router.post("/process", response_model=schemas.ChatResponse)
async def process_message(
    request: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process chat query through agent orchestrator with platform-first behavior"""
    user_data = {
        "id": current_user.id,
        "phone": current_user.phone,
        "name": current_user.name,
        "district": current_user.district or "Andhra Pradesh",
        "trust_score": current_user.trust_score,
        "trust_coins": current_user.trust_coins,
        "trust_badge": current_user.trust_badge,
        "hierarchy_level": current_user.hierarchy_level.value if current_user.hierarchy_level else "SHG",
        "role": current_user.role.value
    }

    use_global_search = request.global_search or False
    agent_override = request.agent_id or None
    
    
    response = await process_chat_query(
        request.query,
        user_data,
        db,
        request.language,
        agent_override
    )
    
    return schemas.ChatResponse(
        reply=response.get("reply", ""),
        agent_triggered=response.get("agent_triggered", "VAANI"),
        language=response.get("language", "English"),
        session_id=response.get("session_id", str(uuid.uuid4())),
        needs_global_search=response.get("needs_global_search", False),
        is_fallback=response.get("is_fallback", False),
    )

@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat history"""
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(
        models.ChatHistory.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": h.id,
            "role": h.role,
            "content": h.content,
            "agent_triggered": h.agent_triggered,
            "language": h.language,
            "audio_url": h.audio_url,
            "created_at": h.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for h in history
    ]

@router.get("/stream")
async def stream_chat(
    query: str,
    language: str = "English",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream chat response in real-time using Server-Sent Events"""
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            user_data = {
                "id": current_user.id,
                "phone": current_user.phone,
                "name": current_user.name,
                "district": current_user.district or "Andhra Pradesh",
                "trust_score": current_user.trust_score,
                "trust_coins": current_user.trust_coins,
                "trust_badge": current_user.trust_badge,
                "hierarchy_level": current_user.hierarchy_level.value if current_user.hierarchy_level else "SHG",
                "role": current_user.role.value
            }

            session_id = str(uuid.uuid4())

            await save_chat_message(
                user_data["id"],
                session_id,
                "user",
                query,
                language=language,
                db=db
            )

            agent_decision = await determine_agent(query, db)

            full_response = ""
            async for chunk, is_done in stream_agent_response(
                agent_decision,
                query,
                user_data,
                db,
                language
            ):
                if not is_done:
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk, 'done': False, 'agent': agent_decision})}\n\n"
                else:
                    await save_chat_message(
                        user_data["id"],
                        session_id,
                        "assistant",
                        full_response,
                        agent_triggered=agent_decision,
                        language=language,
                        db=db
                    )
                    
                    yield f"data: {json.dumps({'content': '', 'done': True, 'session_id': session_id, 'agent': agent_decision})}\n\n"
                    yield "event: done\ndata: [DONE]\n\n"

        except Exception as e:
            error_msg = json.dumps({'error': str(e), 'done': True})
            yield f"data: {error_msg}\n\n"

    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
