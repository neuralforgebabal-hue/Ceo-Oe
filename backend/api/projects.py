"""
CEO AI OS - Projects API Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from db.models import get_db
from db import crud
from scanner.detector import scan_directory
from scanner.classifier import classify_all
from core.logger import get_logger

router = APIRouter()
logger = get_logger("api.projects")


class ScanResponse(BaseModel):
    scanned: int
    projects: list


@router.post("/scan", response_model=ScanResponse)
async def scan_projects(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger a full scan of the home directory."""
    logger.info("Scan triggered via API")
    raw_projects = scan_directory()
    classified = classify_all(raw_projects)

    # Persist all projects
    for p in classified:
        try:
            await crud.upsert_project(db, p)
        except Exception as e:
            logger.error(f"Failed to save project {p.get('name')}: {e}")

    await crud.log_event(db, "SCAN_COMPLETE", "api.projects", {
        "count": len(classified)
    })

    return {"scanned": len(classified), "projects": classified}


@router.get("/")
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all scanned projects."""
    projects = await crud.get_all_projects(db)
    return [
        {
            "id": p.id,
            "name": p.name,
            "path": p.path,
            "project_type": p.project_type,
            "language": p.language,
            "framework": p.framework,
            "complexity_score": p.complexity_score,
            "profit_score": p.profit_score,
            "stability_score": p.stability_score,
            "success_prediction": p.success_prediction,
            "file_count": p.file_count,
            "total_lines": p.total_lines,
            "has_dockerfile": p.has_dockerfile,
            "has_tests": p.has_tests,
            "has_git": p.has_git,
            "readme_exists": p.readme_exists,
            "scanned_at": p.scanned_at.isoformat() if p.scanned_at else None,
        }
        for p in projects
    ]


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get full project details."""
    project = await crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    reports = await crud.get_project_reports(db, project_id)
    return {
        "project": {
            "id": project.id, "name": project.name, "path": project.path,
            "project_type": project.project_type, "language": project.language,
            "framework": project.framework, "complexity_score": project.complexity_score,
            "profit_score": project.profit_score, "stability_score": project.stability_score,
            "success_prediction": project.success_prediction,
            "file_count": project.file_count, "total_lines": project.total_lines,
            "dependencies": project.dependencies, "has_dockerfile": project.has_dockerfile,
            "has_tests": project.has_tests, "has_git": project.has_git,
            "readme_exists": project.readme_exists, "metadata_extra": project.metadata_extra,
        },
        "reports": [
            {
                "id": r.id, "type": r.report_type, "agent": r.agent_id,
                "summary": r.summary, "created_at": r.created_at.isoformat(),
                "content": r.content,
            }
            for r in reports
        ]
    }


@router.get("/stats/summary")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get system-wide statistics."""
    stats = await crud.get_system_stats(db)
    projects = await crud.get_all_projects(db)

    type_dist = {}
    for p in projects:
        type_dist[p.project_type] = type_dist.get(p.project_type, 0) + 1

    avg_profit = sum(p.profit_score or 0 for p in projects) / max(len(projects), 1)
    avg_stability = sum(p.stability_score or 0 for p in projects) / max(len(projects), 1)

    return {
        **stats,
        "type_distribution": type_dist,
        "average_profit_score": round(avg_profit, 2),
        "average_stability_score": round(avg_stability, 2),
        "top_projects": sorted(
            [{"name": p.name, "profit": p.profit_score} for p in projects],
            key=lambda x: x["profit"], reverse=True
        )[:5],
    }
