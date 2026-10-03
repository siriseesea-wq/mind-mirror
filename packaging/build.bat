@echo off
REM 心镜平台打包脚本（Windows）
REM 产物：dist\mind-mirror.exe（单文件可执行程序）
cd /d "%~dp0.."

set PY=backend\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python

echo [build] 使用解释器：%PY%
"%PY%" -m pip install --quiet pyinstaller
"%PY%" -m PyInstaller --clean --noconfirm packaging\mindmirror.spec

echo.
echo [build] 完成：%cd%\dist\mind-mirror.exe
echo [build] 运行测试：cd dist && mind-mirror.exe --port 8000
