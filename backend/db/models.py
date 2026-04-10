"""
CEO AI OS - Database Models
SQLAlchemy async models for all system entities.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    DateTime, ForeignKey, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship
from core.config import settings

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)  # hash of path
    name = Column(String, nullable=False)
    path = Column(String, nullable=False, unique=True)
    project_type = Column(String, default="unknown")  # python|bot|web|ai|mixed
    language = Column(String, default="unknown")
    framework = Column(String, nullable=True)
    complexity_score = Column(Float, default=0.0)   # 0-10
    profit_score = Column(Float, default=0.0)        # 0-10
    stability_score = Column(Float, default=0.0)     # 0-10
    success_prediction = Column(Float, default=0.0)  # 0-100%
    file_count = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    dependencies = Column(JSON, default=list)
    has_dockerfile = Column(Boolean, default=False)
    has_tests = Column(Boolean, default=False)
    has_env = Column(Boolean, default=False)
    has_git = Column(Boolean, default=False)
    readme_exists = Column(Boolean, default=False)
    last_modified = Column(DateTime, nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow)
    metadata_extra = Column(JSON, default=dict)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")


class AgentMemory(Base):
    __tablename__ = "agent_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    result = Column(Text, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    tags = Column(JSON, default=list)
    success = Column(Boolean, default=True)
    error_msg = Column(Text, nullable=True)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    assigned_agent = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    priority = Column(Integer, default=3)  # 1=highest, 5=lowest
    status = Column(String, default="pending")  # pending|running|done|failed
    payload = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="tasks")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    report_type = Column(String, nullable=False)  # security|analysis|monetization|deployment
    agent_id = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="reports")


class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedProject(Base):
    __tablename__ = "generated_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    template = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    output_path = Column(String, nullable=True)
    files_created = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Database Engine ────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
