"""心镜平台 Flask 应用工厂。

约定：
- 所有 API 路径以 /api/v1/ 为前缀，后续版本升级无需破坏旧客户端。
- 统一响应结构 {code, message, data}；业务错误统一 HTTP 200，通过 code 区分。
- 业务逻辑集中在 services 层，API 层只做参数解析与权限校验。
"""
import logging
import os

from flask import Flask, jsonify, request

from .config import config_map
from .extensions import cors, db, migrate


def create_app(config_name="default"):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_map[config_name])

    # 扩展初始化
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 日志：控制台 + 文件（logs/app.log），便于排查线上问题
    from .paths import runtime_root
    log_dir = os.path.join(runtime_root(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(module)s] %(message)s",
    )
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"),
                                       encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(module)s] %(message)s"))
    logging.getLogger().addHandler(file_handler)

    # 注册蓝图
    from .api import register_blueprints

    register_blueprints(app)

    # 统一全局异常兜底：未捕获异常返回统一错误结构
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception("unhandled error: %s", e)
        return jsonify({"code": 9000, "message": "服务器内部错误，请稍后重试", "data": None}), 200

    @app.errorhandler(404)
    def handle_404(e):
        # API 路径返回统一 JSON 错误；浏览器路径返回友好页面
        if request.path.startswith("/api/"):
            return jsonify({"code": 5002, "message": "请求的资源不存在", "data": None}), 200
        app.logger.info("404 for browser path: %s", request.path)
        return ("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
                "<title>页面不存在</title><style>body{font-family:sans-serif;"
                "text-align:center;padding:80px 20px;color:#555}"
                "a{color:#3E6B8E}</style></head><body>"
                "<h1>页面不存在</h1><p>您访问的地址有误或已失效。</p>"
                "<p><a href='/'>返回患者端首页</a> · "
                "<a href='/doctor'>进入工作台</a></p></body></html>"), 404

    # 自动建表（开发便捷；生产使用 flask db upgrade）
    if app.config.get("AUTO_CREATE_TABLES"):
        with app.app_context():
            from . import models  # noqa: F401  确保模型已注册

            db.create_all()

    return app
