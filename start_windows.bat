@echo off
cd /d %~dp0
if not exist .venv python -m venv .venv
call .venv\Scriptsctivate
pip -q install -r requirements.txt
start http://127.0.0.1:8765
python run.py
