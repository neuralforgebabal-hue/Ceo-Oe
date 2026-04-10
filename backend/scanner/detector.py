"""
CEO AI OS - Project Scanner / Detector
Walks the filesystem and identifies project directories.
"""
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import settings
from core.logger import get_logger

logger = get_logger("scanner.detector")

# Signature files that identify project types
PROJECT_SIGNATURES = {
    "python":      ["main.py", "app.py", "setup.py", "pyproject.toml", "requirements.txt"],
    "bot":         ["bot.py", "telegram_bot.py", "bot_main.py", "handlers.py"],
    "web":         ["index.html", "package.json", "webpack.config.js", "vite.config.js"],
    "ai":          ["agent.py", "llm.py", "model.py", "train.py", "inference.py"],
    "flask":       ["app.py", "wsgi.py"],
    "fastapi":     ["main.py"],
    "react":       ["package.json"],
    "docker":      ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "node":        ["package.json", "index.js", "server.js"],
    "rust":        ["Cargo.toml"],
    "go":          ["go.mod", "main.go"],
    "data_science":["notebook.ipynb", "*.ipynb", "data_analysis.py"],
}

IGNORE_DIRS = set(settings.excluded_dirs)
MAX_DEPTH = 4
MIN_FILES = 1


def _hash_path(path: str) -> str:
    return hashlib.md5(path.encode()).hexdigest()[:16]


def _detect_type(files: List[str], dirs: List[str]) -> str:
    file_set = set(files)
    # Order matters - more specific first
    if any(f in file_set for f in ["bot.py", "telegram_bot.py", "bot_main.py"]):
        return "bot"
    if any(f in file_set for f in ["agent.py", "llm.py", "train.py"]):
        return "ai"
    if "package.json" in file_set and ("src" in dirs or "public" in dirs):
        return "web"
    if any(f in file_set for f in ["main.py", "app.py", "requirements.txt", "setup.py"]):
        return "python"
    if "package.json" in file_set:
        return "node"
    if "Cargo.toml" in file_set:
        return "rust"
    if "go.mod" in file_set:
        return "go"
    return "unknown"


def _detect_framework(files: List[str], path: Path) -> Optional[str]:
    file_set = set(files)
    if "requirements.txt" in file_set:
        try:
            reqs = (path / "requirements.txt").read_text(errors="ignore").lower()
            if "fastapi" in reqs:
                return "fastapi"
            if "flask" in reqs:
                return "flask"
            if "django" in reqs:
                return "django"
            if "telegram" in reqs or "aiogram" in reqs or "python-telegram-bot" in reqs:
                return "telegram-bot"
        except Exception:
            pass
    if "package.json" in file_set:
        try:
            import json
            pkg = json.loads((path / "package.json").read_text(errors="ignore"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "react" in deps:
                return "react"
            if "vue" in deps:
                return "vue"
            if "express" in deps:
                return "express"
        except Exception:
            pass
    return None


def _detect_language(files: List[str]) -> str:
    ext_counts: Dict[str, int] = {}
    for f in files:
        ext = Path(f).suffix.lower()
        if ext:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    if not ext_counts:
        return "unknown"
    ext = max(ext_counts, key=ext_counts.get)
    return {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".rs": "Rust", ".go": "Go", ".java": "Java", ".rb": "Ruby",
        ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".c": "C",
    }.get(ext, ext.lstrip(".").capitalize() or "unknown")


def _collect_dependencies(path: Path, files: List[str]) -> List[str]:
    deps = []
    if "requirements.txt" in files:
        try:
            raw = (path / "requirements.txt").read_text(errors="ignore")
            deps = [l.split("==")[0].split(">=")[0].strip()
                    for l in raw.splitlines() if l.strip() and not l.startswith("#")]
        except Exception:
            pass
    elif "package.json" in files:
        try:
            import json
            pkg = json.loads((path / "package.json").read_text(errors="ignore"))
            deps = list(pkg.get("dependencies", {}).keys())
        except Exception:
            pass
    return deps[:30]  # cap at 30


def _count_lines(path: Path, files: List[str]) -> int:
    total = 0
    code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java"}
    for f in files:
        if Path(f).suffix in code_exts:
            try:
                content = (path / f).read_text(errors="ignore")
                total += len(content.splitlines())
            except Exception:
                pass
    return total


def scan_directory(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Walk root dir and return list of detected project metadata dicts."""
    root = root or settings.scan_root_path
    projects = []
    logger.info(f"Scanning {root} ...")

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored dirs in-place to stop recursion into them
        dirnames[:] = [
            d for d in dirnames
            if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        # Depth guard
        rel = Path(dirpath).relative_to(root)
        if len(rel.parts) > MAX_DEPTH:
            dirnames.clear()
            continue

        path = Path(dirpath)

        # Must have minimum files to be a project
        if len(filenames) < MIN_FILES:
            continue

        # Must have at least one code-ish file
        has_code = any(
            Path(f).suffix in {".py", ".js", ".ts", ".go", ".rs", ".java", ".rb", ".php"}
            or f in {"requirements.txt", "package.json", "Cargo.toml", "go.mod"}
            for f in filenames
        )
        if not has_code:
            continue

        proj_type = _detect_type(filenames, dirnames)
        if proj_type == "unknown" and len(rel.parts) == 0:
            continue  # skip bare root

        framework = _detect_framework(filenames, path)
        language = _detect_language(filenames)
        dependencies = _collect_dependencies(path, filenames)
        total_lines = _count_lines(path, filenames)

        try:
            last_mod = datetime.utcfromtimestamp(path.stat().st_mtime)
        except Exception:
            last_mod = None

        project = {
            "id": _hash_path(str(path)),
            "name": path.name,
            "path": str(path),
            "project_type": proj_type,
            "language": language,
            "framework": framework,
            "file_count": len(filenames),
            "total_lines": total_lines,
            "dependencies": dependencies,
            "has_dockerfile": any(f in filenames for f in ["Dockerfile", "docker-compose.yml"]),
            "has_tests": any("test" in f.lower() for f in filenames + dirnames),
            "has_env": ".env" in filenames or ".env.example" in filenames,
            "has_git": ".git" in dirnames or (path / ".git").exists(),
            "readme_exists": any(f.lower().startswith("readme") for f in filenames),
            "last_modified": last_mod,
            "metadata_extra": {
                "dirs": dirnames[:20],
                "sample_files": filenames[:20],
            }
        }
        projects.append(project)
        logger.debug(f"Found project: {project['name']} ({proj_type})")

    logger.info(f"Scan complete. Found {len(projects)} projects.")
    return projects
