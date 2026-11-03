#!/bin/bash

# Factory Inventory Management System - Stop Script
# This script stops both the backend and frontend servers

set -e  # Exit on error

# Colors for output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping Factory Inventory Management System...${NC}\n"

# Check if PID files exist
if [ -f /tmp/inventory-backend.pid ]; then
    BACKEND_PID=$(cat /tmp/inventory-backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping backend server (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID
    fi
    rm -f /tmp/inventory-backend.pid
fi

if [ -f /tmp/inventory-frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/inventory-frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping frontend server (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID
    fi
    rm -f /tmp/inventory-frontend.pid
fi

# Fallback: kill any remaining processes on the ports
echo -e "${YELLOW}Cleaning up any remaining processes...${NC}"

# Stops only listeners on $1 whose command matches $2. Another program (for
# example Docker) may hold the same port, and it must not be killed.
kill_app_on_port() {
    local port=$1 pattern=$2 pid
    for pid in $(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true); do
        if ps -o command= -p "$pid" | grep -qE "$pattern"; then
            kill "$pid" 2>/dev/null || true
        fi
    done
}

# Backend (port 8001 unless API_PORT is set, matching start.sh)
kill_app_on_port "${API_PORT:-8001}" "python|uvicorn"

# Frontend (port 3000)
kill_app_on_port 3000 "node|vite"

# Clean up log files
rm -f /tmp/inventory-backend.log
rm -f /tmp/inventory-frontend.log

echo -e "\n${GREEN}✓ All servers stopped successfully!${NC}"
