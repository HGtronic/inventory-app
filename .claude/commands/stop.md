---
description: Stop the frontend and backend servers
---

Find and stop this app's servers: the frontend on port 3000 and the backend on port 8001 (or `API_PORT` if set).

Kill only this app's own listeners (Python for the backend, Node for the frontend). Another program, such as Docker, may hold the same port and must not be killed:
- macOS/Linux: list listeners with `lsof -nP -iTCP:<port> -sTCP:LISTEN`, check the command column, then `kill <pid>` for the python/node ones
- Windows: Use `netstat -aon | findstr :PORT` to find PIDs, check them with `tasklist /FI "PID eq <pid>"`, then `taskkill /F /PID <pid>`
