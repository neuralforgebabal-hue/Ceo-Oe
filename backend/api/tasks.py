"""
CEO AI OS - Tasks API Routes
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import get_db
from db import crud

router = APIRouter()

@router.get("/")
async def get_tasks(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    tasks = await crud.get_tasks(db, status)
    return [
        {
            "id": t.id, "project_id": t.project_id, "agent": t.assigned_agent,
            "type": t.task_type, "priority": t.priority, "status": t.status,
            "result": t.result, "error": t.error,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in tasks
    ]
