<div style="display: flex; align-items: center; justify-content: center; gap: 16px;">
     <img src="docs/logo.png" alt="SmartSafe Logo" width="180" />
     <div>
          <h1 style="margin: 0;">SmartSafe（智安）</h1>
          <h3 style="margin: 8px 0 0;">大模型安全评测系统</h3>
     </div>
</div>

## 项目简介

SmartSafe（智安）是一套面向大语言模型（LLM）的安全评测系统，提供测试用例库、模型接入、评测任务执行与结果分析等能力，帮助团队将“模型安全”沉淀为可测、可追踪、可对比的指标与流程。参考 tc260-003《生成式人工智能服务安全基本要求》

## 核心功能

### 评测任务管理（`module_evaltask`）

- 三步向导创建任务：选择模型 + 按全部/维度/分类筛选用例，自动批量组装评测输入
- Celery 异步执行评测，支持并发限流、失败重试与任务幂等保护
- 提供任务进度、用例明细、阶段日志查询（支持轮询与 ETag 缓存）
- 内置规则分析与 deepteam 评估，输出风险分数、风险等级、风险原因与 Token 用量
- 自动生成任务汇总结果：等级分布、通过率（合格率）、指标均值与 Top 风险样本

### 测试用例库管理（`module_evaluation`）

- 关键词题库：支持关键词增删改查、同类唯一性校验、风险等级与匹配类型（精确/模糊/正则）配置、关键词匹配测试、命中计数统计、Excel 导入导出
- 生成内容测试题库：支持测试用例 CRUD，按维度/分类/状态分页检索；创建/更新时执行维度分类一致性校验与重复校验（同维度+同分类+同 prompt）
- 候选题审核：支持候选题自动生成（应拒答/不应拒答）、批量审核（通过/驳回）、审核后发布至正式题库，以及覆盖度缺口统计
- 风险分类：支持风险维度与分类管理、启用状态控制、维度-分类树查询，以及分类模板导入导出

### 模型接入管理（`module_model`）

- 模型注册与配置管理（provider/type/api_base 等）
- API Key 加密存储与解密调用（评测执行阶段按模型配置自动注入）
- 连通性测试（在线验证模型可调用性）
- 模型可用状态批量开关、版本维护

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
pnpm dev
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

### 评测任务管理-生成内容评测
![](docs/image1.png)

### 评测任务管理-任务详情
![](docs/image2.png)
![](docs/image3.png)
![](docs/image4.png)

### 测试用例管理-关键词题库
![](docs/image5.png)

### 测试用例管理-生成内容测试题库
![](docs/image6.png)

### 测试用例管理-候选题审核
![](docs/image7.png)

### 测试用例管理-风险分类
![](docs/image6.png)

### 模型接入管理-模型管理
![](docs/image7.png)



## 未来开发计划

1. 大模型相关漏洞库开发：构建专属大模型漏洞库，实现漏洞收集、分类、更新、匹配、扫描的全流程管理，联动现有评测用例库，提升评测精准度，支持漏洞自动扫描与风险预警，形成漏洞治理闭环。
2. Skills 安全扫描能力开发：覆盖大模型技能（插件/应用）的全生命周期安全，重点打造Skills安全扫描核心能力，实现技能注册审核、运行时监控、恶意行为识别、安全评级的全流程扫描管控，联动评测流程完善安全闭环。
3. MCP 安全扫描能力开发：聚焦大模型通信协议（MCP）安全，重点构建MCP安全扫描能力，实现协议适配、加密校验、身份认证、数据传输检测、异常行为拦截的全流程扫描防护，保障模型通信全链路安全。

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
