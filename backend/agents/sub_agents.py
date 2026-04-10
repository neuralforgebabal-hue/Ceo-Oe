"""
CEO AI OS - Sub-Agents
Architect, Developer, Security, Analyst, Monetization, Deployment
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from ai.prompts import (
    ARCHITECT_SYSTEM, architect_analysis_prompt,
    DEVELOPER_SYSTEM,
    SECURITY_SYSTEM, security_scan_prompt,
    ANALYST_SYSTEM, analyst_prompt,
    MONETIZATION_SYSTEM, monetization_prompt,
    DEPLOYMENT_SYSTEM, deployment_prompt,
)
from db import crud


# ─── Architect Agent ──────────────────────────────────────────

class ArchitectAgent(BaseAgent):
    """Analyzes project structure and recommends architectural improvements."""

    def __init__(self):
        super().__init__("architect", ARCHITECT_SYSTEM)

    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        await self.emit_start(project)
        try:
            result = await self.think(architect_analysis_prompt(project))

            if db:
                await crud.write_memory(db, self.agent_id, "architecture_analysis",
                                         str(result), project.get("id"), ["architecture"])
                await crud.save_report(db, {
                    "project_id": project.get("id"),
                    "report_type": "architecture",
                    "agent_id": self.agent_id,
                    "content": result,
                    "summary": f"Score: {result.get('architecture_score', 'N/A')}/10 | Pattern: {result.get('pattern_detected', 'Unknown')}",
                })

            await self.emit_done(project, result)
            return result
        except Exception as e:
            await self.emit_error(project, str(e))
            return {"error": str(e)}


# ─── Developer Agent ─────────────────────────────────────────

class DeveloperAgent(BaseAgent):
    """Detects code issues and generates fix suggestions."""

    def __init__(self):
        super().__init__("developer", DEVELOPER_SYSTEM)

    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        await self.emit_start(project)
        try:
            prompt = f"""Analyze code quality and suggest improvements for:

Project: {project.get('name')}
Type: {project.get('project_type')} | Framework: {project.get('framework')}
Language: {project.get('language')}
Lines: {project.get('total_lines')} | Files: {project.get('file_count')}
Has Tests: {project.get('has_tests')} | Has README: {project.get('readme_exists')}
Dependencies: {project.get('dependencies', [])[:10]}

Return JSON:
{{
  "code_quality_score": 7.0,
  "issues": [
    {{"type": "missing_tests", "severity": "HIGH", "description": "string", "fix": "string"}}
  ],
  "quick_improvements": ["Add type hints", "Add docstrings"],
  "refactor_suggestions": [
    {{"file": "main.py", "current": "...", "suggested": "...", "reason": "string"}}
  ],
  "missing_features": ["error handling", "logging"],
  "estimated_fix_time": "4 hours"
}}"""

            result = await self.think(prompt)

            if db:
                await crud.write_memory(db, self.agent_id, "code_analysis",
                                         str(result), project.get("id"), ["code", "quality"])
                await crud.save_report(db, {
                    "project_id": project.get("id"),
                    "report_type": "developer",
                    "agent_id": self.agent_id,
                    "content": result,
                    "summary": f"Quality: {result.get('code_quality_score', 'N/A')}/10 | Issues: {len(result.get('issues', []))}",
                })

            await self.emit_done(project, result)
            return result
        except Exception as e:
            await self.emit_error(project, str(e))
            return {"error": str(e)}


# ─── Security Agent ───────────────────────────────────────────

class SecurityAgent(BaseAgent):
    """Scans for vulnerabilities, exposed secrets, and security risks."""

    def __init__(self):
        super().__init__("security", SECURITY_SYSTEM)

    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        await self.emit_start(project)
        try:
            # Also do a quick local file scan for obvious secrets
            local_scan = await self._local_secret_scan(project)
            result = await self.think(security_scan_prompt(project))

            # Merge local scan findings
            if local_scan.get("found_issues"):
                existing_vulns = result.get("vulnerabilities", [])
                existing_vulns.extend(local_scan["issues"])
                result["vulnerabilities"] = existing_vulns
                result["exposed_secrets_risk"] = True

            if db:
                await crud.write_memory(db, self.agent_id, "security_scan",
                                         str(result), project.get("id"),
                                         ["security", result.get("risk_level", "UNKNOWN").lower()])
                await crud.save_report(db, {
                    "project_id": project.get("id"),
                    "report_type": "security",
                    "agent_id": self.agent_id,
                    "content": result,
                    "summary": f"Risk: {result.get('risk_level')} | Vulns: {len(result.get('vulnerabilities', []))}",
                })

            await self.emit_done(project, result)
            return result
        except Exception as e:
            await self.emit_error(project, str(e))
            return {"error": str(e)}

    async def _local_secret_scan(self, project: dict) -> dict:
        """Quick local scan for hardcoded secrets."""
        import os
        import re
        from pathlib import Path

        SECRET_PATTERNS = [
            (r'(?i)(api_key|apikey|secret|token|password|passwd)\s*=\s*["\'][A-Za-z0-9_\-]{8,}["\']', "Hardcoded secret"),
            (r'sk-[A-Za-z0-9]{20,}', "OpenAI API Key"),
            (r'xox[baprs]-[A-Za-z0-9\-]+', "Slack Token"),
            (r'ghp_[A-Za-z0-9]{36}', "GitHub Token"),
        ]

        path = Path(project.get("path", ""))
        issues = []

        if not path.exists():
            return {"found_issues": False, "issues": []}

        for fname in os.listdir(path):
            if fname.startswith(".") or not fname.endswith((".py", ".js", ".env", ".txt")):
                continue
            try:
                content = (path / fname).read_text(errors="ignore")
                for pattern, label in SECRET_PATTERNS:
                    if re.search(pattern, content):
                        issues.append({
                            "id": f"LOCAL_{label.replace(' ', '_').upper()}",
                            "title": f"Potential {label} in {fname}",
                            "severity": "CRITICAL",
                            "description": f"Possible hardcoded secret found in {fname}",
                            "fix": "Move to environment variable in .env file"
                        })
            except Exception:
                continue

        return {"found_issues": len(issues) > 0, "issues": issues}


# ─── Analyst Agent ────────────────────────────────────────────

class AnalystAgent(BaseAgent):
    """Analyzes performance, code quality metrics, and technical debt."""

    def __init__(self):
        super().__init__("analyst", ANALYST_SYSTEM)

    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        await self.emit_start(project)
        try:
            result = await self.think(analyst_prompt(project))

            if db:
                await crud.write_memory(db, self.agent_id, "performance_analysis",
                                         str(result), project.get("id"), ["analytics", "metrics"])
                await crud.save_report(db, {
                    "project_id": project.get("id"),
                    "report_type": "analysis",
                    "agent_id": self.agent_id,
                    "content": result,
                    "summary": f"Quality: {result.get('quality_score', 'N/A')}/10 | Debt: {result.get('technical_debt_estimate', 'N/A')}",
                })

            await self.emit_done(project, result)
            return result
        except Exception as e:
            await self.emit_error(project, str(e))
            return {"error": str(e)}


# ─── Monetization Agent ───────────────────────────────────────

class MonetizationAgent(BaseAgent):
    """Suggests revenue strategies and monetization paths."""

    def __init__(self):
        super().__init__("monetization", MONETIZATION_SYSTEM)

    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        await self.emit_start(project)
        try:
            result = await self.think(monetization_prompt(project))

            if db:
                await crud.write_memory(db, self.agent_id, "monetization_strategy",
                                         str(result), project.get("id"), ["revenue", "business"])
                await crud.save_report(db, {
                    "project_id": project.get("id"),
                    "report_type": "monetization",
                    "agent_id": self.agent_id,
                    "content": result,
                    "summary": f"Potential: {result.get('revenue_potential')} | Est: {result.get('estimated_monthly_revenue', 'N/A')}",
                })

            await self.emit_done(project, result)
            return result
        except Exception as e:
            await self.emit_error(project, str(e))
            return {"error": str(e)}


# ─── Deployment Agent ─────────────────────────────────────────

class DeploymentAgent(BaseAgent):
    """Creates deployment plans and generates config files."""

    def __init__(self):
        super().__init__("deployment", DEPLOYMENT_SYSTEM)

    async def run(self, project: Dict[str, Any], db=None) -> Dict[str, Any]:
        await self.emit_start(project)
        try:
            result = await self.think(deployment_prompt(project))

            # Auto-generate Dockerfile if missing and feasible
            if not project.get("has_dockerfile"):
                dockerfile = await self._generate_dockerfile(project)
                result["generated_dockerfile"] = dockerfile

            if db:
                await crud.write_memory(db, self.agent_id, "deployment_plan",
                                         str(result), project.get("id"), ["deployment", "devops"])
                await crud.save_report(db, {
                    "project_id": project.get("id"),
                    "report_type": "deployment",
                    "agent_id": self.agent_id,
                    "content": result,
                    "summary": f"Platform: {result.get('recommended_platform')} | Cost: {result.get('estimated_cost', 'N/A')}",
                })

            await self.emit_done(project, result)
            return result
        except Exception as e:
            await self.emit_error(project, str(e))
            return {"error": str(e)}

    async def _generate_dockerfile(self, project: dict) -> str:
        proj_type = project.get("project_type", "python")
        framework = project.get("framework", "")

        if proj_type == "python" or framework in ("fastapi", "flask", "django"):
            return """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]"""
        elif proj_type in ("web", "node"):
            return """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]"""
        else:
            return """FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt 2>/dev/null || true
EXPOSE 8000
CMD ["python", "main.py"]"""


# ─── Agent Registry ───────────────────────────────────────────

AGENT_REGISTRY = {
    "ceo": None,  # Lazy-loaded
    "architect": ArchitectAgent,
    "developer": DeveloperAgent,
    "security": SecurityAgent,
    "analyst": AnalystAgent,
    "monetization": MonetizationAgent,
    "deployment": DeploymentAgent,
}


def get_agent(agent_name: str) -> BaseAgent:
    from agents.ceo_agent import CEOAgent
    AGENT_REGISTRY["ceo"] = CEOAgent

    cls = AGENT_REGISTRY.get(agent_name)
    if not cls:
        raise ValueError(f"Unknown agent: {agent_name}")
    return cls()
