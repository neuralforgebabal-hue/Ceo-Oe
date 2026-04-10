<<<<<<< HEAD

=======
# CEO AI Operating System

> A self-improving, multi-agent AI system that manages, analyzes, and optimizes all your local projects.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              React Dashboard (port 3000)            │
│    Dashboard · Projects · Agents · Tasks · Memory   │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP + WebSocket
┌───────────────────────▼─────────────────────────────┐
│              FastAPI Backend (port 8000)             │
│    /api/projects · /api/agents · /api/engine · /ws  │
└──────┬────────────────┬────────────────┬────────────┘
       │                │                │
  ┌────▼────┐    ┌──────▼──────┐   ┌────▼────────┐
  │ Scanner │    │  7 Agents   │   │  AI Router  │
  │  ~/     │    │  CEO+6 Sub  │   │ Groq/OpenAI │
  └─────────┘    └──────┬──────┘   └─────────────┘
                        │
                ┌───────▼────────┐
                │  Memory Bus    │
                │  SQLite + RAM  │
                └───────┬────────┘
                        │
         ┌──────────────┼──────────────┐
    ┌────▼────┐   ┌─────▼─────┐  ┌────▼──────┐
    │Predictor│   │ Refactor  │  │ Generator │
    └─────────┘   └───────────┘  └───────────┘
```

---

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/ceo-os.git
cd ceo-os
chmod +x setup.sh start.sh
./setup.sh
```

### 2. Configure API Key
```bash
nano .env
# Set: GROQ_API_KEY=your_key_here
# Get free key: https://console.groq.com
```

### 3. Start System
```bash
./start.sh
# Dashboard: http://localhost:3000
# API Docs:  http://localhost:8000/docs
```

---

## Termux (Android) Setup

```bash
# Install dependencies
pkg update && pkg install python nodejs git -y

# Clone & setup
git clone https://github.com/YOUR_USERNAME/ceo-os.git
cd ceo-os
chmod +x setup.sh start_termux.sh
./setup.sh

# Edit .env
nano .env

# Start (optional: install tmux for split panes)
pkg install tmux -y
./start_termux.sh

# Or manual start:
# Terminal 1:
cd backend && python main.py
# Terminal 2:
cd frontend && npm run dev
```

---

## Docker Start

```bash
cp .env.example .env
nano .env  # add your keys
docker-compose up --build
```

---

## Feature Map

| Feature | Description |
|---------|-------------|
| **Project Scanner** | Recursively walks `~/`, detects type, language, framework |
| **Smart Classification** | Scores each project: complexity, profit, stability, success% |
| **CEO Agent** | Master orchestrator — prioritizes projects, assigns agents |
| **Architect Agent** | Architecture analysis, design patterns, scalability rating |
| **Developer Agent** | Code quality, bugs, refactor suggestions |
| **Security Agent** | Vulnerability scan, secret detection, OWASP checks |
| **Analyst Agent** | Performance metrics, technical debt, KPIs |
| **Monetization Agent** | Revenue strategies, pricing, market analysis |
| **Deployment Agent** | Docker, Render, Vercel deployment plans |
| **Memory Bus** | Shared real-time state + event queue for all agents |
| **Prediction Engine** | AI-powered success probability & risk forecasting |
| **Self-Improvement Engine** | Code refactor suggestions per file or project |
| **Project Generator** | Auto-generates complete projects from text descriptions |
| **WebSocket Dashboard** | Real-time agent activity feed |
| **Telegram Alerts** | Notifications for scans, critical issues, completions |

---

## API Endpoints

```
GET    /api/projects/          List all scanned projects
POST   /api/projects/scan      Trigger ~/  scan
GET    /api/projects/{id}      Project detail + reports
GET    /api/projects/stats/summary  System statistics

GET    /api/agents/            List agents + statuses
POST   /api/agents/run         Run one agent on a project
POST   /api/agents/run-all     Run all agents on a project
GET    /api/agents/events      Recent bus events

GET    /api/tasks/             Task queue (all or by status)

GET    /api/memory/            Agent memories
GET    /api/memory/bus         Live bus events + stats
GET    /api/memory/state       Shared state + agent statuses

GET    /api/reports/{id}       Project reports

POST   /api/engine/predict     AI success prediction
POST   /api/engine/improve     Improvement suggestions
POST   /api/engine/generate    Auto-generate project
POST   /api/engine/analyze-file  File-level refactor analysis
GET    /api/engine/templates   Available project templates

WS     /ws                     Real-time WebSocket stream
```

---

## Configuration (.env)

```env
# AI (get free key at console.groq.com)
AI_PROVIDER=groq
GROQ_API_KEY=your_key_here
AI_MODEL=llama-3.3-70b-versatile

# Optional fallbacks
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Scanner
SCAN_ROOT=~/
SCAN_EXCLUDE=.git,node_modules,__pycache__,.venv

# Alerts (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# DB (default: SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/ceo_os.db
```

---

## Project Structure

```
ceo-os/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── core/                # Config, Logger, Memory Bus
│   ├── scanner/             # Detector + Classifier
│   ├── agents/              # Base + CEO + 6 Sub-agents
│   ├── ai/                  # Router (Groq/OpenAI/Anthropic) + Prompts
│   ├── engine/              # Predictor, Refactor, Generator
│   ├── api/                 # REST routes (6 routers)
│   ├── db/                  # SQLAlchemy models + CRUD
│   └── monitoring/          # Telegram alerts
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, Projects, Agents, Tasks, Generator, Memory
│       ├── api/             # Axios client
│       └── hooks/           # WebSocket hook
├── docker/                  # Dockerfiles
├── docker-compose.yml
├── setup.sh                 # One-command setup
├── start.sh                 # Launch both services
└── start_termux.sh          # Termux-specific launcher
```

---

## Extending the System

### Add a New Agent
```python
# backend/agents/sub_agents.py
class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom", "You are a custom agent...")

    async def run(self, project, db=None):
        await self.emit_start(project)
        result = await self.think(f"Analyze: {project['name']}")
        await self.emit_done(project, result)
        return result

# Register it:
AGENT_REGISTRY["custom"] = MyCustomAgent
```

### Add a New API Route
```python
# backend/api/myroute.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def my_endpoint(): return {"ok": True}

# In main.py:
app.include_router(myroute.router, prefix="/api/custom")
```

---

## Deployment

### Render (Backend)
1. Push to GitHub
2. New Web Service → connect repo → set root to `backend/`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars in Render dashboard

### Vercel (Frontend)
```bash
cd frontend
npm install -g vercel
vercel --prod
# Set VITE_API_URL env var to your Render backend URL
```

---

## License
MIT — Build freely, sell if you want.
>>>>>>> b938359 (init)
