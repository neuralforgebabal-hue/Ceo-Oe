"""
CEO AI OS - Database CRUD Operations
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from db.models import Project, AgentMemory, Task, Report, SystemEvent, GeneratedProject
from core.config import settings


# ─── Projects ────────────────────────────────────────────────
async def upsert_project(db: AsyncSession, project_data: dict) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_data["id"]))
    existing = result.scalar_one_or_none()
    if existing:
        for k, v in project_data.items():
            setattr(existing, k, v)
        existing.scanned_at = datetime.utcnow()
        await db.commit()
        return existing
    project = Project(**project_data)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_all_projects(db: AsyncSession) -> List[Project]:
    result = await db.execute(select(Project).order_by(Project.scanned_at.desc()))
    return result.scalars().all()


async def get_project(db: AsyncSession, project_id: str) -> Optional[Project]:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


# ─── Memory ──────────────────────────────────────────────────
async def write_memory(db: AsyncSession, agent_id: str, action: str, result: str,
                       project_id: Optional[str] = None, tags: List[str] = None,
                       success: bool = True, error_msg: str = None,
                       duration_ms: int = 0) -> AgentMemory:
    expires = datetime.utcnow() + timedelta(days=settings.MEMORY_TTL_DAYS)
    mem = AgentMemory(
        agent_id=agent_id, action=action, result=result,
        project_id=project_id, tags=tags or [], success=success,
        error_msg=error_msg, duration_ms=duration_ms, expires_at=expires
    )
    db.add(mem)
    await db.commit()
    return mem


async def get_agent_memories(db: AsyncSession, agent_id: str, limit: int = 20) -> List[AgentMemory]:
    result = await db.execute(
        select(AgentMemory)
        .where(AgentMemory.agent_id == agent_id)
        .order_by(AgentMemory.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_recent_memories(db: AsyncSession, limit: int = 50) -> List[AgentMemory]:
    result = await db.execute(
        select(AgentMemory).order_by(AgentMemory.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


# ─── Tasks ───────────────────────────────────────────────────
async def create_task(db: AsyncSession, task_data: dict) -> Task:
    task = Task(**task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task_status(db: AsyncSession, task_id: str, status: str,
                              result: dict = None, error: str = None):
    values = {"status": status}
    if status == "running":
        values["started_at"] = datetime.utcnow()
    elif status in ("done", "failed"):
        values["completed_at"] = datetime.utcnow()
    if result:
        values["result"] = result
    if error:
        values["error"] = error
    await db.execute(update(Task).where(Task.id == task_id).values(**values))
    await db.commit()


async def get_tasks(db: AsyncSession, status: Optional[str] = None) -> List[Task]:
    q = select(Task).order_by(Task.priority, Task.created_at)
    if status:
        q = q.where(Task.status == status)
    result = await db.execute(q)
    return result.scalars().all()


# ─── Reports ─────────────────────────────────────────────────
async def save_report(db: AsyncSession, report_data: dict) -> Report:
    report = Report(**report_data)
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_project_reports(db: AsyncSession, project_id: str) -> List[Report]:
    result = await db.execute(
        select(Report).where(Report.project_id == project_id)
        .order_by(Report.created_at.desc())
    )
    return result.scalars().all()


# ─── System Events ───────────────────────────────────────────
async def log_event(db: AsyncSession, event_type: str, source: str, data: dict = None):
    event = SystemEvent(event_type=event_type, source=source, data=data or {})
    db.add(event)
    await db.commit()


async def get_recent_events(db: AsyncSession, limit: int = 100) -> List[SystemEvent]:
    result = await db.execute(
        select(SystemEvent).order_by(SystemEvent.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


# ─── Stats ───────────────────────────────────────────────────
async def get_system_stats(db: AsyncSession) -> Dict[str, Any]:
    total_projects = await db.scalar(select(func.count(Project.id)))
    total_tasks = await db.scalar(select(func.count(Task.id)))
    done_tasks = await db.scalar(select(func.count(Task.id)).where(Task.status == "done"))
    total_memories = await db.scalar(select(func.count(AgentMemory.id)))
    return {
        "total_projects": total_projects or 0,
        "total_tasks": total_tasks or 0,
        "completed_tasks": done_tasks or 0,
        "total_memories": total_memories or 0,
    }
