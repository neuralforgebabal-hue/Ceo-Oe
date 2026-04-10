"""
CEO AI OS - Agents API Routes
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import get_db
from db import crud
from agents.sub_agents import get_agent, AGENT_REGISTRY
from core.memory import memory_bus
from core.logger import get_logger

router = APIRouter()
logger = get_logger("api.agents")


class RunAgentRequest(BaseModel):
    agent_name: str
    project_id: str


class RunAllAgentsRequest(BaseModel):
    project_id: str
    agents: Optional[list] = None  # None = run all


@router.get("/")
async def list_agents():
    """List all registered agents and their statuses."""
    statuses = memory_bus.get_agent_statuses()
    agents = []
    for name in AGENT_REGISTRY:
        agents.append({
            "id": name,
            "name": name.capitalize() + " Agent",
            "status": statuses.get(name, {}).get("status", "idle"),
            "last_active": statuses.get(name, {}).get("last_active"),
            "last_event": statuses.get(name, {}).get("last_event"),
        })
    return agents


@router.post("/run")
async def run_agent(
    request: RunAgentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Run a specific agent on a project."""
    project = await crud.get_project(db, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dict = {
        "id": project.id, "name": project.name, "path": project.path,
        "project_type": project.project_type, "language": project.language,
        "framework": project.framework, "complexity_score": project.complexity_score,
        "profit_score": project.profit_score, "stability_score": project.stability_score,
        "file_count": project.file_count, "total_lines": project.total_lines,
        "dependencies": project.dependencies or [],
        "has_dockerfile": project.has_dockerfile, "has_tests": project.has_tests,
        "has_git": project.has_git, "readme_exists": project.readme_exists,
        "has_env": project.has_env, "metadata_extra": project.metadata_extra or {},
    }

    task_id = uuid.uuid4().hex
    task = await crud.create_task(db, {
        "id": task_id,
        "project_id": request.project_id,
        "assigned_agent": request.agent_name,
        "task_type": f"agent_{request.agent_name}",
        "priority": 2,
        "status": "pending",
        "payload": {"project_id": request.project_id},
    })

    background_tasks.add_task(
        _run_agent_task, request.agent_name, project_dict, task_id, db
    )

    return {"task_id": task_id, "status": "started", "agent": request.agent_name}


@router.post("/run-all")
async def run_all_agents(
    request: RunAllAgentsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Run all (or selected) agents on a project."""
    project = await crud.get_project(db, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dict = {
        "id": project.id, "name": project.name, "path": project.path,
        "project_type": project.project_type, "language": project.language,
        "framework": project.framework, "complexity_score": project.complexity_score,
        "profit_score": project.profit_score, "stability_score": project.stability_score,
        "file_count": project.file_count, "total_lines": project.total_lines,
        "dependencies": project.dependencies or [],
        "has_dockerfile": project.has_dockerfile, "has_tests": project.has_tests,
        "has_git": project.has_git, "readme_exists": project.readme_exists,
        "has_env": project.has_env, "metadata_extra": project.metadata_extra or {},
    }

    agents_to_run = request.agents or ["ceo", "architect", "security", "analyst", "monetization", "deployment"]
    task_ids = []

    for agent_name in agents_to_run:
        task_id = uuid.uuid4().hex
        await crud.create_task(db, {
            "id": task_id, "project_id": request.project_id,
            "assigned_agent": agent_name, "task_type": f"agent_{agent_name}",
            "priority": 3, "status": "pending",
            "payload": {"project_id": request.project_id},
        })
        task_ids.append(task_id)
        background_tasks.add_task(_run_agent_task, agent_name, project_dict, task_id, db)

    return {"task_ids": task_ids, "agents": agents_to_run, "status": "started"}


@router.get("/events")
async def get_agent_events(limit: int = 50):
    """Get recent agent bus events."""
    events = memory_bus.get_recent_events(limit)
    return {"events": events, "total": len(events)}


async def _run_agent_task(agent_name: str, project: dict, task_id: str, db):
    """Background task runner."""
    from db.models import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            await crud.update_task_status(session, task_id, "running")
            agent = get_agent(agent_name)
            result = await agent.run(project, session)
            await crud.update_task_status(session, task_id, "done", result=result)
        except Exception as e:
            logger.error(f"Agent {agent_name} failed on task {task_id}: {e}")
            await crud.update_task_status(session, task_id, "failed", error=str(e))
