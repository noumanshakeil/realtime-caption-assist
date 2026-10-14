from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import CaptionLine, CaptionSession

async def start_session(session: AsyncSession, title: str) -> CaptionSession:
    row = CaptionSession(id=uuid.uuid4().hex[:10], title=title.strip()[:200], status="live")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def list_sessions(session: AsyncSession) -> list[CaptionSession]:
    return list((await session.execute(select(CaptionSession).order_by(CaptionSession.created_at.desc()))).scalars())

async def add_line(
    session: AsyncSession,
    session_id: str,
    text: str,
    *,
    speaker: str = "spk1",
    is_final: bool = False,
    latency_ms: float = 120.0,
) -> CaptionLine:
    count = len(
        list(
            (
                await session.execute(select(CaptionLine).where(CaptionLine.session_id == session_id))
            ).scalars()
        )
    )
    line = CaptionLine(
        id=uuid.uuid4().hex[:12],
        session_id=session_id,
        speaker=speaker[:80],
        text=text.strip(),
        is_final=is_final,
        latency_ms=float(latency_ms),
        seq=count + 1,
    )
    session.add(line)
    await session.commit()
    await session.refresh(line)
    return line

async def lines(session: AsyncSession, session_id: str) -> list[CaptionLine]:
    return list(
        (
            await session.execute(
                select(CaptionLine)
                .where(CaptionLine.session_id == session_id)
                .order_by(CaptionLine.seq.asc())
            )
        ).scalars()
    )

async def end_session(session: AsyncSession, session_id: str) -> CaptionSession:
    row = await session.get(CaptionSession, session_id)
    if not row:
        raise ValueError("not found")
    row.status = "ended"
    await session.commit()
    await session.refresh(row)
    return row

async def latency_stats(session: AsyncSession, session_id: str) -> dict:
    rows = await lines(session, session_id)
    if not rows:
        return {"count": 0, "avg_ms": 0.0, "p95_ms": 0.0}
    vals = sorted(r.latency_ms for r in rows)
    p95 = vals[int(len(vals) * 0.95) - 1] if len(vals) >= 2 else vals[-1]
    return {"count": len(vals), "avg_ms": round(sum(vals) / len(vals), 2), "p95_ms": round(p95, 2)}
