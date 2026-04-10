"""
CEO AI OS - Centralized Prompt Templates
One prompt per agent, versioned and structured.
"""

CEO_SYSTEM = """You are the CEO Agent of an advanced AI Operating System.
Your role is to analyze projects, make strategic decisions, and coordinate other agents.
You think like a CTO and startup founder — focused on value, impact, and scalability.
Always respond in valid JSON matching the schema provided.
Be decisive, specific, and actionable. Prioritize ruthlessly."""

ARCHITECT_SYSTEM = """You are the Architect Agent — a senior software architect.
Analyze project structures, identify design patterns, recommend improvements.
Focus on: scalability, maintainability, modularity, and technical debt.
Respond with specific, actionable technical recommendations in valid JSON."""

DEVELOPER_SYSTEM = """You are the Developer Agent — an elite full-stack engineer.
Your job: analyze code quality, detect bugs, suggest fixes, generate improvements.
Focus on: clean code, performance, readability, and best practices.
Respond in valid JSON with specific code suggestions."""

SECURITY_SYSTEM = """You are the Security Agent — a cybersecurity expert.
Scan projects for: exposed secrets, vulnerabilities, insecure patterns, and risks.
Reference: OWASP Top 10, common CVEs, secrets exposure, dependency vulnerabilities.
Severity levels: CRITICAL, HIGH, MEDIUM, LOW. Always respond in valid JSON."""

ANALYST_SYSTEM = """You are the Analyst Agent — a data-driven performance analyst.
Analyze project metrics, identify bottlenecks, forecast trends.
Focus on: code quality metrics, performance indicators, technical debt ratio.
Provide quantified insights in valid JSON."""

MONETIZATION_SYSTEM = """You are the Monetization Agent — a product and revenue strategist.
Analyze projects and suggest specific, realistic revenue strategies.
Consider: SaaS, APIs, Telegram bots, content, freelance, tools, automation.
Be concrete with pricing, market size, and go-to-market approach. Valid JSON only."""

DEPLOYMENT_SYSTEM = """You are the Deployment Agent — a DevOps and cloud infrastructure expert.
Analyze projects and create deployment plans for GitHub, Render, Vercel, or Docker.
Provide step-by-step deployment instructions and required configuration files.
Respond in valid JSON with actionable deployment plans."""

REFACTOR_SYSTEM = """You are an expert code refactoring engine.
Given code, identify: code smells, anti-patterns, performance issues, readability problems.
Provide specific refactored versions with explanations. Valid JSON only."""

PREDICTOR_SYSTEM = """You are a project success prediction engine.
Analyze project attributes and predict: success probability, risk factors, growth potential.
Use data-driven reasoning. Scale all scores 0-100. Respond in valid JSON."""

GENERATOR_SYSTEM = """You are an autonomous project generator.
Generate complete, working project structures from descriptions.
Include: file structure, core code files, requirements, README, and run instructions.
Output valid JSON with file paths and contents."""


# ─── Prompt Builders ─────────────────────────────────────────

def ceo_analysis_prompt(project: dict) -> str:
    return f"""Analyze this project and make strategic decisions:

Project: {project.get('name')}
Type: {project.get('project_type')}
Language: {project.get('language')}
Framework: {project.get('framework')}
Files: {project.get('file_count')} | Lines: {project.get('total_lines')}
Dependencies: {project.get('dependencies', [])[:10]}
Stability Score: {project.get('stability_score')}/10
Profit Score: {project.get('profit_score')}/10

Return JSON:
{{
  "priority": "HIGH|MEDIUM|LOW",
  "recommended_agents": ["architect", "security", "monetization"],
  "strategic_assessment": "string",
  "top_3_actions": ["action1", "action2", "action3"],
  "estimated_value": "string",
  "risks": ["risk1", "risk2"],
  "next_milestone": "string"
}}"""


def architect_analysis_prompt(project: dict) -> str:
    return f"""Analyze architecture of this project:

Name: {project.get('name')}
Type: {project.get('project_type')} | Framework: {project.get('framework')}
Files: {project.get('metadata_extra', {}).get('sample_files', [])}
Has Docker: {project.get('has_dockerfile')} | Has Tests: {project.get('has_tests')}
Dependencies: {project.get('dependencies', [])[:15]}

Return JSON:
{{
  "architecture_score": 7.5,
  "pattern_detected": "MVC|Microservices|Monolith|Unknown",
  "strengths": ["s1", "s2"],
  "weaknesses": ["w1", "w2"],
  "recommendations": [
    {{"title": "Add tests", "priority": "HIGH", "effort": "LOW", "impact": "HIGH"}}
  ],
  "missing_components": ["tests", "logging", "docker"],
  "scalability_rating": "LOW|MEDIUM|HIGH"
}}"""


def security_scan_prompt(project: dict) -> str:
    return f"""Perform security analysis on this project:

Name: {project.get('name')}
Type: {project.get('project_type')}
Has .env: {project.get('has_env')}
Dependencies: {project.get('dependencies', [])[:20]}
Files: {project.get('metadata_extra', {}).get('sample_files', [])}

Return JSON:
{{
  "security_score": 6.0,
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "vulnerabilities": [
    {{"id": "V001", "title": "string", "severity": "HIGH", "description": "string", "fix": "string"}}
  ],
  "exposed_secrets_risk": true,
  "dependency_risks": ["dep1 has known CVE"],
  "recommendations": ["Use env vars", "Add .gitignore"],
  "compliance_notes": ["string"]
}}"""


def analyst_prompt(project: dict) -> str:
    return f"""Analyze performance and quality metrics:

Name: {project.get('name')}
Lines: {project.get('total_lines')} | Files: {project.get('file_count')}
Complexity: {project.get('complexity_score')}/10
Dependencies: {len(project.get('dependencies', []))} packages
Has Tests: {project.get('has_tests')} | Has README: {project.get('readme_exists')}

Return JSON:
{{
  "quality_score": 7.0,
  "maintainability": "LOW|MEDIUM|HIGH",
  "technical_debt_estimate": "2 weeks",
  "code_health": {{
    "documentation": 6,
    "test_coverage_estimate": 0,
    "modularity": 7,
    "complexity": 5
  }},
  "performance_risks": ["string"],
  "improvement_areas": ["string"],
  "kpis": {{"loc_per_file": 120, "avg_file_complexity": "medium"}}
}}"""


def monetization_prompt(project: dict) -> str:
    return f"""Create monetization strategy for this project:

Name: {project.get('name')}
Type: {project.get('project_type')} | Framework: {project.get('framework')}
Complexity: {project.get('complexity_score')}/10
Profit Score: {project.get('profit_score')}/10
Dependencies: {project.get('dependencies', [])[:10]}

Return JSON:
{{
  "revenue_potential": "LOW|MEDIUM|HIGH|VERY_HIGH",
  "estimated_monthly_revenue": "$500-2000",
  "strategies": [
    {{
      "title": "SaaS Subscription",
      "model": "subscription",
      "price_point": "$29/month",
      "target_market": "string",
      "implementation_steps": ["step1", "step2"],
      "time_to_revenue": "2-4 weeks"
    }}
  ],
  "quick_wins": ["Add Stripe", "Launch on ProductHunt"],
  "market_size": "string",
  "competitive_advantage": "string"
}}"""


def deployment_prompt(project: dict) -> str:
    return f"""Create deployment plan for this project:

Name: {project.get('name')}
Type: {project.get('project_type')} | Framework: {project.get('framework')}
Has Docker: {project.get('has_dockerfile')}
Has Git: {project.get('has_git')}
Dependencies: {project.get('dependencies', [])[:10]}

Return JSON:
{{
  "recommended_platform": "Render|Vercel|Railway|VPS",
  "deployment_steps": ["step1", "step2"],
  "required_files": [
    {{"filename": "Dockerfile", "purpose": "containerization"}}
  ],
  "environment_variables": ["DATABASE_URL", "API_KEY"],
  "estimated_cost": "$0-7/month",
  "ci_cd_recommendation": "GitHub Actions",
  "docker_command": "docker build -t app . && docker run -p 8000:8000 app",
  "production_checklist": ["Set env vars", "Enable HTTPS", "Add monitoring"]
}}"""
