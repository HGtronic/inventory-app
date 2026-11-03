---
description: Start the frontend and backend servers
---

Stop any existing app servers on ports 3000 and the backend port, then start both the backend (FastAPI, port 8001 by default) and frontend (Vite on port 3000) development servers in the background.

The backend port is 8001 unless `API_PORT` is set. If it is, start the backend with that `API_PORT` and the frontend with `VITE_API_BASE_URL=http://localhost:$API_PORT/api` (or rely on `client/.env`, see `.env.example`).

**Backend:** `cd server && uv run python main.py` (with `API_PORT=<port>` prefixed when overriding)
**Frontend:** `cd client && npm run dev`

To stop existing app servers on a port, kill only this app's own listeners (Python for the backend, Node for the frontend). Another program, such as Docker, may hold the same port and must not be killed:
- macOS/Linux: list listeners with `lsof -nP -iTCP:<port> -sTCP:LISTEN`, check the command column, then `kill <pid>` for the python/node ones
- Windows: Use `netstat -aon | findstr :PORT` to find PIDs, check them with `tasklist /FI "PID eq <pid>"`, then `taskkill /F /PID <pid>`

After starting, verify:
- Backend: http://localhost:8001/docs (or the `API_PORT` in use)
- Frontend: http://localhost:3000
