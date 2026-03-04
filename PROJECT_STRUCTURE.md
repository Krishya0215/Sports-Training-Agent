# 项目结构说明

## 目录结构

```
sports-training-system/
├── backend/                    # 后端服务
│   ├── api.py                 # FastAPI接口
│   ├── requirements.txt       # Python依赖
│   └── README.md             # 后端文档
│
├── frontend/                   # 前端应用
│   ├── src/                   # 源代码
│   │   ├── api/              # API接口
│   │   ├── assets/           # 静态资源
│   │   ├── components/       # 公共组件
│   │   ├── views/            # 页面视图
│   │   ├── router/           # 路由配置
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 入口文件
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── README.md             # 前端文档
│
├── agent/                      # Agent模块
│   ├── graph_agent.py         # LangGraph Agent
│   └── tools/                 # Agent工具
│
├── config/                     # 配置文件
│   ├── agent.yml              # Agent配置
│   ├── chroma.yml             # 向量数据库配置
│   ├── prompts.yml            # 提示词配置
│   └── rag.yml                # RAG配置
│
├── data/                       # 知识库数据
│   ├── sample_sports_training.md
│   └── 运动训练基础理论.pdf
│
├── memory/                     # 记忆管理
│   └── memory_manager.py      # 多层次记忆管理器
│
├── model/                      # 模型工厂
│   ├── .env                   # 环境变量（API密钥）
│   └── factory.py             # 模型工厂
│
├── prompts/                    # 提示词模板
│   ├── answer_generation_prompt.txt
│   ├── hyde_prompt.txt
│   ├── memory_summary_prompt.txt
│   ├── multi_query_prompt.txt
│   └── rag_qa_prompt.txt
│
├── rag/                        # RAG模块
│   ├── advanced_retriever.py  # 高级检索器
│   ├── document_processor.py  # 文档处理器
│   ├── rag_service.py         # RAG服务
│   ├── vector_store.py        # 向量存储
│   └── chroma_db/             # ChromaDB数据
│
├── utils/                      # 工具模块
│   ├── config_handler.py      # 配置处理
│   ├── file_handler.py        # 文件处理
│   ├── logger_handler.py      # 日志处理
│   ├── path_tool.py           # 路径工具
│   └── prompt_loader.py       # 提示词加载器
│
├── logs/                       # 日志文件
│   └── agent_YYYYMMDD.log
│
├── package.json                # 项目配置
├── README.md                   # 项目文档
├── QUICKSTART.md              # 快速开始
└── PROJECT_STRUCTURE.md       # 本文件
```

## 模块说明

### Backend（后端）

FastAPI后端服务，提供RESTful API接口。

**核心文件：**
- `api.py`：API路由和业务逻辑
- `requirements.txt`：Python依赖包

**功能：**
- 问答查询接口
- 知识库管理
- 记忆系统管理
- 对话历史记录

### Frontend（前端）

Vue 3前端应用，提供用户界面。

**核心目录：**
- `src/views/`：页面组件（Home、Chat、Knowledge、Memory）
- `src/components/`：公共组件（Navbar）
- `src/api/`：API接口封装
- `src/router/`：路由配置

**功能：**
- 智能问答界面
- 知识库管理界面
- 记忆系统可视化
- 对话历史展示

### Agent（智能体）

基于LangGraph的智能Agent实现。

**核心文件：**
- `graph_agent.py`：Agent主逻辑
- `tools/agent_tools.py`：Agent工具集

**功能：**
- 状态管理
- 工作流编排
- 工具调用

### RAG（检索增强生成）

RAG核心功能实现。

**核心文件：**
- `advanced_retriever.py`：高级检索（MQE + HyDE）
- `document_processor.py`：文档处理和分块
- `vector_store.py`：向量存储管理
- `rag_service.py`：RAG服务封装

**功能：**
- 多查询扩展（MQE）
- 假设文档嵌入（HyDE）
- 文档向量化
- 相似度检索

### Memory（记忆系统）

多层次记忆管理。

**核心文件：**
- `memory_manager.py`：记忆管理器

**功能：**
- 工作记忆：当前对话上下文
- 情景记忆：问答历史
- 语义记忆：概念知识
- 感知记忆：文档特征

### Config（配置）

系统配置文件。

**配置文件：**
- `agent.yml`：Agent行为配置
- `chroma.yml`：向量数据库配置
- `prompts.yml`：提示词路径配置
- `rag.yml`：RAG模型配置

### Model（模型）

模型工厂和配置。

**核心文件：**
- `factory.py`：模型工厂类
- `.env`：API密钥配置

**功能：**
- 统一模型接口
- 模型切换
- API密钥管理

### Utils（工具）

通用工具函数。

**核心文件：**
- `config_handler.py`：配置文件读取
- `file_handler.py`：文件操作
- `logger_handler.py`：日志管理
- `path_tool.py`：路径处理
- `prompt_loader.py`：提示词加载

## 数据流

```
用户输入
    ↓
前端 (Vue)
    ↓
API接口 (FastAPI)
    ↓
Agent (LangGraph)
    ↓
记忆管理 + RAG检索
    ↓
LLM生成答案
    ↓
返回前端展示
```

## 技术栈

### 后端
- Python 3.8+
- FastAPI
- LangChain
- LangGraph
- ChromaDB
- DashScope

### 前端
- Vue 3
- Vue Router
- Axios
- Vite

## 开发流程

1. **后端开发**：在 `backend/` 目录开发API
2. **前端开发**：在 `frontend/` 目录开发界面
3. **Agent开发**：在 `agent/` 目录开发智能体
4. **RAG开发**：在 `rag/` 目录开发检索逻辑
5. **配置调整**：在 `config/` 目录调整参数

## 部署结构

### 开发环境
- 前端：http://localhost:3000
- 后端：http://localhost:8000

### 生产环境
- 前端：Nginx静态托管
- 后端：Gunicorn + Uvicorn
- 数据库：ChromaDB持久化

## 扩展指南

### 添加新API接口
1. 在 `backend/api.py` 添加路由
2. 在 `frontend/src/api/index.js` 添加接口调用

### 添加新页面
1. 在 `frontend/src/views/` 创建组件
2. 在 `frontend/src/router/index.js` 添加路由

### 添加新Agent工具
1. 在 `agent/tools/` 创建工具函数
2. 在 `agent/graph_agent.py` 注册工具

### 添加新配置
1. 在 `config/` 创建YAML文件
2. 在 `utils/config_handler.py` 添加读取逻辑
