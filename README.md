<div align="center">
     <h1>SmartSafe（智安）</h1>
     <h3>大模型安全评测系统</h3>
</div>

## 项目简介

SmartSafe（智安）是一套面向大语言模型（LLM）的安全评测系统，提供测试用例库、模型接入、评测任务执行与结果分析等能力，帮助团队将“模型安全”沉淀为可测、可追踪、可对比的指标与流程。参考 tc260-003《生成式人工智能服务安全基本要求》

## 核心功能

### 评测任务（`module_evaltask`）

- 创建评测任务、批量执行
- 任务进度与日志记录
- 风险分析与汇总输出（规则/分析器注册机制）

### 测试用例库管理（`module_evaluation`）

- 维度/分类管理
- 测试用例 CRUD
- 用例版本快照（变更可追溯）
- 批量导入（前端已提供 Excel 导入交互；后端提供对应导入接口）

### 模型接入管理（`module_model`）

- 模型接入配置
- 连通性测试
- 状态管理、版本管理
- 配额字段维护（配额更新接口）

## 技术栈

### 后端技术栈

| 技术        | 版本    | 说明             |
| ----------- | ------- | ---------------- |
| FastAPI     | 0.115.2 | 现代 Web 框架    |
| SQLAlchemy  | 2.0.36  | ORM 框架         |
| Alembic     | 1.15.1  | 数据库迁移工具   |
| Pydantic    | 2.x     | 数据验证与序列化 |
| APScheduler | 3.11.0  | 定时任务调度     |
| Redis       | 5.2.1   | 缓存与会话存储   |
| Uvicorn     | 0.30.6  | ASGI 服务器      |
| Python      | 3.10+   | 运行环境         |
| Celery      | 5.2.7   | 异步任务队列     |

### 前端技术栈

- Vue 3
- TypeScript
- Vite
- Element Plus

## 快速开始（本地开发）

### 1) 后端

后端使用 `typer` 提供命令行入口。

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移（首次运行或模型变更后）
python main.py revision --env=dev
python main.py upgrade --env=dev

# 启动后端（默认 dev）
python main.py run --env=dev

# 启动Celery
./celery_worker.sh start
```

默认配置：

- 服务端口：`8001`
- API 前缀：`/api/v1`
- Swagger：`http://localhost:8001/api/v1/docs`
- Redoc：`http://localhost:8001/api/v1/redoc`

### 2) 前端

前端使用 Vite，`base` 为 `/web`，开发端口由 `VITE_APP_PORT` 控制；后端代理通过 `VITE_APP_BASE_API` 与 `VITE_API_BASE_URL` 配置。

```bash
cd frontend

pnpm install
pnpm run dev
```

## 配置说明

### 后端配置（env）

后端通过 `ENVIRONMENT` 选择配置文件：

- `backend/env/.env.dev`
- `backend/env/.env.prod`

常用配置项：

- 数据库：`DATABASE_HOST`/`DATABASE_PORT`/`DATABASE_USER`/`DATABASE_PASSWORD`/`DATABASE_NAME`
- Redis：`REDIS_HOST`/`REDIS_PORT`/`REDIS_PASSWORD`
- 大模型：`OPENAI_BASE_URL`/`OPENAI_API_KEY`/`OPENAI_MODEL`

重要：

- 请勿将真实 `OPENAI_API_KEY` 提交到仓库。
- 建议在本地/服务器上使用私密方式注入（例如仅在私有环境文件中配置），并定期轮换密钥。

### 前端配置（Vite env）

前端运行依赖以下环境变量（见 `frontend/src/types/env.d.ts` 与 `frontend/vite.config.ts`）：

- `VITE_APP_PORT`
- `VITE_APP_BASE_API`
- `VITE_API_BASE_URL`

## 部署说明（Docker/Compose）

当前仓库根目录 `docker-compose.yaml` 默认仅启用 `redis` 服务，其它服务（mysql/backend/nginx）处于注释状态。

```bash
docker compose up -d redis
```

如果你希望使用 Docker 完整部署（backend/nginx/mysql 一键启动），需要补齐并启用对应 compose 配置。

## 目录结构

```txt
.
├── backend/                      # FastAPI 后端
│   ├── app/                      # 业务代码
│   ├── env/                      # .env.dev / .env.prod
│   ├── alembic.ini
│   └── main.py                   # 入口：run / revision / upgrade
├── frontend/                     # Vue3 前端（Vite）
├── devops/                       # 部署相关配置（nginx/redis 等）
├── docker-compose.yaml
└── README.md
```

## 系统截图

![评测任务管理](docs/image1.png)
![评测任务详情](docs/image2.png)
![测试用例评测风险详情](docs/image3.png)
![测试用例评测风险详情](docs/image4.png)
![测试用例管理](docs/image5.png)
![风险分类管理](docs/image6.png)
![模型管理](docs/image7.png)

## 开发者指南

### 后端分层约定

后端业务模块通常采用统一分层结构：

```txt
module_xxx/
├── controller.py   # HTTP 接口层
├── service.py      # 业务编排层
├── crud.py         # 数据访问层
├── model.py        # ORM 模型
├── schema.py       # Pydantic Schema
└── param.py        # 查询/请求参数
```

### 新增一个业务模块（建议路径）

- 后端：`backend/app/api/v1/module_{your_module}/{your_feature}/...`
- 前端页面：`frontend/src/views/module_{your_module}/...`
- 前端 API：`frontend/src/api/module_{your_module}/...`

### 常用命令

```bash
cd backend

# 迁移
python main.py revision --env=dev
python main.py upgrade --env=dev

# 启动
python main.py run --env=dev
```

## 特别鸣谢

感谢以下开源项目的贡献和支持：

- FastapiAdmin
- FastAPI
- Pydantic
- SQLAlchemy
- APScheduler
- Vue3
- TypeScript
- Vite
- Element Plus
- UniApp
- Wot-Design-UI
