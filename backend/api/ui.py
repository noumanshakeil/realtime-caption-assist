from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import captions as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str | None = None, db: AsyncSession = Depends(get_db)):
    sessions = await svc.list_sessions(db)
    sid = session_id or (sessions[0].id if sessions else None)
    lines = await svc.lines(db, sid) if sid else []
    stats = await svc.latency_stats(db, sid) if sid else {}
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Realtime Caption Assist", "sessions": sessions, "session_id": sid, "lines": lines, "stats": stats},
    )

@router.post("/ui/sessions")
async def ui_start(title: str = Form(...), db: AsyncSession = Depends(get_db)):
    s = await svc.start_session(db, title)
    return RedirectResponse(f"/?session_id={s.id}", status_code=303)

@router.post("/ui/lines")
async def ui_line(
    session_id: str = Form(...),
    text: str = Form(...),
    speaker: str = Form("spk1"),
    is_final: str = Form("1"),
    latency_ms: float = Form(110.0),
    db: AsyncSession = Depends(get_db),
):
    await svc.add_line(db, session_id, text, speaker=speaker, is_final=is_final == "1", latency_ms=latency_ms)
    return RedirectResponse(f"/?session_id={session_id}", status_code=303)
