from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import captions as svc

class SessionIn(BaseModel):
    title: str = Field(min_length=2)

class LineIn(BaseModel):
    text: str = Field(min_length=1)
    speaker: str = "spk1"
    is_final: bool = False
    latency_ms: float = 120.0

router = APIRouter()

@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_sessions(db)
    return {"sessions": [{"id": s.id, "title": s.title, "status": s.status} for s in rows]}

@router.post("/sessions")
async def create(payload: SessionIn, db: AsyncSession = Depends(get_db)):
    s = await svc.start_session(db, payload.title)
    return {"id": s.id}

@router.post("/sessions/{session_id}/lines")
async def post_line(session_id: str, payload: LineIn, db: AsyncSession = Depends(get_db)):
    line = await svc.add_line(
        db, session_id, payload.text, speaker=payload.speaker, is_final=payload.is_final, latency_ms=payload.latency_ms
    )
    return {"id": line.id, "seq": line.seq}

@router.get("/sessions/{session_id}/lines")
async def get_lines(session_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.lines(db, session_id)
    return {
        "lines": [
            {
                "id": r.id,
                "speaker": r.speaker,
                "text": r.text,
                "is_final": r.is_final,
                "latency_ms": r.latency_ms,
                "seq": r.seq,
            }
            for r in rows
        ]
    }

@router.get("/sessions/{session_id}/stats")
async def stats(session_id: str, db: AsyncSession = Depends(get_db)):
    return await svc.latency_stats(db, session_id)

@router.post("/sessions/{session_id}/end")
async def end(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        s = await svc.end_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"id": s.id, "status": s.status}
