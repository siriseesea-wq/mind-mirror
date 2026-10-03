"""心镜 · 心理健康自测工具平台 独立启动入口。

用途：
- PyInstaller 打包后的单文件可执行程序入口（双击或命令行运行）；
- 开发模式也可直接 `python launcher.py` 运行。

运行行为：
1. 首次运行自动创建数据库并写入种子数据（管理员 admin / Admin@1234，首次登录强制改密）；
2. 自动生成并持久化 JWT 密钥（exe 同级 secret_key.txt），重启后登录态不失效；
3. 启动 Web 服务（默认 http://127.0.0.1:8000）。

命令行参数：
    --host 0.0.0.0   监听地址（默认 127.0.0.1）
    --port 8000      监听端口
    --no-seed        跳过首次自动播种
"""
import argparse
import os
import secrets
import sys

# 先加载纯路径工具（不读取配置），确保密钥环境变量在 config 导入前就位
from app.paths import is_frozen, runtime_root  # noqa: E402


def _ensure_secret_key():
    """SECRET_KEY 必须在 app.config 导入前确定：优先环境变量，其次持久化文件。"""
    if os.environ.get("MIND_MIRROR_SECRET_KEY"):
        return
    key_file = os.path.join(runtime_root(), "secret_key.txt")
    key = None
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                key = f.read().strip()
        except OSError:
            key = None
    if not key:
        key = secrets.token_hex(32)
        try:
            with open(key_file, "w", encoding="utf-8") as f:
                f.write(key)
            try:
                os.chmod(key_file, 0o600)
            except OSError:
                pass
        except OSError:
            pass  # 只读目录时退化为临时密钥（重启后需重新登录）
    os.environ["MIND_MIRROR_SECRET_KEY"] = key


_ensure_secret_key()

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402

import seed  # noqa: E402  引入种子模块（PyInstaller 静态收集 seed_data）


def _ensure_database(app, do_seed=True):
    with app.app_context():
        db.create_all()
        if not do_seed:
            return
        from app.models import User
        if User.query.filter_by(username="admin").first() is None:
            seed.seed_admin()
            seed.seed_configs()
            seed.seed_scales()
            seed.seed_packages()
            seed.seed_push_rules()
            seed.seed_referral_rules()
            seed.seed_norms()
            db.session.commit()


def main():
    parser = argparse.ArgumentParser(description="心镜 · 心理健康自测工具平台")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"),
                        help="监听地址（默认 127.0.0.1；对外服务用 0.0.0.0）")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")),
                        help="监听端口（默认 8000）")
    parser.add_argument("--env", default=os.environ.get("MIND_MIRROR_ENV", "production"),
                        choices=["development", "production", "testing"],
                        help="运行配置（默认 production）")
    parser.add_argument("--no-seed", action="store_true",
                        help="跳过首次运行自动播种")
    args = parser.parse_args()

    app = create_app(args.env)
    _ensure_database(app, do_seed=not args.no_seed)

    data_dir = runtime_root()
    print("=" * 52)
    print("  心镜 · 心理健康自测工具平台")
    print("=" * 52)
    print(f"  患者端    http://{args.host}:{args.port}/")
    print(f"  工作台    http://{args.host}:{args.port}/doctor")
    print(f"  管理端    http://{args.host}:{args.port}/admin")
    print(f"  数据目录  {data_dir}")
    if not args.no_seed:
        print("  管理员    admin / Admin@1234（首次登录强制修改密码）")
    print("=" * 52)
    print("  本平台为非医疗工具，测试结果不代表临床诊断。")
    print("  按 Ctrl+C 停止服务。")

    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
