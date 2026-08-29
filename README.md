# 电商小二智能客服系统

<p align="center">
  <img src="/notes/images/hero.svg" width="100%" alt="电商小二智能客服系统：用自然语言描述需求，系统判断该交给谁处理，再以工程化方式执行——查订单、查物流、申请退款、咨询政策，都在同一个对话里完成">
</p>

基于大语言模型（LLM）的电商智能客服系统。用户用自然语言描述需求，系统判断这句话该交给谁处理，再用工程化的方式把事情做完——查订单、查物流、申请退款、咨询商品和政策，都能在同一个对话里完成。

> **核心命题**：如何用工程化方式驯服 LLM 的不确定性，保证业务结果稳定可控？

一句话总结设计思想：**大模型负责理解，后端代码负责约束和执行。**

与传统 CRUD 系统不同，本项目以自然语言为输入、以 LLM 现场推断路由、以多轮强状态驱动对话：

| 维度 | 传统 CRUD 系统 | 本项目（AI 驱动） |
| --- | --- | --- |
| 输入 | 结构化参数 | 用户自然语言 |
| 路由 | URL / 方法名决定 | LLM 现场推断 |
| 输出 | 严格 JSON | 自然语言 + 结构化对象 |
| 不确定性 | 几乎没有 | LLM 可能幻觉、漂移、违反 schema |
| 状态 | 通常无状态 | 多轮对话强状态 |

稳定性来自三个关键设计：

- **结构化输出 + 校验白名单 + 澄清兜底**：LLM 只负责规划，规划结果必须通过确定性校验才能执行，不明确时进入澄清。
- **LLM 路由 + YAML 流程编排引擎**：LLM 判断意图，业务步骤由 YAML 配置驱动，代码负责执行。
- **会话状态与任务栈管理**：每个用户一份完整对话状态，支持任务中断与恢复。

<p align="center">
  <img src="/notes/images/showcase.png" width="100%" alt="系统演示界面：左侧为退款申请对话，右侧业务对象面板展示订单卡片，点击发送订单即可把对象补入对话">
</p>

---

## 核心能力

<p align="center">
  <img src="/notes/images/tracks.svg" width="100%" alt="核心能力：任务流程、信息检索、闲聊三条处理轨道">
</p>

系统将用户输入分为三类处理轨道：

| 轨道 | 负责场景 | 典型例子 |
| --- | --- | --- |
| Task（任务流程） | 步骤明确的业务任务 | 查询订单状态、查询物流、申请退款、商品推荐、转人工 |
| Knowledge（信息检索） | 查询型问题 | 商品信息、订单信息、退款/退货/配送政策、平台规则、FAQ |
| Chitchat（闲聊） | 轻量自然对话 | 打招呼、寒暄、兜底 |

### 任务流程

业务流程通过 YAML 配置定义，由 `start`、`collect`、`action`、`response`、`end` 五种 Step 组成，支持槽位收集、槽位校验、条件跳转、Action 调用和模板回复：

```yaml
refund_request:
  name: 退款申请
  description: 帮用户提交简单的退款申请，收集订单号和退款原因。
  steps:
    - id: start
      type: start
      next: ask_order_number

    - id: ask_order_number
      type: collect
      slot_name: order_number
      template:
        text: "请告诉我你的订单号。"
      next: ask_refund_reason

    - id: ask_refund_reason
      type: collect
      slot_name: refund_reason
      template:
        text: "请简单说一下退款原因。"
      next: refund_submitted

    - id: refund_submitted
      type: response
      template:
        text: "好的，订单{{ slots.order_number }}的退款申请已提交，原因是：{{ slots.refund_reason }}。后续会尽快为你处理。"
      next: end

    - id: end
      type: end
      next: []
```

交互示例：

```text
用户：我想申请退款
客服：好的，我们先处理退款申请。
客服：请告诉我你的订单号。
用户：A20240315001
客服：请简单说一下退款原因。
用户：尺码不合适
客服：好的，订单 A20240315001 的退款申请已提交，原因是：尺码不合适。后续会尽快为你处理。
```

### 信息检索

检索链路的核心思路不是让模型自由回答，而是**先找到可信的信息来源，再让模型基于这些信息生成自然回复**。不同知识走不同的 Provider：

| 知识 | 来源 | 检索依据 |
| --- | --- | --- |
| 商品信息、订单信息 | 商品 API、订单 API | 商品 ID / 订单 ID（聚焦对象） |
| 常见政策问题 | FAQ | 当前用户问题 |
| 平台规则与文档知识 | 文档知识库（RAG） | 当前用户问题 |

### 闲聊

当输入不属于明确任务、也不适合知识检索时，系统进入闲聊轨道，结合当前消息和最近对话历史由大模型生成自然回复，作为兜底体验。

---

## 主要特性

- **LLM 意图规划**：`TurnPlanner` 结合对话上下文、任务状态、聚焦对象和系统能力生成处理计划。
- **计划校验 + 澄清兜底**：`TurnPlanValidator` 用确定性规则校验计划，不明确或不可执行时由 `ClarifyResponder` 引导补齐信息。
- **YAML 流程编排**：业务流程配置化，新增业务不改引擎代码。
- **Action 插件机制**：业务代码与流程配置解耦，每个 Action 独立实现、独立注册。
- **任务中断与恢复**：任务可被暂停（paused）后切到其他任务，之后随时恢复。
- **对象消息与聚焦对象**：前端点击订单/商品卡片，后端自动填槽并记录当前聚焦对象。
- **多轮状态整体持久化**：完整 `DialogueState` 以 JSON 存入 MySQL，恢复上下文简单。
- **历史会话管理**：会话自动超时切换，历史接口返回 `session_id`，前端据此展示分割线。

---

## 系统架构

<p align="center">
  <img src="/notes/images/architecture.svg" width="100%" alt="系统架构：前端、客服后端、模拟电商后端、MySQL、LLM API 组件拓扑，以及 API、Service、Engine、Planning、Repository、基础设施六层职责">
</p>

<p align="center">
  <img src="/notes/images/flow.svg" width="100%" alt="一条消息的处理流程：文本消息经规划、校验后按轨道分流，对象消息记录聚焦对象并尝试补槽，最终统一提交 Turn、保存状态并返回回复">
</p>

### 核心状态模型

`DialogueState` 是项目的核心聚合根，每个用户一份，请求时加载、处理完保存：

```text
DialogueState
  ├── shared         全局共享状态
  │     ├── focused_object   当前聚焦对象（订单/商品）
  │     └── sessions         全部历史会话（Session → Turn）
  └── tasks          任务状态
        ├── active           当前活动任务（TaskInstance）
        └── paused           暂停任务栈（可恢复）

TaskInstance: flow_id / step_id / slots / task_id
```

持久化时，完整状态通过 Pydantic `TypeAdapter` 序列化为 JSON，存入 MySQL 的 `dialogue_states` 表（`sender_id` 为主键，`state_json` 保存状态），写入使用 MySQL Upsert。

<details>
<summary><b>技术栈</b></summary>

| 类别 | 技术 | 用途 |
| --- | --- | --- |
| Web 框架 | FastAPI + Uvicorn | 异步接口与服务端 |
| 数据库 | MySQL + SQLAlchemy Async + aiomysql | 对话状态持久化 |
| LLM | LangChain + langchain-openai | 意图规划、话术改写、知识回复 |
| 配置/校验 | Pydantic、pydantic-settings、Pydantic TypeAdapter | 配置管理、状态序列化 |
| 流程编排 | PyYAML + 自研 FlowExecutor | 业务流程配置与执行 |
| 模板渲染 | Jinja2 | 槽位与上下文渲染客服话术 |
| HTTP 调用 | httpx | 调用电商订单/物流/商品接口 |
| 前端 | Vue（customer-service-frontend） | 聊天页面、订单/商品卡片 |
| 部署 | Docker（Ubuntu 24.04） | 后端/前端容器化部署 |

</details>

---

## 快速开始

<p align="center">
  <img src="/notes/images/quickstart.svg" width="100%" alt="快速开始：五步启动——数据库、.env 配置、电商后端、客服后端、前端页面">
</p>

建议按以下顺序启动环境。

### 1. 启动数据库

使用 Docker 安装并启动 MySQL，或使用本地 MySQL 服务，然后创建数据库：

```sql
CREATE DATABASE customer_service CHARACTER SET utf8mb4;
```

### 2. 配置客服后端

在 `customer-service-backend` 根目录创建 `.env`：

```env
LLM_MODEL=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-xxxxxxxxxx

COMMERCE_API_BASE_URL=http://127.0.0.1:18081

DATABASE_URL=mysql+aiomysql://root:123456@127.0.0.1:3306/customer_service?charset=utf8mb4

APP_HOST=0.0.0.0
APP_PORT=18082
```

### 3. 启动模拟电商后端

```bash
cd ecommerce-service-backend
uv sync
uv run python main.py
```

### 4. 启动客服后端

```bash
cd customer-service-backend
uv sync
uv run python -m app.main
```

### 5. 启动客服前端

```bash
cd customer-service-frontend
npm install
npm run dev
```

访问 [http://127.0.0.1:5173](http://127.0.0.1:5173) 即可看到页面（部分配置使用 5174，以实际 vite 配置为准）。

服务地址速查：

| 服务 | 地址 |
| --- | --- |
| 客服前端 | http://127.0.0.1:5173（或 5174） |
| 客服后端 | http://127.0.0.1:18082 |
| 电商业务后端 | http://127.0.0.1:18081 |

---

## API 接口

<p align="center">
  <img src="/notes/images/section-api.svg" width="100%" alt="API 接口：POST /api/chat 与 GET /api/chat/history">
</p>

### POST `/api/chat`

发送一条用户消息，返回机器人本轮回复。请求支持文本消息和对象消息（`text` 和 `object` 必须且只能传一个）。

文本消息：

```json
{
  "sender_id": "user_001",
  "text": "帮我查一下订单状态",
  "object": null,
  "message_id": "msg_001"
}
```

对象消息（前端点击订单卡片）：

```json
{
  "sender_id": "user_001",
  "text": null,
  "object": {
    "type": "order",
    "id": "ORDER_10001",
    "title": "订单 ORDER_10001",
    "attributes": { "source": "order_list" }
  },
  "message_id": "msg_002"
}
```

响应：

```json
{
  "sender_id": "user_001",
  "message_id": "msg_001",
  "messages": [
    { "text": "好的，我们先处理订单状态查询。", "object": null },
    { "text": "请告诉我你的订单号。", "object": null }
  ]
}
```

约束：`sender_id` 必填；`text` 不能为空字符串或纯空白；传 `object` 时 `object.type`、`object.id` 必填。

### GET `/api/chat/history`

获取指定用户的聊天历史。

```http
GET /api/chat/history?sender_id=user_001
```

```json
{
  "sender_id": "user_001",
  "messages": [
    { "role": "user", "text": "帮我查一下订单状态", "object": null },
    { "role": "bot", "text": "好的，我们先处理订单状态查询。", "object": null }
  ]
}
```

---

## 扩展指南

<p align="center">
  <img src="/notes/images/section-extension.svg" width="100%" alt="扩展指南：新增业务流程、自定义 Action、知识意图">
</p>

### 新增业务流程

1. 在 `flows/` 下编写 YAML，定义 `slots` 和 `flows`（步骤类型：`start` / `collect` / `action` / `response` / `end`）。
2. `collect` 支持 `validation.condition` 槽位校验；`next` 支持静态跳转和 `if / then / else` 条件跳转。
3. 回复模板支持三种模式：`static`（直接渲染）、`rephrase`（大模型改写）、`generate`（大模型生成）。
4. 业务变更时，主要修改 YAML 和 Action，引擎代码通常不用改。

### 新增自定义 Action

一个模块只定义一个 Action，独立调用业务接口，通过 `ActionResult.slot_updates` 返回写回任务的数据：

| Action | 所属流程 | 输入 Slot | 输出 Slot |
| --- | --- | --- | --- |
| `action_lookup_order_status` | 订单状态查询 | `order_number` | `order_status`、`order_summary` |
| `action_lookup_logistics` | 物流查询 | `order_number` | `tracking_number`、`logistics_company`、`logistics_status` |
| `action_recommend_similar_products` | 商品推荐 | `product_id` | `recommendation_summary` |

### 新增知识意图 / Provider

1. 定义 `KnowledgeIntent`，绑定 `provider_ids`。
2. 实现 `KnowledgeProvider.retrieve(state, user_message) -> list[KnowledgeChunk]`，并在 Registry 中注册。
3. 商品/订单类走业务 API（依赖聚焦对象），政策类走 FAQ / RAG。

---

## 项目结构

<p align="center">
  <img src="/notes/images/section-structure.svg" width="100%" alt="项目结构：客服后端、模拟电商后端、客服前端">
</p>

<details>
<summary><b>目录树（按开发笔记逐步实现）</b></summary>

```text
customer-service-backend/        客服后端（FastAPI，端口 18082）
├── app/
│   ├── api/                     接口层：/api/chat、/api/chat/history、依赖注入
│   ├── service/                 DialogueService：加载状态 -> 调用引擎 -> 保存状态
│   ├── engine/                  DialogueEngine：会话准备、消息分流、Turn 提交；builder 组装
│   ├── plan/                    TurnPlanner（LLM 规划）、TurnPlanValidator（计划校验）
│   ├── task/                    TaskHandler、Flow 模型/加载器、CommandProcessor、
│   │                            FlowExecutor、Action 注册与执行
│   ├── knowledge/               KnowledgeHandler、KnowledgeIntent、
│   │                            KnowledgeProvider（API/FAQ/RAG）、KnowledgeResponder
│   ├── chitchat/                ChitchatHandler、ChitchatResponder
│   ├── repository/              DialogueStateRepository（MySQL 读写）
│   ├── domain/                  领域模型：消息、状态、任务
│   ├── models/                  SQLAlchemy ORM
│   ├── clients/                 LLM / Database / HTTP 客户端
│   ├── prompts/                 提示词加载与历史构建
│   └── conf/                    配置（pydantic-settings）
├── flows/                       业务流程 YAML
└── pyproject.toml

ecommerce-service-backend/      模拟电商业务后端（端口 18081）
customer-service-frontend/      客服前端页面（Vue，npm run dev）
```

</details>

---

## 部署

项目支持 Docker 部署（Ubuntu Server 24.04 已实测）：

- 客服后端与电商后端：编写 `Dockerfile`（后端使用 uv 虚拟环境），`docker build` + `docker run`。
- 前端：编写 `Dockerfile`（Node 构建 + Nginx 托管），修改 `vite.config.js` 使 API 代理指向服务器地址。
- 数据库：MySQL 容器，初始化脚本在资料目录中。

详细步骤见开发文档《附录-项目部署》。

---

## 开发文档

<p align="center">
  <img src="/notes/images/section-docs.svg" width="100%" alt="开发文档：01–13 章开发笔记与三份附录">
</p>

本仓库的 `电商客服系统/` 目录下包含完整开发笔记，按实现顺序记录了每一步的设计与代码：

| 文档 | 内容 |
| --- | --- |
| 01_项目概述 | 项目背景、功能概览、整体架构 |
| 02_项目开发准备工作 | 工程创建、依赖、基础设施、接口框架 |
| 03_DialogueService实现 | Service 层与领域模型 |
| 04_DialogueState设计与定义 | 对话状态、会话/轮次、任务状态 |
| 05_DialogueStateRepository实现 | MySQL 状态持久化 |
| 06_DialogueEngine设计 | 引擎调度设计 |
| 07_TaskHandler实现 | Flow 定义/加载、Command、FlowExecutor |
| 08_KnowledgeHandler实现 | 知识检索链路 |
| 09_ChitchatHandler实现 | 闲聊处理 |
| 10_Planning模块实现 | TurnPlanner 与 TurnPlanValidator |
| 11_ClarifyResponder实现 | 澄清兜底 |
| 12_DialogueEngine实现 | 引擎入口、会话管理、消息处理 |
| 13_FastAPI接口与应用生命周期 | 接口实现与依赖注入 |
| 附录-自定义Action实现 | 三个内置 Action 的实现 |
| 附录-项目部署 | Ubuntu + Docker 部署 |
| 附录-面试指南 | 架构讲解与面试高频问题 |
