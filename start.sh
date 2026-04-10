#!/usr/bin/env bash
# CEO AI OS — Quick Start (both services)

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}Starting CEO AI Operating System...${NC}"
echo ""

cleanup() {
    echo -e "\n${RED}Shutting down...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
fi
echo -e "${GREEN}[✓] Starting backend on :8000${NC}"
python main.py &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
cd frontend
echo -e "${GREEN}[✓] Starting frontend on :3000${NC}"
npm run dev --silent &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Dashboard → ${GREEN}http://localhost:3000${NC}"
echo -e "  API Docs  → ${GREEN}http://localhost:8000/docs${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Press ${RED}Ctrl+C${NC} to stop"
echo ""

wait $BACKEND_PID $FRONTEND_PID
