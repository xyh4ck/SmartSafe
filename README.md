<p align="center">
  <img src="docs/logo.png" alt="SmartSafe Logo" width="200" />
</p>

<h1 align="center">SmartSafe（智安）</h1>

<h2 align="center">

**大模型安全评测系统**

</h2>

## 📖 项目简介

SmartSafe（智安）是一套面向大语言模型（LLM）的安全评测系统，**助力企业快速完成大模型备案**。系统参考 **tc260-003《生成式人工智能服务安全基本要求》** 等国家标准，提供测试用例库、模型接入、评测任务执行与结果分析等能力，帮助团队将”模型安全”沉淀为可测、可追踪、可对比的指标与流程，**一键生成符合监管要求的安全评测报告**。

### 🎯 核心价值

- **合规备案**：对标国家标准，输出符合监管要求的评测报告，助力大模型快速通过备案
- **全面评测**：覆盖语料安全、生成内容安全、拒答测试等多维度安全评测能力
- **开箱即用**：内置丰富测试用例库，支持自定义扩展，快速构建评测体系

## ✨ 核心功能

### 🔬 评测任务管理

> 模块路径：`module_evaltask`

| 功能 | 说明 |
| --- | --- |
| 任务创建 | 三步向导创建任务，选择模型 + 按全部/维度/分类筛选用例，自动批量组装评测输入 |
| 异步执行 | Celery 异步执行评测，支持并发限流、失败重试与任务幂等保护 |
| 进度追踪 | 提供任务进度、用例明细、阶段日志查询（支持轮询与 ETag 缓存） |
| 结果分析 | 内置规则分析与 deepteam 评估，输出风险分数、风险等级、风险原因与 Token 用量 |
| 汇总报告 | 自动生成任务汇总结果：等级分布、通过率、指标均值与 Top 风险样本 |

### 📚 测试用例库管理

> 模块路径：`module_evaluation`

| 功能 | 说明 |
| --- | --- |
| 关键词题库 | 支持关键词增删改查、同类唯一性校验、风险等级与匹配类型配置、Excel 导入导出 |
| 生成内容题库 | 支持测试用例 CRUD，按维度/分类/状态分页检索，自动校验维度分类一致性与重复 |
| 候选题审核 | 支持候选题自动生成（应拒答/不应拒答）、批量审核、审核后发布至正式题库 |
| 风险分类 | 支持风险维度与分类管理、启用状态控制、维度-分类树查询、模板导入导出 |

### 🤖 模型接入管理

> 模块路径：`module_model`

| 功能 | 说明 |
| --- | --- |
| 模型配置 | 模型注册与配置管理（provider/type/api_base 等） |
| 密钥管理 | API Key 加密存储与解密调用，评测执行阶段按模型配置自动注入 |
| 连通测试 | 在线验证模型可调用性 |
| 状态管理 | 模型可用状态批量开关、版本维护 |

## 🛠️ 技术栈

### 后端技术栈

| 技术 | 版本 | 说明 |
| --- | --- | --- |
| ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python) | 3.10+ | 运行环境 |
| ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-009688?logo=fastapi) | 0.115.2 | Web 框架 |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.36-D71F00?logo=sqlalchemy) | 2.0.36 | ORM 框架 |
| ![Alembic](https://img.shields.io/badge/Alembic-1.15.1-D71F00) | 1.15.1 | 数据库迁移 |
| ![Celery](https://img.shields.io/badge/Celery-5.2.7-37B24D?logo=celery) | 5.2.7 | 异步任务队列 |
| ![Redis](https://img.shields.io/badge/Redis-5.2.1-DC382D?logo=redis) | 5.2.1 | 缓存与消息队列 |
| Pydantic | 2.x | 数据验证与序列化 |
| APScheduler | 3.11.0 | 定时任务调度 |
| Uvicorn | 0.30.6 | ASGI 服务器 |

### 前端技术栈

| 技术 | 版本 | 说明 |
| --- | --- | --- |
| ![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js) | 3.x | 渐进式框架 |
| ![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript) | 5.x | 类型安全 |
| ![Vite](https://img.shields.io/badge/Vite-6.x-646CFF?logo=vite) | 6.x | 构建工具 |
| ![Element Plus](https://img.shields.io/badge/Element_Plus-2.x-409EFF?logo=element) | 2.x | UI 组件库 |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- pnpm 8+
- MySQL 8.0+ / PostgreSQL
- Redis

### 后端启动

```bash
# 1. 进入后端目录
cd backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端服务（默认 dev 环境）
python main.py run --env=dev

# 4. 启动 Celery Worker（评测任务异步执行）
./celery_worker.sh start
```

<details>
<summary>📋 服务配置</summary>

| 配置项 | 值 |
| --- | --- |
| 服务端口 | `8001` |
| API 前缀 | `/api/v1` |
| Swagger 文档 | `http://localhost:8001/api/v1/docs` |
| ReDoc 文档 | `http://localhost:8001/api/v1/redoc` |

</details>

### 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
pnpm install

# 3. 启动开发服务器
pnpm dev
```

> 💡 **提示**：前端使用 Vite 构建，`base` 为 `/web`，开发端口由 `VITE_APP_PORT` 控制，后端代理通过 `VITE_APP_BASE_API` 与 `VITE_API_BASE_URL` 配置。

## ⚙️ 配置说明

### 后端配置

配置文件位于 `backend/env/` 目录，通过 `ENVIRONMENT` 环境变量选择：

| 环境 | 配置文件 |
| --- | --- |
| 开发 | `backend/env/.env.dev` |
| 生产 | `backend/env/.env.prod` |

<details>
<summary>📝 常用配置项</summary>

| 类别 | 配置项 | 说明 |
| --- | --- | --- |
| 数据库 | `DATABASE_HOST` | 数据库地址 |
| | `DATABASE_PORT` | 数据库端口 |
| | `DATABASE_USER` | 数据库用户名 |
| | `DATABASE_PASSWORD` | 数据库密码 |
| | `DATABASE_NAME` | 数据库名称 |
| Redis | `REDIS_HOST` | Redis 地址 |
| | `REDIS_PORT` | Redis 端口 |
| | `REDIS_PASSWORD` | Redis 密码 |
| 大模型 | `OPENAI_BASE_URL` | API 基础地址 |
| | `OPENAI_API_KEY` | API 密钥 |
| | `OPENAI_MODEL` | 模型名称 |

</details>

> ⚠️ **安全提醒**：请勿将真实 `OPENAI_API_KEY` 提交到仓库！建议通过环境变量或私有配置文件注入，并定期轮换密钥。

### 前端配置

前端环境变量配置（详见 `frontend/src/types/env.d.ts`）：

| 变量 | 说明 |
| --- | --- |
| `VITE_APP_PORT` | 开发服务器端口 |
| `VITE_APP_BASE_API` | API 代理路径 |
| `VITE_API_BASE_URL` | 后端服务地址 |

## 🐳 部署说明

### Docker Compose 部署

项目支持 Docker Compose 一键部署，配置文件位于根目录 `docker-compose.yaml`。

```bash
# 仅启动 Redis（默认）
docker compose up -d redis

# 完整部署（需取消注释 mysql/backend/nginx 服务）
docker compose up -d
```

<details>
<summary>📦 服务说明</summary>

| 服务 | 说明 | 默认状态 |
| --- | --- | --- |
| `redis` | 缓存与消息队列 | ✅ 启用 |
| `mysql` | 数据库 | ⚪ 注释 |
| `backend` | 后端服务 | ⚪ 注释 |
| `nginx` | 反向代理 | ⚪ 注释 |

> 💡 如需完整部署，请在 `docker-compose.yaml` 中取消对应服务的注释，并配置环境变量。

</details>

## 📁 目录结构

```
SmartSafe/
├── 📂 backend/                 # 后端服务 (FastAPI)
│   ├── 📂 app/                 # 业务代码
│   │   ├── 📂 api/             # API 路由
│   │   ├── 📂 core/            # 核心模块
│   │   ├── 📂 config/          # 配置文件
│   │   └── 📂 utils/           # 工具函数
│   ├── 📂 env/                 # 环境配置 (.env.dev / .env.prod)
│   ├── 📂 tests/               # 测试用例
│   ├── 📄 alembic.ini          # 数据库迁移配置
│   └── 📄 main.py              # 入口文件
│
├── 📂 frontend/                # 前端服务 (Vue 3 + Vite)
│   ├── 📂 src/                 # 源代码
│   │   ├── 📂 api/             # API 请求
│   │   ├── 📂 views/           # 页面组件
│   │   ├── 📂 components/      # 公共组件
│   │   ├── 📂 router/          # 路由配置
│   │   └── 📂 store/           # 状态管理
│   └── 📄 vite.config.ts       # Vite 配置
│
├── 📂 devops/                  # 部署配置 (nginx/redis 等)
├── 📂 docs/                    # 文档与截图
├── 📄 docker-compose.yaml      # Docker 编排配置
└── 📄 README.md                # 项目说明
```

## 📸 系统截图

### 评测任务管理

| 生成内容评测 | 任务详情 |
| :---: | :---: |
| ![](docs/image1.png) | ![](docs/image2.png) |

| 任务明细 | 结果报告 |
| :---: | :---: |
| ![](docs/image3.png) | ![](docs/image4.png) |

### 测试用例管理

| 关键词题库 | 生成内容题库 |
| :---: | :---: |
| ![](docs/image5.png) | ![](docs/image6.png) |

| 候选题审核 | 风险分类 |
| :---: | :---: |
| ![](docs/image7.png) | ![](docs/image8.png) |

### 模型接入管理

| 模型管理 |
| :---: |
| ![](docs/image9.png) |



## 🗺️ 未来开发计划

### 🔐 大模型漏洞库

构建专属大模型漏洞库，实现漏洞收集、分类、更新、匹配、扫描的全流程管理，联动现有评测用例库，提升评测精准度，支持漏洞自动扫描与风险预警，形成漏洞治理闭环。

### 🔌 Skills 安全扫描

覆盖大模型技能（插件/应用）的全生命周期安全，重点打造 Skills 安全扫描核心能力，实现技能注册审核、运行时监控、恶意行为识别、安全评级的全流程扫描管控，联动评测流程完善安全闭环。

### 📡 MCP 安全扫描

聚焦大模型通信协议（MCP）安全，重点构建 MCP 安全扫描能力，实现协议适配、加密校验、身份认证、数据传输检测、异常行为拦截的全流程扫描防护，保障模型通信全链路安全。

## 👨‍💻 开发者指南

### 📦 后端分层约定

后端业务模块采用统一分层架构：

```
module_xxx/
├── 📄 controller.py   # HTTP 接口层 - 路由与请求处理
├── 📄 service.py      # 业务编排层 - 核心业务逻辑
├── 📄 crud.py         # 数据访问层 - 数据库 CRUD 操作
├── 📄 model.py        # ORM 模型 - 数据库表映射
├── 📄 schema.py       # Pydantic Schema - 响应数据结构
└── 📄 param.py        # 请求参数 - 查询/请求参数定义
```

### 🆕 新增业务模块

| 位置 | 路径 |
| --- | --- |
| 后端 | `backend/app/api/v1/module_{your_module}/{your_feature}/...` |
| 前端页面 | `frontend/src/views/module_{your_module}/...` |
| 前端 API | `frontend/src/api/module_{your_module}/...` |

## 💖 特别鸣谢

感谢以下开源项目的贡献和支持：

**后端技术**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063)](https://pydantic-docs.helpmanual.io/)
[![Celery](https://img.shields.io/badge/Celery-37B24D?logo=celery)](https://docs.celeryproject.org/)
[![APScheduler](https://img.shields.io/badge/APScheduler-3776AB)](https://apscheduler.readthedocs.io/)

**前端技术**

[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?logo=vue.js)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite)](https://vitejs.dev/)
[![Element Plus](https://img.shields.io/badge/Element_Plus-409EFF?logo=element)](https://element-plus.org/)

**特别感谢**

[![FastapiAdmin](https://img.shields.io/badge/FastapiAdmin-009688)](https://github.com/fastapi-admin/fastapi-admin)
