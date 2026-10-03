"""配置管理：开发 / 生产 / 测试 三套配置。

敏感配置（SECRET_KEY、数据库口令等）通过环境变量注入，禁止写入代码仓库。
"""
import os
from datetime import timedelta

from .paths import runtime_root

BASE_DIR = runtime_root()  # 数据库/日志等可写目录（开发：backend/；打包后：exe 同级目录）


class BaseConfig:
    """公共配置项。"""

    # 安全
    SECRET_KEY = os.environ.get(
        "MIND_MIRROR_SECRET_KEY",
        "dev-only-secret-key-change-me-in-production-0123456789")
    JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", "24"))

    # 数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 业务参数（运行时可通过管理端系统配置覆盖）
    REVOKE_HOURS = int(os.environ.get("REVOKE_HOURS", "24"))          # 患者撤回时限（小时）
    TIMEOUT_MINUTES = int(os.environ.get("TIMEOUT_MINUTES", "30"))    # 作答超时提醒（分钟）
    SESSION_RESUME_HOURS = int(os.environ.get("SESSION_RESUME_HOURS", "24"))  # 断点续答有效期
    LOGIN_MAX_FAILURES = 5        # 连续失败锁定阈值
    LOGIN_LOCK_MINUTES = 30       # 锁定分钟数

    # 部署
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8000"))

    # 首次运行自动建表（生产环境建议改为 False，使用迁移脚本）
    AUTO_CREATE_TABLES = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "mind_mirror_dev.db")
    )


class ProductionConfig(BaseConfig):
    DEBUG = False
    AUTO_CREATE_TABLES = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "mind_mirror.db")
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    AUTO_CREATE_TABLES = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
