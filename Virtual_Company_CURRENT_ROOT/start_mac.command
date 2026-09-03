#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip -q install -r requirements.txt
(sleep 2; open http://127.0.0.1:8765) &
python run.py
