#!/usr/bin/env bash
set -e

TASK_ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$TASK_ROOT/.." && pwd)"

port_owner() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null | head -1 || true
  elif command -v ss >/dev/null 2>&1; then
    ss -ltnp 2>/dev/null | awk -v pattern=":$1\$" '$4 ~ pattern' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2 || true
  fi
}

# A stale backend on 8000 would keep serving the dashboard silently, and a
# stale Vite on 5173 would open the wrong app. Refuse to start in either case.
check_port() {
  local port="$1" role="$2" pid
  pid="$(port_owner "$port" || true)"
  if [ -n "$pid" ]; then
    echo ""
    echo "Port $port is already in use, so the $role cannot start cleanly."
    echo "  Held by PID $pid ($(ps -p "$pid" -o comm= 2>/dev/null || echo unknown))"
    echo "  Stop it with:  kill $pid"
    echo "  Or reuse that process intentionally and skip this script."
    echo ""
    echo "Startup cancelled so the dashboard does not attach to an old backend."
    exit 1
  fi
}

check_port 8000 "backend (uvicorn)"
check_port 5173 "dashboard (vite)"

cleanup() {
  kill "${BACKEND_PID:-}" "${FRONTEND_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(cd "$REPO_ROOT" && python -m uvicorn task6_web_scraper.api:app --reload --port 8000) &
BACKEND_PID=$!

(cd "$TASK_ROOT/frontend" && npm run dev) &
FRONTEND_PID=$!

sleep 2

if command -v open >/dev/null 2>&1; then
  open http://localhost:5173
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:5173
fi

echo "Backend: http://localhost:8000"
echo "Dashboard: http://localhost:5173"
wait
