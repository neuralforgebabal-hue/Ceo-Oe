#!/usr/bin/env bash
# CEO AI OS — Termux Start Script (Android)
# Uses tmux or sequential start for Termux environment

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${CYAN}CEO AI OS — Termux Start${NC}"
echo ""

# Check if tmux available for split sessions
if command -v tmux &>/dev/null; then
    echo -e "${GREEN}Starting with tmux (split panes)...${NC}"
    tmux new-session -d -s ceo-os -x 220 -y 50
    tmux split-window -h -t ceo-os
    # Left pane: backend
    tmux send-keys -t ceo-os:0.0 "cd $(pwd)/backend && python main.py" Enter
    # Right pane: frontend
    tmux send-keys -t ceo-os:0.1 "cd $(pwd)/frontend && npm run dev" Enter
    tmux attach-session -t ceo-os
else
    echo -e "${YELLOW}tmux not found. Starting backend only (run frontend manually).${NC}"
    echo -e "Install tmux: ${CYAN}pkg install tmux${NC}"
    echo ""
    echo -e "Starting backend on :8000..."
    cd backend && python main.py
fi
