"""
CEO AI OS - Base Agent
All agents extend this class. Handles memory, AI calls, logging.
"""
import json
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from ai.router import ai_router
from core.memory import memory_bus
from core.logger import get_logger


class BaseAgent(ABC):
    """
    Abstract base for all CEO OS agents.
    Provides: AI calls, memory publishing, error handling, timing.
    """

    def __init__(self, agent_id: str, system_prompt: str):
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self.logger = get_logger(f"agent.{agent_id}")
        self._task_count = 0
        self._error_count = 0

    @abstractmethod
    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        """Execute the agent's core task on a project."""
        pass

    async def think(self, user_message: str, max_tokens: int = 2000,
                    json_mode: bool = True) -> Dict[str, Any]:
        """Call AI and parse JSON response."""
        start = time.time()
        try:
            raw = await ai_router.complete(
                system_prompt=self.system_prompt,
                user_message=user_message,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )
            elapsed = int((time.time() - start) * 1000)
            parsed = self._parse_json(raw)
            self.logger.debug(f"AI response in {elapsed}ms")
            return parsed
        except Exception as e:
            self.logger.error(f"AI call failed: {e}")
            return {"error": str(e), "agent": self.agent_id}

    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try extracting JSON block
            import re
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            return {"raw_response": text, "parse_error": True}

    async def emit(self, event_type: str, data: Any, project_id: Optional[str] = None):
        """Publish an event to the memory bus."""
        await memory_bus.publish(
            agent_id=self.agent_id,
            event_type=event_type,
            data=data,
            project_id=project_id,
        )

    async def emit_start(self, project: dict):
        self._task_count += 1
        await self.emit("AGENT_START", {
            "project": project.get("name"),
            "task_num": self._task_count,
        }, project.get("id"))
        self.logger.info(f"▶ Starting on project: {project.get('name')}")

    async def emit_done(self, project: dict, result: dict):
        memory_bus.set_agent_idle(self.agent_id)
        await self.emit("AGENT_DONE", {
            "project": project.get("name"),
            "result_keys": list(result.keys()),
        }, project.get("id"))
        self.logger.info(f"✓ Done with project: {project.get('name')}")

    async def emit_error(self, project: dict, error: str):
        self._error_count += 1
        memory_bus.set_agent_idle(self.agent_id)
        await self.emit("AGENT_ERROR", {
            "project": project.get("name"),
            "error": error,
        }, project.get("id"))
        self.logger.error(f"✗ Error on {project.get('name')}: {error}")

    def get_stats(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "tasks_run": self._task_count,
            "errors": self._error_count,
        }
