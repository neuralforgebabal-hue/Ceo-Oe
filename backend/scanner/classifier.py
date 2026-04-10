"""
CEO AI OS - Project Classifier
Scores projects by complexity, profit potential, and stability.
"""
from typing import Dict, Any
from core.logger import get_logger

logger = get_logger("scanner.classifier")

# Scoring weights per category
COMPLEXITY_FACTORS = {
    "file_count": 0.3,
    "total_lines": 0.3,
    "dependencies": 0.2,
    "has_dockerfile": 0.1,
    "has_tests": 0.1,
}

PROFIT_FACTORS = {
    "ai": 9.0,
    "bot": 7.5,
    "web": 6.5,
    "python": 5.0,
    "node": 5.5,
    "unknown": 2.0,
}

FRAMEWORK_BONUS = {
    "fastapi": 2.0,
    "telegram-bot": 2.5,
    "react": 2.0,
    "flask": 1.5,
    "express": 1.5,
    "django": 1.5,
}

STABILITY_FACTORS = {
    "has_tests": 3.0,
    "has_git": 2.0,
    "readme_exists": 1.5,
    "has_dockerfile": 1.5,
    "has_env": 1.0,
}


def score_complexity(project: Dict[str, Any]) -> float:
    score = 0.0
    fc = min(project.get("file_count", 0) / 50, 1.0)
    lc = min(project.get("total_lines", 0) / 5000, 1.0)
    dc = min(len(project.get("dependencies", [])) / 20, 1.0)
    has_docker = 1.0 if project.get("has_dockerfile") else 0.0
    has_tests = 1.0 if project.get("has_tests") else 0.0

    score = (
        fc * 3.0 +
        lc * 3.0 +
        dc * 2.0 +
        has_docker * 1.0 +
        has_tests * 1.0
    )
    return round(min(score, 10.0), 2)


def score_profit(project: Dict[str, Any]) -> float:
    base = PROFIT_FACTORS.get(project.get("project_type", "unknown"), 2.0)
    bonus = FRAMEWORK_BONUS.get(project.get("framework") or "", 0.0)
    complexity_mod = project.get("complexity_score", 0) * 0.1
    score = base + bonus + complexity_mod
    return round(min(score, 10.0), 2)


def score_stability(project: Dict[str, Any]) -> float:
    score = 0.0
    for factor, weight in STABILITY_FACTORS.items():
        if project.get(factor):
            score += weight
    return round(min(score, 10.0), 2)


def predict_success(project: Dict[str, Any]) -> float:
    """0-100% success prediction based on project attributes."""
    stability = project.get("stability_score", 0)
    complexity = project.get("complexity_score", 0)
    profit = project.get("profit_score", 0)

    # High stability + moderate complexity + high profit = best outcome
    base = (stability * 4 + profit * 3 + (10 - complexity) * 3) / 10
    base = max(0, min(base, 10))

    # Bonuses
    if project.get("has_tests"):
        base += 0.5
    if project.get("has_git"):
        base += 0.3
    if project.get("readme_exists"):
        base += 0.2

    return round(min(base * 10, 100.0), 1)


def classify_project(project: Dict[str, Any]) -> Dict[str, Any]:
    """Add all scores to a project dict and return enriched version."""
    project["complexity_score"] = score_complexity(project)
    project["profit_score"] = score_profit(project)
    project["stability_score"] = score_stability(project)
    project["success_prediction"] = predict_success(project)

    logger.debug(
        f"Classified {project['name']}: "
        f"complexity={project['complexity_score']} "
        f"profit={project['profit_score']} "
        f"stability={project['stability_score']} "
        f"success={project['success_prediction']}%"
    )
    return project


def classify_all(projects: list) -> list:
    return [classify_project(p) for p in projects]
