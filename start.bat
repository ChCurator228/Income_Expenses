@echo off
cd /d "%~dp0"
python budget_app.py
cd web_flask
python run.py
pause
