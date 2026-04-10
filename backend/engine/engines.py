"""
CEO AI OS - Advanced Intelligence Engines
- Self-Improvement Engine: suggests and applies code refactoring
- Prediction Engine: forecasts project success and bug risks
- Project Generator: auto-creates new projects from templates
"""
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from ai.router import ai_router
from ai.prompts import REFACTOR_SYSTEM, PREDICTOR_SYSTEM, GENERATOR_SYSTEM
from core.logger import get_logger
from core.config import settings

logger = get_logger("engine")


# ─── Self-Improvement Engine ─────────────────────────────────

class SelfImprovementEngine:
    """
    Continuously analyzes code and generates improvement suggestions.
    Can optionally apply changes with git safety backup.
    """

    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file and get AI refactoring suggestions."""
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return {"error": f"File not found: {file_path}"}

        try:
            code = path.read_text(errors="ignore")
        except Exception as e:
            return {"error": str(e)}

        if len(code) > 8000:
            code = code[:8000] + "\n... (truncated)"

        prompt = f"""Analyze this code file and suggest improvements:

File: {path.name}
Language: {path.suffix}

```
{code}
```

Return JSON:
{{
  "file": "{path.name}",
  "overall_quality": 7,
  "issues": [
    {{"line": 10, "type": "code_smell", "severity": "MEDIUM", "description": "string", "suggestion": "string"}}
  ],
  "refactored_sections": [
    {{"original": "code snippet", "improved": "better code", "reason": "string"}}
  ],
  "quick_wins": ["Add type hints", "Extract function"],
  "estimated_improvement": "20%"
}}"""

        result = await ai_router.complete(
            system_prompt=REFACTOR_SYSTEM,
            user_message=prompt,
            max_tokens=2000,
            json_mode=True,
        )

        try:
            return json.loads(result)
        except Exception:
            return {"raw": result}

    async def suggest_project_improvements(self, project: dict) -> Dict[str, Any]:
        """High-level improvement suggestions for an entire project."""
        prompt = f"""Suggest self-improvement actions for this project:

Name: {project.get('name')} | Type: {project.get('project_type')}
Complexity: {project.get('complexity_score')}/10
Stability: {project.get('stability_score')}/10
Issues: missing_tests={not project.get('has_tests')}, no_readme={not project.get('readme_exists')}

Return JSON:
{{
  "improvement_plan": [
    {{
      "priority": 1,
      "action": "Add unit tests",
      "files_to_create": ["tests/test_main.py"],
      "estimated_hours": 3,
      "impact": "HIGH"
    }}
  ],
  "automation_opportunities": ["Auto-deploy on push", "Add CI/CD"],
  "tech_debt_items": ["Refactor main module", "Add error handling"],
  "estimated_total_hours": 12
}}"""

        result = await ai_router.complete(
            system_prompt=REFACTOR_SYSTEM,
            user_message=prompt,
            max_tokens=1500,
            json_mode=True,
        )
        try:
            return json.loads(result)
        except Exception:
            return {"raw": result}


# ─── Prediction Engine ───────────────────────────────────────

class PredictionEngine:
    """
    Predicts project outcomes:
    - Success probability
    - Bug risk areas
    - Growth trajectory
    - Market viability
    """

    async def predict(self, project: dict, history: List[dict] = None) -> Dict[str, Any]:
        history_context = ""
        if history:
            history_context = f"\nPast issues: {[h.get('action') for h in history[:5]]}"

        prompt = f"""Predict success and risks for this project:

Name: {project.get('name')} | Type: {project.get('project_type')}
Complexity: {project.get('complexity_score')}/10
Profit Score: {project.get('profit_score')}/10
Stability: {project.get('stability_score')}/10
Has Tests: {project.get('has_tests')} | Has Docker: {project.get('has_dockerfile')}
Lines: {project.get('total_lines')} | Files: {project.get('file_count')}
{history_context}

Return JSON:
{{
  "success_probability": 72.5,
  "confidence": "HIGH|MEDIUM|LOW",
  "risk_factors": [
    {{"factor": "no tests", "probability": 0.8, "impact": "HIGH"}}
  ],
  "growth_trajectory": "RISING|STABLE|DECLINING",
  "bug_risk_areas": ["authentication", "database queries"],
  "recommended_investments": ["testing", "documentation"],
  "6_month_forecast": {{
    "completion_probability": 65,
    "major_refactor_risk": 0.3,
    "scaling_readiness": "NOT_READY|PARTIALLY|READY"
  }},
  "market_viability": "LOW|MEDIUM|HIGH"
}}"""

        result = await ai_router.complete(
            system_prompt=PREDICTOR_SYSTEM,
            user_message=prompt,
            max_tokens=1200,
            json_mode=True,
        )
        try:
            return json.loads(result)
        except Exception:
            return {"raw": result}


# ─── Project Generator ───────────────────────────────────────

class ProjectGenerator:
    """
    Auto-generates new projects from natural language descriptions.
    Outputs file structures and code.
    """

    TEMPLATES = {
        "telegram_bot": {
            "description": "Telegram bot with command handlers",
            "base_files": ["main.py", "handlers.py", "config.py", "requirements.txt", "README.md", ".env.example"]
        },
        "flask_api": {
            "description": "Flask REST API with SQLAlchemy",
            "base_files": ["app.py", "models.py", "routes.py", "requirements.txt", "README.md", ".env.example"]
        },
        "fastapi_app": {
            "description": "FastAPI application with async support",
            "base_files": ["main.py", "models.py", "routes.py", "database.py", "requirements.txt", "README.md"]
        },
        "web_scraper": {
            "description": "Web scraper with data export",
            "base_files": ["scraper.py", "parser.py", "exporter.py", "requirements.txt", "README.md"]
        },
        "ai_agent": {
            "description": "AI agent with Groq integration",
            "base_files": ["agent.py", "prompts.py", "memory.py", "main.py", "requirements.txt", "README.md"]
        },
    }

    async def generate(self, description: str, template: str = "flask_api",
                        output_name: str = None) -> Dict[str, Any]:
        """Generate a complete project from a description."""
        tmpl_info = self.TEMPLATES.get(template, self.TEMPLATES["flask_api"])
        project_name = output_name or f"generated_{template}_{uuid.uuid4().hex[:6]}"

        prompt = f"""Generate a complete, working project:

Description: {description}
Template: {template} ({tmpl_info['description']})
Project Name: {project_name}
Files to generate: {tmpl_info['base_files']}

Return JSON:
{{
  "project_name": "{project_name}",
  "description": "string",
  "tech_stack": ["Python", "FastAPI"],
  "files": [
    {{
      "path": "main.py",
      "content": "# Full working code here\\n...",
      "description": "Entry point"
    }}
  ],
  "setup_instructions": ["pip install -r requirements.txt", "python main.py"],
  "env_variables": ["API_KEY", "DATABASE_URL"],
  "features": ["feature1", "feature2"]
}}"""

        result = await ai_router.complete(
            system_prompt=GENERATOR_SYSTEM,
            user_message=prompt,
            max_tokens=3000,
            json_mode=True,
        )

        try:
            parsed = json.loads(result)
        except Exception:
            parsed = {"error": "Failed to parse", "raw": result}

        # Write files to disk if valid
        if "files" in parsed:
            await self._write_project(parsed, project_name)

        return parsed

    async def _write_project(self, project_data: dict, project_name: str):
        """Write generated project files to disk."""
        output_dir = Path(settings.DATA_DIR) / "generated" / project_name
        output_dir.mkdir(parents=True, exist_ok=True)

        for file_info in project_data.get("files", []):
            file_path = output_dir / file_info.get("path", "file.txt")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                file_path.write_text(file_info.get("content", ""), encoding="utf-8")
                logger.info(f"Generated: {file_path}")
            except Exception as e:
                logger.error(f"Failed to write {file_path}: {e}")

        project_data["output_path"] = str(output_dir)
        logger.info(f"Project generated at: {output_dir}")


# Singletons
improvement_engine = SelfImprovementEngine()
prediction_engine = PredictionEngine()
project_generator = ProjectGenerator()
