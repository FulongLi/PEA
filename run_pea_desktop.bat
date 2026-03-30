@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%
python -m pip show pywebview >nul 2>&1
if errorlevel 1 (
  echo Installing pywebview...
  python -m pip install "pywebview>=5.0" -q
)
python -m pea.desktop
if errorlevel 1 pause
