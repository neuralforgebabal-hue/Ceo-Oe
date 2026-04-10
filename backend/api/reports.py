"""
CEO AI OS - Reports API Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import get_db
from db import crud

router = APIRouter()

@router.get("/{project_id}")
async def get_reports(project_id: str, db: AsyncSession = Depends(get_db)):
    reports = await crud.get_project_reports(db, project_id)
    return [
        {
            "id": r.id, "type": r.report_type, "agent": r.agent_id,
            "summary": r.summary, "content": r.content,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]

@router.get("/events/recent")
async def get_events(limit: int = 50, db: AsyncSession = Depends(get_db)):
    events = await crud.get_recent_events(db, limit)
    return [
        {"id": e.id, "type": e.event_type, "source": e.source,
         "data": e.data, "created_at": e.created_at.isoformat()}
        for e in events
    ]
