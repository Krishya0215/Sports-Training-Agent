# 运动训练知识问答Agent

基于LangChain和LangGraph实现的智能运动训练知识问答系统，具有多模态RAG功能、多层次记忆管理和多智能体协同训练支持。

## 核心特性

### 1. 多智能体协同训练支持系统 ⭐ NEW
- **5个专业虚拟教练**: 模拟真实运动指导团队
  - 📋 训练规划教练：制定科学训练计划并动态优化
  - 🎯 技术指导教练：提供动作指导和姿势分析
  - 💪 体能评估教练：分析身体状态与疲劳程度
  - 🏥 运动康复教练：提供损伤预防与恢复建议
  - ⚠️ 安全督导教练：识别风险因素并提供安全提示
- **智能协作流程**: 基于LangGraph的状态图协作
- **意图识别路由**: 自动选择合适的教练团队
- **完整训练闭环**: 从计划制定到安全评估的全流程支持

### 2. 智能文档处理
- **MarkItDown集成**: 将多模态PDF（文本+图像）统一转换为Markdown格式
- **结构化分块**: 基于Markdown标题层级的智能分块策略
- **高效索引**: 优化的向量化和索引构建流程

### 3. 高级检索问答
- **多查询扩展(MQE)**: 生成多个查询变体，提升召回率
- **假设文档嵌入(HyDE)**: 生成假设答案改善检索精度
- **上下文感知**: 结合对话历史的智能问答

### 4. 多层次记忆管理
- **工作记忆**: 管理当前任务和对话上下文（最近N轮）
- **情景记忆**: 记录学习事件和查询历史
- **语义记忆**: 存储概念知识和理解
- **感知记忆**: 处理文档特征和多模态信息 ⭐ NEW

### 5. 多模态处理能力 ⭐ NEW
- **图像提取**: 从PDF中自动提取图像
- **图像理解**: 使用通义千问VL生成专业图像描述
- **统一检索**: 文本和图像描述在同一向量空间检索
- **感知记忆**: 存储和管理图像描述及元数据

### 6. LangGraph工作流
- 状态管理和节点编排
- 可扩展的图结构设计
- 灵活的流程控制
- 多智能体协作支持

## 项目结构

```
.
├── backend/                    # 后端服务
│   ├── api.py                 # FastAPI接口
│   ├── requirements.txt       # Python依赖
│   └── README.md             # 后端文档
├── frontend/                   # 前端应用
│   ├── src/                   # 源代码
│   │   ├── api/              # API接口
│   │   ├── components/       # 公共组件
│   │   ├── views/            # 页面视图
│   │   └── router/           # 路由配置
│   ├── package.json
│   └── README.md             # 前端文档
├── agent/                      # Agent模块
│   ├── graph_agent.py         # 单智能体问答系统
│   ├── multi_agent_system.py # 多智能体协同系统
│   └── tools/                 # Agent工具集
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
│   ├── factory.py             # 模型工厂
│   └── multimodal_model.py    # 多模态LLM服务 ⭐ NEW
├── prompts/                    # 提示词模板
├── rag/                        # RAG模块
│   ├── advanced_retriever.py  # 高级检索器（MQE+HyDE）
│   ├── document_processor.py  # 智能文档处理器（支持多模态）⭐ NEW
│   └── vector_store.py        # 向量存储服务
├── utils/                      # 工具模块
├── main.py                     # 命令行入口
├── package.json                # 项目配置
└── README.md                   # 本文件
```

## 快速开始

### 体验多模态功能 ⭐ 最新

```bash
# 1. 检查环境配置
python check_multimodal_setup.py

# 2. 运行测试
python test_multimodal.py

# 3. 查看示例
python examples/multimodal_example.py
```

详细文档：[多模态功能使用指南.md](./多模态功能使用指南.md)

### 体验多智能体系统 ⭐ 推荐

```bash
# 安装依赖
pip install -r requirements.txt

# 运行交互式演示
python start_multi_agent_demo.py

# 或运行完整测试
python test_multi_agent.py
```

### Windows用户（最简单）

1. 双击 `安装依赖.bat` 安装依赖
2. 编辑 `model/.env` 配置API密钥
3. 双击 `启动后端.bat` 启动后端
4. 双击 `启动前端.bat` 启动前端
5. 访问 http://localhost:3000
6. 点击顶部"👥 多智能体"按钮切换到多智能体模式

### 跨平台方式

**安装依赖：**
```bash
# 前端
cd frontend && npm install

# 后端
cd backend && pip install -r requirements.txt
```

**启动服务（需要两个终端）：**
```bash
# 终端1：后端
cd backend && python api.py

# 终端2：前端
cd frontend && npm run dev
```

**访问：**
- 前端界面：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 命令行模式

```bash
pip install -r backend/requirements.txt
python main.py
```

## 配置

在 `model/.env` 文件中配置API密钥：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

获取API密钥：https://dashscope.console.aliyun.com/

## 功能特性

### Web界面
- 🎨 现代化UI设计，简洁高级
- 💬 实时智能问答
- 📚 知识库管理
- 🧠 记忆系统可视化
- 📊 统计数据展示

### 命令行界面
1. **加载知识库**: 首次使用或更新知识库
2. **开始问答**: 交互式问答模式
3. **查看记忆摘要**: 查看各层记忆状态
4. **清空工作记忆**: 清除对话上下文

### 编程接口

```python
from agent.graph_agent import SportsTrainingAgent

# 初始化Agent
agent = SportsTrainingAgent()

# 加载知识库
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
- **PyMuPDF**: 1.23.0 - PDF图像提取 ⭐ NEW
- **DashScope**: 1.19.0 - 阿里云模型API（含多模态）⭐ NEW

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


## 多智能体协同训练支持系统

### 系统架构

多智能体系统模拟真实运动指导团队，由5个专业虚拟教练协同工作：

```
用户输入 → 知识检索 → 意图分析 → 教练路由
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            单一意图模式                    综合咨询模式
                    ↓                               ↓
            激活对应教练              激活所有教练（顺序协作）
                    ↓                               ↓
                    └───────────────┬───────────────┘
                                    ↓
                            综合响应生成
                                    ↓
                            记忆系统更新
```

### 教练团队

| 教练 | 职责 | 激活关键词 |
|------|------|-----------|
| 📋 训练规划教练 | 制定科学训练计划并动态优化 | 计划、规划、安排、周期、目标 |
| 🎯 技术指导教练 | 提供动作指导和姿势分析 | 动作、姿势、技术、要领、标准 |
| 💪 体能评估教练 | 分析身体状态与疲劳程度 | 体能、疲劳、状态、评估、能力 |
| 🏥 运动康复教练 | 提供损伤预防与恢复建议 | 恢复、康复、损伤、伤痛、拉伤 |
| ⚠️ 安全督导教练 | 识别风险因素并提供安全提示 | 安全、风险、危险、注意、防护 |

### 使用示例

#### 场景1: 训练计划制定
```python
from agent.multi_agent_system import MultiAgentTrainingSystem

system = MultiAgentTrainingSystem()

result = system.process_request(
    "我想制定一个12周的增肌训练计划",
    user_profile={
        "fitness_level": "中级",
        "goals": ["增肌", "提高力量"]
    }
)

print(result['response'])
# 输出: 训练规划教练的详细计划
```

#### 场景2: 综合咨询
```python
result = system.process_request(
    "我是健身新手，想开始力量训练",
    user_profile={"fitness_level": "初级"}
)

# 所有教练协同工作，提供全方位指导
# - 训练规划教练：制定新手计划
# - 技术指导教练：讲解基础动作
# - 体能评估教练：评估初始体能
# - 运动康复教练：预防损伤建议
# - 安全督导教练：安全注意事项
```

### API接口

#### 多智能体查询
```bash
curl -X POST http://localhost:8000/api/multi-agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "深蹲的标准动作是什么？",
    "user_profile": {
      "fitness_level": "中级"
    }
  }'
```

#### 获取教练信息
```bash
curl http://localhost:8000/api/multi-agent/coaches
```

### 前端使用

1. 打开聊天界面
2. 点击顶部的"👥 多智能体"按钮
3. 输入问题，系统自动选择合适的教练团队
4. 查看各教练的专业建议

### 技术特点

- **智能路由**: 自动识别用户意图，激活相应教练
- **协同决策**: 多个教练按需协作，形成完整闭环
- **上下文共享**: 后续教练可访问前序教练的输出
- **RAG增强**: 所有教练都可访问知识库
- **记忆集成**: 完整记录工作流和参与教练

### 配置

编辑 `config/agent.yml`:

```yaml
multi_agent:
  enabled: true
  coaches:
    - name: planning_coach
      role: 训练规划教练
      description: 根据用户目标、能力和历史数据制定科学训练计划并动态优化
    # ... 其他教练配置
```

### 扩展开发

添加新教练：

1. 在 `multi_agent_system.py` 的 `_init_coaches()` 中定义
2. 更新 `_analyze_intent_node()` 添加关键词
3. 在状态图中添加节点和边
4. 更新配置文件

详细文档请参考：[多智能体训练系统使用指南.md](./多智能体训练系统使用指南.md)

## 文档

- [项目结构说明](PROJECT_STRUCTURE.md)
- [快速开始指南](QUICKSTART.md)
- [多模态功能使用指南](多模态功能使用指南.md) ⭐ NEW
- [多智能体系统使用指南](多智能体训练系统使用指南.md)
- [后端API文档](backend/README.md)
- [前端开发文档](frontend/README.md)

## 技术栈

- **后端**: Python 3.8+, FastAPI, LangChain, LangGraph, ChromaDB
- **前端**: Vue 3, Vue Router, Axios, Vite
- **AI模型**: 阿里云DashScope (通义千问)
- **向量数据库**: ChromaDB
- **文档处理**: MarkItDown

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
