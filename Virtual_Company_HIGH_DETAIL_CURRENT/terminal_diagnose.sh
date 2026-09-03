#!/bin/bash
cd "$(dirname "$0")"
echo "=== AI COMPANY OS 診断 ==="
echo "場所: $(pwd)"
echo "Python: $(command -v python3 || echo NOT_FOUND)"
python3 --version 2>&1 || true
echo "--- PORT 8765 ---"
lsof -nP -iTCP:8765 -sTCP:LISTEN || echo "8765は待受していません"
echo "--- HTTP STATUS ---"
curl -i --max-time 3 http://127.0.0.1:8765/api/status 2>&1 || true
echo
echo "--- FILES ---"
for f in run.py requirements.txt web/index.html app/main.py; do [ -f "$f" ] && echo "OK $f" || echo "NG $f"; done
