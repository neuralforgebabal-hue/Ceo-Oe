"""
CEO AI OS - FastAPI Main Application
Entry point with all routes, WebSocket, and startup.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.logger import get_logger
from core.memory import memory_bus
from db.models import init_db
from api import projects, agents, tasks, memory_api, reports, engine_api

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 CEO AI OS starting up...")
    await init_db()
    logger.info("✓ Database initialized")
    yield
    logger.info("CEO AI OS shutting down.")


app = FastAPI(
    title="CEO AI Operating System",
    description="Autonomous AI system for managing, analyzing, and improving projects",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── API Routers ─────────────────────────────────────────────
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(memory_api.router, prefix="/api/memory", tags=["Memory"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(engine_api.router, prefix="/api/engine", tags=["Engine"])


# ─── WebSocket ───────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = memory_bus.subscribe()
    logger.info("WebSocket client connected")
    try:
        # Send initial state
        await websocket.send_json({
            "type": "CONNECTED",
            "data": {
                "message": "CEO AI OS WebSocket connected",
                "bus_stats": memory_bus.get_stats(),
            }
        })
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json({
                    "type": "BUS_EVENT",
                    "data": event,
                })
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "PING", "data": {}})
    except WebSocketDisconnect:
        memory_bus.unsubscribe(queue)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        memory_bus.unsubscribe(queue)
        logger.error(f"WebSocket error: {e}")


# ─── Root ────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "system": "CEO AI Operating System",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "projects": "/api/projects",
            "agents": "/api/agents",
            "tasks": "/api/tasks",
            "memory": "/api/memory",
            "reports": "/api/reports",
            "engine": "/api/engine",
            "websocket": "/ws",
            "docs": "/docs",
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "ai_provider": settings.AI_PROVIDER,
        "bus": memory_bus.get_stats(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
