"""
CEO AI OS - CEO Agent
Master decision maker. Orchestrates all other agents.
"""
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from ai.prompts import CEO_SYSTEM, ceo_analysis_prompt
from db import crud
from core.logger import get_logger

logger = get_logger("agent.ceo")


class CEOAgent(BaseAgent):
    """
    The CEO Agent is the top-level orchestrator.
    - Analyzes each project at a strategic level
    - Decides which sub-agents to activate
    - Sets priorities and task queue
    - Makes final recommendations
    """

    def __init__(self):
        super().__init__("ceo", CEO_SYSTEM)
        self._project_queue: List[dict] = []

    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        await self.emit_start(project)
        try:
            prompt = ceo_analysis_prompt(project)
            result = await self.think(prompt, max_tokens=1500)

            # Store decision in shared state
            from core.memory import memory_bus
            memory_bus.set_state(f"ceo_decision_{project['id']}", result)

            # Persist to DB
            if db:
                await crud.write_memory(
                    db=db,
                    agent_id=self.agent_id,
                    action="strategic_analysis",
                    result=str(result),
                    project_id=project.get("id"),
                    tags=["strategy", "decision"],
                    success=True,
                )
                await crud.save_report(db, {
                    "project_id": project.get("id"),
                    "report_type": "ceo_analysis",
                    "agent_id": self.agent_id,
                    "content": result,
                    "summary": result.get("strategic_assessment", ""),
                })

            await self.emit_done(project, result)
            return result

        except Exception as e:
            await self.emit_error(project, str(e))
            return {"error": str(e)}

    async def prioritize_projects(self, projects: List[dict]) -> List[dict]:
        """Sort projects by strategic value."""
        await self.emit("CEO_PRIORITIZING", {"count": len(projects)})

        def priority_score(p):
            return (
                p.get("profit_score", 0) * 0.4 +
                p.get("stability_score", 0) * 0.3 +
                p.get("success_prediction", 0) / 10 * 0.3
            )

        sorted_projects = sorted(projects, key=priority_score, reverse=True)
        await self.emit("CEO_PRIORITIZED", {
            "top_project": sorted_projects[0]["name"] if sorted_projects else None
        })
        return sorted_projects

    async def decide_agents(self, project: dict, analysis: dict) -> List[str]:
        """Determine which agents should run on this project."""
        recommended = analysis.get("recommended_agents", [])
        priority = analysis.get("priority", "MEDIUM")

        agents = list(recommended)

        # Always add analyst
        if "analyst" not in agents:
            agents.append("analyst")

        # High priority → add security + architect
        if priority == "HIGH":
            for a in ["security", "architect"]:
                if a not in agents:
                    agents.append(a)

        # High profit score → add monetization
        if project.get("profit_score", 0) >= 7.0:
            if "monetization" not in agents:
                agents.append("monetization")

        return agents

    async def generate_executive_summary(self, all_results: List[dict]) -> dict:
        """Generate an executive summary across all projects."""
        prompt = f"""You are the CEO AI. Generate an executive summary based on analysis of {len(all_results)} projects.

Projects analyzed: {[r.get('project_name', 'unknown') for r in all_results]}
High priority count: {sum(1 for r in all_results if r.get('priority') == 'HIGH')}
Average profit potential: {sum(r.get('profit_score', 0) for r in all_results) / max(len(all_results), 1):.1f}/10

Return JSON:
{{
  "executive_summary": "string",
  "total_projects": {len(all_results)},
  "high_value_count": 0,
  "top_recommendations": ["rec1", "rec2", "rec3"],
  "estimated_total_value": "string",
  "next_90_day_plan": ["step1", "step2", "step3"],
  "immediate_actions": ["action1", "action2"]
}}"""

        return await self.think(prompt, max_tokens=1000)
