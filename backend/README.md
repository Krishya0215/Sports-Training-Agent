# 运动训练知识问答系统 - 后端

基于LangChain、LangGraph和FastAPI的智能问答后端服务。

## 技术栈

- FastAPI - 现代化Web框架
- LangChain - LLM应用框架
- LangGraph - 状态图工作流
- ChromaDB - 向量数据库
- DashScope - 阿里云模型API

## 项目结构

```
backend/
├── api.py              # FastAPI接口
├── requirements.txt    # Python依赖
└── README.md          # 说明文档

项目根目录/
├── agent/             # Agent模块
├── config/            # 配置文件
├── data/              # 知识库数据
├── memory/            # 记忆管理
├── model/             # 模型工厂
├── prompts/           # 提示词模板
├── rag/               # RAG模块
└── utils/             # 工具模块
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录的 `model/.env` 文件中配置API密钥：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 启动服务

```bash
cd backend
python api.py
```

或使用uvicorn：

```bash
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问服务

- API服务：http://localhost:8000
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

## API接口

### 查询问答

```http
POST /api/query
Content-Type: application/json

{
  "question": "什么是有氧运动？"
}
```

### 加载知识库

```http
POST /api/knowledge/load
```

### 获取记忆摘要

```http
GET /api/memory/summary
```

### 清空工作记忆

```http
POST /api/memory/clear
```

### 获取对话历史

```http
GET /api/chat/history
```

### 健康检查

```http
GET /api/health
```

## 开发模式

启用热重载：

```bash
cd backend
uvicorn api:app --reload
```

## 生产部署

### 使用Gunicorn + Uvicorn

```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 使用Docker

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
docker build -t sports-training-backend .
docker run -p 8000:8000 sports-training-backend
```

## 配置说明

### CORS设置

在 `api.py` 中配置允许的前端地址：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 修改为你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 端口配置

修改 `api.py` 中的端口：

```python
uvicorn.run(
    "api:app",
    host="0.0.0.0",
    port=8000,  # 修改端口
    reload=True
)
```

## 日志

日志文件位于项目根目录的 `logs/` 文件夹：

```
logs/
└── agent_YYYYMMDD.log
```

## 性能优化

1. **使用缓存**：缓存常见问题的答案
2. **异步处理**：利用FastAPI的异步特性
3. **连接池**：配置数据库连接池
4. **负载均衡**：使用多个worker进程

## 监控

### 健康检查

```bash
curl http://localhost:8000/api/health
```

### 查看日志

```bash
tail -f ../logs/agent_*.log
```

## 故障排查

### Agent初始化失败

检查：
1. API密钥是否正确配置
2. 依赖是否完整安装
3. 查看日志文件

### 知识库加载失败

检查：
1. `data/` 目录是否有文档
2. 文档格式是否支持
3. 磁盘空间是否充足

### 查询响应慢

优化：
1. 减少检索文档数量
2. 调整chunk大小
3. 使用更快的模型

## 许可证

MIT License
