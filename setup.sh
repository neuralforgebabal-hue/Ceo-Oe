#!/usr/bin/env bash
# ============================================================
#  CEO AI Operating System — Setup Script
#  Supports: Linux, macOS, Termux (Android)
# ============================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${CYAN}[CEO-OS]${NC} $1"; }
ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo -e "${BOLD}${CYAN}"
echo "  ██████╗███████╗ ██████╗      █████╗ ██╗"
echo " ██╔════╝██╔════╝██╔═══██╗    ██╔══██╗██║"
echo " ██║     █████╗  ██║   ██║    ███████║██║"
echo " ██║     ██╔══╝  ██║   ██║    ██╔══██║██║"
echo " ╚██████╗███████╗╚██████╔╝    ██║  ██║██║"
echo "  ╚═════╝╚══════╝ ╚═════╝     ╚═╝  ╚═╝╚═╝"
echo -e "${NC}"
echo -e "${BOLD}  CEO AI Operating System — Setup${NC}"
echo "  ─────────────────────────────────────"
echo ""

# ─── Detect Environment ──────────────────────────────────────
IS_TERMUX=false
IS_MACOS=false

if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then
    IS_TERMUX=true
    log "Detected: Termux (Android)"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    IS_MACOS=true
    log "Detected: macOS"
else
    log "Detected: Linux"
fi

# ─── Check Python ─────────────────────────────────────────────
log "Checking Python..."
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    if $IS_TERMUX; then
        warn "Installing Python via pkg..."
        pkg install python -y
        PYTHON=python
    else
        err "Python 3.8+ required. Install from https://python.org"
    fi
fi
ok "Python: $($PYTHON --version)"

# ─── Check Node.js ───────────────────────────────────────────
log "Checking Node.js..."
if ! command -v node &>/dev/null; then
    if $IS_TERMUX; then
        warn "Installing Node.js via pkg..."
        pkg install nodejs -y
    elif $IS_MACOS; then
        warn "Install Node.js from https://nodejs.org or via brew: brew install node"
        err "Node.js 18+ required"
    else
        warn "Install Node.js 18+ from https://nodejs.org"
        err "Node.js 18+ required"
    fi
fi
ok "Node.js: $(node --version)"

# ─── Setup .env ──────────────────────────────────────────────
log "Setting up environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        ok "Created .env from .env.example"
        warn "Edit .env and add your API keys before running!"
    else
        warn ".env.example not found — creating minimal .env"
        cat > .env << 'ENVEOF'
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./data/ceo_os.db
SECRET_KEY=change_this_in_production_min_32_chars
SCAN_ROOT=~/
PORT=8000
FRONTEND_URL=http://localhost:3000
ENVEOF
    fi
else
    ok ".env already exists"
fi

# ─── Backend Setup ───────────────────────────────────────────
log "Setting up Python backend..."
cd backend

if $IS_TERMUX; then
    # Termux: install without venv (pkg already manages isolation)
    log "Installing Python packages (Termux mode)..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q || {
        warn "Some packages may need native build tools. Running with --no-deps fallback..."
        pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings \
            python-dotenv httpx groq cryptography aiofiles python-multipart \
            websockets schedule rich click requests psutil pyyaml -q
    }
else
    # Standard: use venv
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        $PYTHON -m venv venv
    fi
    log "Activating venv and installing packages..."
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
fi

mkdir -p data/logs
ok "Backend dependencies installed"
cd ..

# ─── Frontend Setup ──────────────────────────────────────────
log "Setting up React frontend..."
cd frontend
npm install --silent
ok "Frontend dependencies installed"
cd ..

echo ""
echo -e "${GREEN}${BOLD}  ✓ Setup Complete!${NC}"
echo ""
echo -e "  ${BOLD}Next steps:${NC}"
echo ""
echo -e "  1. ${YELLOW}Edit .env and add your GROQ_API_KEY${NC}"
echo -e "     Get free key: https://console.groq.com"
echo ""
echo -e "  2. ${CYAN}Start the backend:${NC}"
echo -e "     cd backend && python main.py"
echo ""
echo -e "  3. ${CYAN}Start the frontend (new terminal):${NC}"
echo -e "     cd frontend && npm run dev"
echo ""
echo -e "  4. ${CYAN}Open dashboard:${NC}"
echo -e "     http://localhost:3000"
echo ""
echo -e "  ${BOLD}Quick start (both services):${NC}"
echo -e "     ./start.sh"
echo ""
