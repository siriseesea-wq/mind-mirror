"""静态页面托管（文档 9.1 部署方案：Nginx 生产环境可直接接管，开发时由 Flask 托管）。

路由约定：
- /           患者端首页（邀请码链接 /patient?code=XXXX 同页）
- /doctor     医生/家长端（/doctor/login 与 /admin/login 为文档 5.1 登录路径别名）
- /admin      管理端（与医生端共用 SPA，按 hash 区分工作区）
"""
import os

from flask import Blueprint, send_from_directory

from ..paths import static_root

PATIENT_DIR = os.path.join(static_root(), "frontend-patient")
DOCTOR_DIR = os.path.join(static_root(), "frontend-doctor")

bp = Blueprint("pages", __name__)


@bp.get("/")
@bp.get("/patient")
def patient_index():
    return send_from_directory(PATIENT_DIR, "index.html")


@bp.get("/patient/static/<path:filename>")
def patient_static(filename):
    return send_from_directory(PATIENT_DIR, filename)


@bp.get("/doctor")
@bp.get("/doctor/login")     # 文档 5.1：登录路径别名（SPA 内部处理登录）
@bp.get("/admin")
@bp.get("/admin/login")      # 文档 5.1：登录路径别名
def doctor_index():
    return send_from_directory(DOCTOR_DIR, "index.html")


@bp.get("/doctor/static/<path:filename>")
def doctor_static(filename):
    return send_from_directory(DOCTOR_DIR, filename)


# SPA 深链接兜底：/doctor/xxx 与 /admin/xxx 均回退到工作台入口（前端 hash 路由接管）
@bp.get("/doctor/<path:rest>")
def doctor_deep(rest):
    return send_from_directory(DOCTOR_DIR, "index.html")


@bp.get("/admin/<path:rest>")
def admin_deep(rest):
    return send_from_directory(DOCTOR_DIR, "index.html")
