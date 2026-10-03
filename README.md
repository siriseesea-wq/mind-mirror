# 心镜 · 心理健康自测工具平台

> 免登录、免注册的心理健康自测工具。患者通过邀请码完成测评，数据定向推送给医生或家长，
> 由专业人士在线下解读。平台不做诊断，只承担「数据采集—数据传递—数据呈现」。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](backend/requirements.txt)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey)](backend/app)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

核心设计理念：**简约可拓展 · 以患者为中心 · 医生/家长看详细**（详见 `docs/`）。

> ⚠️ **重要声明**：本平台为**非医疗工具**，测试结果不代表临床诊断，不能替代专业医生面诊。
> 仓库内量表条目文本的权利归属见 [NOTICE.md](NOTICE.md)，本项目的 MIT 许可证**不转移
> 任何量表版权**；商用或对外分发量表内容前请完成版权合规流程。

## 目录结构

```
mind-mirror/
├── backend/             # Flask 后端（Python 3.10+）
│   ├── app/             #   models / services / api / middleware / utils
│   ├── seed_data/       #   量表条目数据（PHQ-4/GAD-7/PHQ-9/HADS/SDS/SAS/PSS/ESS/PSQI/SCL-90/IES-R）
│   ├── seed.py          #   种子数据脚本（幂等）
│   ├── scripts/         #   冒烟测试脚本
│   ├── tests/           #   pytest 单元/集成测试
│   └── run.py           #   开发启动入口
├── frontend-patient/    # 患者端（原生 HTML/CSS/JS，移动端优先）
├── frontend-doctor/     # 医生/家长/管理端（原生 JS SPA，工作台风格）
├── docs/                # 技术需求规格说明书（章节子文件 + 单一主文档）
├── deploy/              # nginx / gunicorn / systemd / 备份脚本
└── README.md
```

## 快速开始（开发环境）

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py                 # 初始化数据库 + 种子数据
.venv/bin/python run.py                  # http://127.0.0.1:8000
```

访问地址：

| 端 | 地址 | 说明 |
|---|---|---|
| 患者端 | `http://127.0.0.1:8000/` | 邀请码入口（也可用 `/patient?code=XXXX`） |
| 医生端 | `http://127.0.0.1:8000/doctor` | 医生/家长工作台 |
| 管理端 | `http://127.0.0.1:8000/admin` | 管理员工作台（同一 SPA） |

默认账号（首次登录强制修改密码）：

| 账号 | 初始密码 | 角色 |
|---|---|---|
| `admin` | `Admin@1234` | 超级管理员 |

医生账号需由管理员在「账号管理」中创建（初始密码自定义，首次登录强制修改）。

## 测试

```bash
cd backend
.venv/bin/python -m pytest tests/ -q                 # 单元+集成测试（20 用例）
.venv/bin/python scripts/smoke_flow.py               # 端到端冒烟（25 项）
.venv/bin/python scripts/smoke_patient_ui.py         # 患者端契约（13 项）
```

> 冒烟脚本需要以全新种子库运行（`rm -f mind_mirror_dev.db && python seed.py`）。
> 脚本会在结束时**自动把管理员密码还原为初始值**；若因异常中断导致密码被改，
> 执行 `python scripts/reset_admin.py` 一键恢复（开发库），
> 或 `python scripts/reset_admin.py --env production`（生产库）。

## 已实现功能（对照需求文档）

- **患者端**：邀请码验证 → 知情同意（强制前置）→ PHQ-4 快筛 + 睡眠/压力补充题 →
  推送决策引擎（7 分支）→ 深度包逐题作答（单题呈现、300ms 自动推进、量表确认页、断点续答）→
  患者结果页（零分数泄露）→ 24 小时撤回（物理删除 + 「确认撤回」二次确认）；
  **匿名自测**（无需邀请码，同样经知情同意，结果不发送给任何人，可断点续答与撤回）。
- **医生端**：JWT 登录（5 次失败锁定 30 分钟、首登强制改密）、邀请码生成/状态机/作废、
  报告列表与详情（逐题作答、维度分、常模对比、分科标签双轨文案、分步展示）、PDF/Excel 导出。
- **管理端**：量表库 CRUD + 条目管理（选项/反向计分/维度）、常模管理、分科规则（条件 JSON + 测试）、
  推送规则、医生账号（创建/重置/停用）、系统配置热更新、操作日志、禁用词硬校验。
- **合规**：四层兜底（知情同意前置、作答确认、硬编码免责声明、禁用词过滤），
  不采集任何个人身份信息，IP/UA 仅存哈希。

## 部署（生产）

笔记本 + DDNS + Nginx + Gunicorn（文档 9.1），详见 `deploy/`：

```bash
sudo cp deploy/mind-mirror.service /etc/systemd/system/
sudo systemctl enable --now mind-mirror
# 配置 nginx.conf 中的域名与证书后
sudo cp deploy/nginx.conf /etc/nginx/sites-available/mind-mirror
sudo ln -s /etc/nginx/sites-available/mind-mirror /etc/nginx/sites-enabled/
sudo certbot --nginx -d YOUR_DOMAIN
```

数据库迁移：开发环境自动建表；生产环境使用 `flask db init/migrate/upgrade`（Flask-Migrate 已配置）。

## 打包为可执行文件（便携部署）

无需安装 Python 环境即可运行整个平台（单文件，内置 Flask + 两套前端 + 种子数据）：

```bash
bash packaging/build.sh        # Linux / macOS → dist/mind-mirror
# Windows 上执行 packaging\build.bat → dist\mind-mirror.exe
```

运行（任意目录，双击或命令行均可）：

```bash
./mind-mirror                  # 默认 http://127.0.0.1:8000
./mind-mirror --host 0.0.0.0 --port 8080   # 对外提供服务
```

首次运行自动完成：创建数据库（`mind_mirror.db`，与程序同级）、写入种子数据、
生成登录密钥（`secret_key.txt`）。管理员账号 `admin / Admin@1234`（首登强制改密）。
停止服务：Ctrl+C。重置数据：删除程序同级的 `mind_mirror.db` 后重新运行。

> 注：产物按平台区分——Linux 上构建的是 Linux 可执行文件，Windows `.exe` 需在
> Windows 上运行 `build.bat`（PyInstaller 不支持跨平台交叉编译）。

## 文档

- 完整需求文档（单一文件）：`docs/心镜-技术需求规格说明书-v1.0.md`
- 按章拆分的子文件：`docs/01-项目概述.md` … `docs/15-附录.md`

## 免责声明

本平台为非医疗工具，测试结果不代表临床诊断。平台所用量表部分来源于
《心理量表自评手册》（198X年版）及其他公开学术资源，仅供学习参考使用；正式商用前需完成版权合规流程（文档第十一章）。

## 开源协议与版权

- 代码与文档：**MIT License**（见 [LICENSE](LICENSE)）；
- 量表条目文本：权利归属见 [NOTICE.md](NOTICE.md)，不随 MIT 授权转移；
- 参与贡献请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)；
- 安全漏洞报告见 [SECURITY.md](SECURITY.md)；
- 社区行为准则见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。
