#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  AXIOM OS — Personal AI Research, Learning & Creation OS   "
echo "============================================================"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$ROOT_DIR/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
