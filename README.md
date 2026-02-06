# 运动训练知识问答Agent

基于LangChain和LangGraph实现的智能运动训练知识问答系统，具有多模态RAG功能和多层次记忆管理。

## 核心特性

### 1. 智能文档处理
- **MarkItDown集成**: 将多模态PDF（文本+图像）统一转换为Markdown格式
- **结构化分块**: 基于Markdown标题层级的智能分块策略
- **高效索引**: 优化的向量化和索引构建流程

### 2. 高级检索问答
- **多查询扩展(MQE)**: 生成多个查询变体，提升召回率
- **假设文档嵌入(HyDE)**: 生成假设答案改善检索精度
- **上下文感知**: 结合对话历史的智能问答

### 3. 多层次记忆管理
- **工作记忆**: 管理当前任务和对话上下文（最近N轮）
- **情景记忆**: 记录学习事件和查询历史
- **语义记忆**: 存储概念知识和理解
- **感知记忆**: 处理文档特征和多模态信息

### 4. LangGraph工作流
- 状态管理和节点编排
- 可扩展的图结构设计
- 灵活的流程控制

## 项目结构

```
.
├── agent/                      # Agent模块
│   └── graph_agent.py         # LangGraph Agent实现
├── config/                     # 配置文件
│   ├── agent.yml              # Agent配置
│   ├── chroma.yml             # 向量数据库配置
│   ├── prompts.yml            # 提示词路径配置
│   └── rag.yml                # RAG模型配置
├── data/                       # 知识库数据（PDF/MD/TXT）
├── memory/                     # 记忆管理模块
│   └── memory_manager.py      # 多层次记忆管理器
├── model/                      # 模型工厂
│   ├── .env                   # 环境变量（API密钥）
│   └── factory.py             # 模型工厂
├── prompts/                    # 提示词模板
│   ├── answer_generation_prompt.txt
│   ├── hyde_prompt.txt
│   ├── memory_summary_prompt.txt
│   ├── multi_query_prompt.txt
│   └── rag_qa_prompt.txt
├── rag/                        # RAG模块
│   ├── advanced_retriever.py  # 高级检索器（MQE+HyDE）
│   ├── document_processor.py  # 智能文档处理器
│   └── vector_store.py        # 向量存储服务
├── utils/                      # 工具模块
│   ├── config_handler.py      # 配置处理
│   ├── file_handler.py        # 文件处理
│   ├── logger_handler.py      # 日志处理
│   ├── path_tool.py           # 路径工具
│   └── prompt_loader.py       # 提示词加载器
├── main.py                     # 主程序入口
└── requirements.txt            # 依赖包
```

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `model/.env` 文件中配置API密钥：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 准备知识库

将运动训练相关的PDF、Markdown或文本文件放入 `data/` 目录。

## 使用方法

### 启动主程序

```bash
python main.py
```

### 功能菜单

1. **加载知识库**: 首次使用或更新知识库时执行
2. **开始问答**: 进入交互式问答模式
3. **查看记忆摘要**: 查看各层记忆的状态
4. **清空工作记忆**: 清除当前对话上下文
5. **退出**: 退出程序

### 编程接口

```python
from agent.graph_agent import SportsTrainingAgent

# 初始化Agent
agent = SportsTrainingAgent()

# 加载知识库（首次运行）
agent.load_knowledge_base()

# 查询
answer = agent.query("什么是有氧运动？")
print(answer)

# 查看记忆摘要
summary = agent.get_memory_summary()
print(summary)
```

## 配置说明

### Agent配置 (config/agent.yml)

```yaml
# 记忆配置
memory:
  working_memory_size: 5          # 工作记忆保留轮数
  episodic_memory_enabled: true   # 启用情景记忆
  semantic_memory_enabled: true   # 启用语义记忆
  perceptual_memory_enabled: true # 启用感知记忆

# 检索增强配置
retrieval:
  use_multi_query: true           # 启用多查询扩展
  use_hyde: true                  # 启用HyDE
  num_queries: 3                  # MQE生成查询数量
  rerank_enabled: true            # 启用重排序
```

### 文档处理配置 (config/chroma.yml)

```yaml
# 文档处理配置
document_processing:
  use_markitdown: true            # 使用MarkItDown处理PDF
  extract_images: true            # 提取图像
  image_description_enabled: true # 为图像生成描述

# 文本分割配置
chunk_size: 800
chunk_overlap: 100
separators: ["\n## ", "\n### ", "\n#### ", "\n\n", "\n", "。"]
```

## 技术架构

### 检索流程

```
用户问题
    ↓
多查询扩展(MQE) → 生成3个查询变体
    ↓
假设文档嵌入(HyDE) → 生成假设答案
    ↓
向量检索 → 检索相关文档
    ↓
去重 + 重排序
    ↓
上下文构建
    ↓
答案生成
```

### 记忆层次

```
工作记忆 (Working Memory)
    ↓ 短期保留
情景记忆 (Episodic Memory)
    ↓ 事件记录
语义记忆 (Semantic Memory)
    ↓ 概念存储
感知记忆 (Perceptual Memory)
    ↓ 多模态特征
```

## 依赖项

- **LangChain**: 0.3.0 - LLM应用框架
- **LangGraph**: 0.2.0 - 状态图工作流
- **ChromaDB**: 0.5.0 - 向量数据库
- **MarkItDown**: 0.0.1a2 - 文档转换
- **DashScope**: 1.19.0 - 阿里云模型API

## 扩展建议

1. **图像理解**: 集成多模态模型处理PDF中的图像
2. **知识图谱**: 构建运动训练概念的知识图谱
3. **个性化推荐**: 基于用户历史提供个性化训练建议
4. **实时更新**: 支持知识库的增量更新
5. **评估指标**: 添加检索和生成质量的评估

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
