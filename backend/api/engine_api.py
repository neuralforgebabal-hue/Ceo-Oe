"""
CEO AI OS - Engine API Routes
Self-improvement, prediction, and project generation endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import get_db
from db import crud
from engine.engines import improvement_engine, prediction_engine, project_generator
from core.logger import get_logger

router = APIRouter()
logger = get_logger("api.engine")


class PredictRequest(BaseModel):
    project_id: str


class ImproveRequest(BaseModel):
    project_id: str


class GenerateRequest(BaseModel):
    description: str
    template: str = "flask_api"
    output_name: Optional[str] = None


class FileAnalyzeRequest(BaseModel):
    file_path: str


@router.post("/predict")
async def predict_project(request: PredictRequest, db: AsyncSession = Depends(get_db)):
    """Predict success probability and risks for a project."""
    project = await crud.get_project(db, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    memories = await crud.get_agent_memories(db, "analyst", 10)
    history = [{"action": m.action} for m in memories]

    project_dict = {
        "id": project.id, "name": project.name,
        "project_type": project.project_type, "complexity_score": project.complexity_score,
        "profit_score": project.profit_score, "stability_score": project.stability_score,
        "has_tests": project.has_tests, "has_dockerfile": project.has_dockerfile,
        "total_lines": project.total_lines, "file_count": project.file_count,
    }
    result = await prediction_engine.predict(project_dict, history)
    return result


@router.post("/improve")
async def suggest_improvements(request: ImproveRequest, db: AsyncSession = Depends(get_db)):
    """Get AI-powered improvement suggestions for a project."""
    project = await crud.get_project(db, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dict = {
        "id": project.id, "name": project.name,
        "project_type": project.project_type, "complexity_score": project.complexity_score,
        "stability_score": project.stability_score,
        "has_tests": project.has_tests, "readme_exists": project.readme_exists,
    }
    result = await improvement_engine.suggest_project_improvements(project_dict)
    return result


@router.post("/analyze-file")
async def analyze_file(request: FileAnalyzeRequest):
    """Analyze a specific file for improvement suggestions."""
    result = await improvement_engine.analyze_file(request.file_path)
    return result


@router.post("/generate")
async def generate_project(request: GenerateRequest, db: AsyncSession = Depends(get_db)):
    """Auto-generate a new project from a description."""
    logger.info(f"Generating project: {request.description[:60]}...")
    result = await project_generator.generate(
        description=request.description,
        template=request.template,
        output_name=request.output_name,
    )
    if "files" in result and not result.get("error"):
        from db.models import GeneratedProject
        gen = GeneratedProject(
            name=result.get("project_name", "unknown"),
            template=request.template,
            description=request.description,
            output_path=result.get("output_path"),
            files_created=[f.get("path") for f in result.get("files", [])],
        )
        db.add(gen)
        await db.commit()
    return result


@router.get("/templates")
async def list_templates():
    """List available project templates."""
    return {"templates": list(project_generator.TEMPLATES.keys()),
            "details": project_generator.TEMPLATES}
