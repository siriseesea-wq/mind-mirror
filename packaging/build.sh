#!/usr/bin/env bash
# 心镜平台打包脚本（Linux / macOS）
# 产物：dist/mind-mirror（单文件可执行程序）
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-backend/.venv/bin/python}"
if [ ! -x "$PY" ]; then
  PY="$(command -v python3)"
fi

echo "[build] 使用解释器：$PY"
"$PY" -m pip install --quiet pyinstaller
"$PY" -m PyInstaller --clean --noconfirm packaging/mindmirror.spec

echo
echo "[build] 完成：$(pwd)/dist/mind-mirror"
echo "[build] 运行测试：cd dist && ./mind-mirror --port 8000"
