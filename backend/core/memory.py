"""
CEO AI OS - Memory Bus
Shared in-memory + persistent state for all agents.
Agents read/write here instead of calling each other directly.
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
from core.logger import get_logger

logger = get_logger("core.memory")


class MemoryBus:
    """
    Central shared memory for all agents.
    - In-memory queue for fast real-time access
    - Agents push events and read from shared state
    - WebSocket clients subscribe to live updates
    """

    def __init__(self, max_events: int = 500):
        self._events: deque = deque(maxlen=max_events)
        self._shared_state: Dict[str, Any] = {}
        self._agent_states: Dict[str, Dict] = {}
        self._subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    async def publish(self, agent_id: str, event_type: str,
                       data: Any, project_id: Optional[str] = None) -> dict:
        """Push an event from an agent to the bus."""
        event = {
            "id": f"{agent_id}_{datetime.utcnow().timestamp()}",
            "agent_id": agent_id,
            "event_type": event_type,
            "data": data,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        async with self._lock:
            self._events.append(event)
            # Update agent state
            self._agent_states[agent_id] = {
                "last_event": event_type,
                "last_active": event["timestamp"],
                "status": "active",
            }
        # Notify all WebSocket subscribers
        await self._broadcast(event)
        logger.debug(f"[BUS] {agent_id} → {event_type}")
        return event

    async def _broadcast(self, event: dict):
        dead = []
        for q in self._subscribers:
            try:
                await q.put(event)
            except Exception:
                dead.append(q)
        for d in dead:
            self._subscribers.remove(d)

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to live events (for WebSocket connections)."""
        q = asyncio.Queue(maxsize=100)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    def get_recent_events(self, limit: int = 50) -> List[dict]:
        events = list(self._events)
        return events[-limit:]

    def get_agent_events(self, agent_id: str, limit: int = 20) -> List[dict]:
        return [e for e in self._events if e["agent_id"] == agent_id][-limit:]

    def set_state(self, key: str, value: Any):
        self._shared_state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._shared_state.get(key, default)

    def get_all_state(self) -> dict:
        return dict(self._shared_state)

    def get_agent_statuses(self) -> Dict[str, Dict]:
        return dict(self._agent_states)

    def set_agent_idle(self, agent_id: str):
        if agent_id in self._agent_states:
            self._agent_states[agent_id]["status"] = "idle"

    def get_stats(self) -> dict:
        return {
            "total_events": len(self._events),
            "active_agents": sum(
                1 for s in self._agent_states.values()
                if s.get("status") == "active"
            ),
            "subscribers": len(self._subscribers),
            "shared_keys": len(self._shared_state),
        }


# Singleton
memory_bus = MemoryBus()
