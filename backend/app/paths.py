"""路径解析工具：兼容开发模式与 PyInstaller 冻结（打包）模式。

- static_root()：前端静态资源（frontend-patient / frontend-doctor）所在根目录
  · 开发模式：项目根目录（mind-mirror/）
  · 冻结模式：PyInstaller 解包目录 sys._MEIPASS
- runtime_root()：可写运行时目录（数据库、日志、密钥文件）
  · 开发模式：backend/ 目录
  · 冻结模式：可执行文件所在目录（便于随身携带、数据与程序同级）
"""
import os
import sys


def is_frozen():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def static_root():
    if is_frozen():
        return sys._MEIPASS
    # app/paths.py → app/ → backend/ → mind-mirror/
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def runtime_root():
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    # app/paths.py → app/ → backend/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
