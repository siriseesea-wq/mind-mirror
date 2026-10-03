@echo off
REM Mind Mirror build script (Windows)
REM Output: dist\mind-mirror.exe (single-file executable)
cd /d "%~dp0.."

set PY=backend\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python

echo [build] interpreter: %PY%
"%PY%" -m pip install --quiet pyinstaller
"%PY%" -m PyInstaller --clean --noconfirm packaging\mindmirror.spec

echo.
echo [build] done: %cd%\dist\mind-mirror.exe
echo [build] run test: cd dist ^&^& mind-mirror.exe --port 8000
