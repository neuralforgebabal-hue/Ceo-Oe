"""
CEO AI OS - Memory API Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import get_db
from db import crud
from core.memory import memory_bus

router = APIRouter()

@router.get("/")
async def get_memories(limit: int = 50, db: AsyncSession = Depends(get_db)):
    memories = await crud.get_recent_memories(db, limit)
    return [
        {
            "id": m.id, "agent_id": m.agent_id, "action": m.action,
            "result": m.result[:300] if m.result else None,
            "project_id": m.project_id, "tags": m.tags, "success": m.success,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in memories
    ]

@router.get("/bus")
async def get_bus_events(limit: int = 100):
    return {"events": memory_bus.get_recent_events(limit), "stats": memory_bus.get_stats()}

@router.get("/state")
async def get_shared_state():
    return {"state": memory_bus.get_all_state(), "agents": memory_bus.get_agent_statuses()}
