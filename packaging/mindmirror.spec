# -*- mode: python ; coding: utf-8 -*-
"""心镜平台 PyInstaller 打包配置（单文件可执行程序）。

用法（在仓库根目录）：
    backend/.venv/bin/pyinstaller --clean --noconfirm packaging/mindmirror.spec

产物：dist/mind-mirror（Windows 下为 dist/mind-mirror.exe）
"""
import os

project_root = os.path.abspath(os.path.join(SPECPATH, ".."))
backend = os.path.join(project_root, "backend")

a = Analysis(
    [os.path.join(backend, "launcher.py")],
    pathex=[backend],
    binaries=[],
    datas=[
        (os.path.join(project_root, "frontend-patient"), "frontend-patient"),
        (os.path.join(project_root, "frontend-doctor"), "frontend-doctor"),
    ],
    hiddenimports=[
        # SQLAlchemy SQLite 方言（PyInstaller 静态分析常漏）
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.dialects.sqlite.aiosqlite",
        # Web 与扩展
        "flask", "flask_sqlalchemy", "flask_migrate", "flask_cors", "jwt",
        # PDF 导出中文字体
        "reportlab.pdfbase.cidfonts",
        "reportlab.pdfbase.pdfmetrics",
        # 业务模块（函数内导入，静态分析不可见，需显式声明）
        "app", "app.config", "app.extensions", "app.paths",
        "app.api", "app.api.auth", "app.api.patient", "app.api.doctor",
        "app.api.admin", "app.api.pages",
        "app.services", "app.services.push_engine", "app.services.scoring",
        "app.services.rule_engine", "app.services.report",
        "app.services.condition_engine", "app.services.config_service",
        "app.services.invite_service",
        "app.middleware", "app.middleware.auth",
        "app.utils", "app.utils.response", "app.utils.errors",
        "app.utils.sanitize", "app.utils.validators", "app.utils.code_generator",
        "app.models", "app.models.user", "app.models.invite_code",
        "app.models.assessment", "app.models.scale", "app.models.norm",
        "app.models.rule", "app.models.config_model", "app.models.audit_log",
        # 种子数据
        "seed", "seed_data", "seed_data.scales_core",
        "seed_data.scales_scl90", "seed_data.scales_iesr",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="mind-mirror",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
