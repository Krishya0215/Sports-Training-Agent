# 快速开始指南

## 🚀 5分钟快速上手

### 前置要求

- Python 3.8 或更高版本
- pip 包管理器
- 阿里云 DashScope API 密钥（免费注册）

### 步骤1: 克隆或下载项目

```bash
# 如果是Git仓库
git clone <repository-url>
cd sports-training-agent

# 或直接解压下载的项目文件
```

### 步骤2: 安装依赖

```bash
# 推荐：先升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

**常见问题解决**：

如果遇到依赖冲突，尝试：
```bash
# 方案1: 使用最新兼容版本
pip install langchain langchain-community langgraph langchain-chroma chromadb dashscope python-dotenv pyyaml loguru markitdown pypdf pillow

# 方案2: 使用虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

### 步骤3: 配置API密钥

1. 注册阿里云账号并开通 DashScope 服务
   - 访问: https://dashscope.console.aliyun.com/
   - 点击"开通DashScope"（免费额度足够测试使用）
   - 创建 API Key

2. 创建并编辑 `model/.env` 文件：

```bash
# Windows
echo DASHSCOPE_API_KEY=your_api_key_here > model\.env

# Linux/Mac
echo "DASHSCOPE_API_KEY=your_api_key_here" > model/.env
```

或手动创建 `model/.env` 文件，内容如下：
```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ 注意：请将 `your_api_key_here` 替换为你的实际 API 密钥

### 步骤4: 准备知识库

项目已包含示例数据 `data/sample_sports_training.md`，包含运动训练基础知识。

**添加自己的文档**：
```bash
# 将PDF、Markdown或文本文件复制到data目录
# Windows
copy your_document.pdf data\
# Linux/Mac
cp your_document.pdf data/
```

支持的文件格式：
- ✅ PDF（多模态，包含文本和图像）
- ✅ Markdown (.md)
- ✅ 纯文本 (.txt)

### 步骤5: 加载知识库

首次运行需要加载知识库到向量数据库：

```bash
python main.py
```

在菜单中选择 `1` 加载知识库，等待处理完成（首次可能需要1-2分钟）。

### 步骤6: 开始问答

在主菜单选择 `2` 开始问答，然后输入你的问题：

```
请输入您的问题: 什么是有氧运动？
```

输入 `quit` 返回主菜单。

---

## 💬 示例对话

### 基础问答

```
请输入您的问题: 什么是有氧运动？

正在思考...

================================================================================
回答:
有氧运动是指人体在氧气充分供应的情况下进行的体育锻炼。其特点是强度低、
有节奏、持续时间较长。在运动过程中，吸入的氧气与需求相等，达到生理上的
平衡状态。

常见的有氧运动包括：
- 跑步：最简单有效的有氧运动
- 游泳：全身性运动，对关节压力小
- 骑自行车：锻炼下肢力量和心肺功能
- 快走：低强度，适合初学者
- 跳绳：高效燃脂，提升协调性
================================================================================
```

### 上下文对话（记忆功能）

```
请输入您的问题: 什么是力量训练？

回答:
力量训练通过抗阻运动增强肌肉力量和耐力。它不仅能塑造体型，还能提高
基础代谢率，预防骨质疏松...

请输入您的问题: 它有什么好处？

回答:
力量训练的好处包括：
1. 增强肌肉力量和耐力
2. 提高基础代谢率，有助于减脂
3. 改善体态和身体线条
4. 预防骨质疏松
5. 提升运动表现
...
```

> 💡 注意：Agent 能理解"它"指的是前面提到的"力量训练"

### 复杂查询（高级检索）

```
请输入您的问题: 我想减肥，应该做什么运动？运动后怎么吃？

回答:
针对减肥目标，建议结合有氧运动和力量训练：

**运动方面**：
- 有氧运动：每周3-5次，每次30-45分钟（跑步、游泳、骑车）
- 力量训练：每周2-3次，增加肌肉量提高代谢

**运动后营养**：
- 蛋白质：20-30克（鸡胸肉、鸡蛋、牛奶）
- 碳水化合物：适量补充（糙米、红薯）
- 水分：体重每减少0.5kg补充500-700ml

建议在运动后30分钟内进食，促进肌肉恢复...
```

---

## 🧪 运行测试

在使用前，建议先运行测试确保一切正常：

```bash
# 测试知识库加载
python test_agent.py loading

# 测试基础查询功能
python test_agent.py basic

# 测试上下文感知能力
python test_agent.py context

# 测试记忆系统
python test_agent.py memory

# 测试高级检索（MQE + HyDE）
python test_agent.py retrieval

# 运行所有测试
python test_agent.py all
```

**预期输出**：
```
================================================================================
开始测试: 知识库加载
================================================================================

开始加载知识库...
✓ 知识库加载成功

✓ 知识库加载 测试完成
```

---

## 💻 编程接口示例

### 基础使用

```python
from agent.graph_agent import SportsTrainingAgent

# 1. 初始化Agent
agent = SportsTrainingAgent()

# 2. 加载知识库（首次运行或更新知识库时）
agent.load_knowledge_base()

# 3. 单次查询
answer = agent.query("如何进行深蹲训练？")
print(answer)
```

### 上下文对话

```python
# 连续对话（自动保持上下文）
agent.query("什么是力量训练？")
answer = agent.query("它有什么好处？")  # 会理解"它"指的是力量训练
print(answer)

# 查看对话历史
context = agent.memory_manager.get_context_for_query()
print(context)
```

### 记忆管理

```python
# 查看记忆状态
summary = agent.get_memory_summary()
print(summary)
# 输出: {
#   'working_memory_size': 4,
#   'episodic_memory_size': 2,
#   'semantic_concepts': 0,
#   'perceptual_documents': 0
# }

# 清空工作记忆（开始新话题）
agent.clear_working_memory()

# 访问情景记忆
if agent.memory_manager.episodic_memory:
    recent = agent.memory_manager.episodic_memory.get_recent_episodes(n=5)
    for episode in recent:
        print(f"问题: {episode['question']}")
        print(f"时间: {episode['timestamp']}")
```

### 批量查询

```python
questions = [
    "什么是有氧运动？",
    "如何进行力量训练？",
    "运动后如何拉伸？"
]

for q in questions:
    print(f"\n问题: {q}")
    answer = agent.query(q)
    print(f"答案: {answer}")
    print("-" * 80)
```

### 自定义检索

```python
from rag.vector_store import VectorStoreService
from rag.advanced_retriever import AdvancedRetriever

# 直接使用检索器
vector_store = VectorStoreService()
base_retriever = vector_store.get_retriever()
advanced_retriever = AdvancedRetriever(base_retriever)

# 检索相关文档
docs = advanced_retriever.retrieve("深蹲训练技巧")
for doc in docs:
    print(doc.page_content)
    print(doc.metadata)
```

---

## ⚙️ 配置调整

### 记忆系统配置

编辑 `config/agent.yml`:

```yaml
memory:
  working_memory_size: 10           # 工作记忆保留轮数（默认5）
  episodic_memory_enabled: true     # 启用情景记忆
  semantic_memory_enabled: true     # 启用语义记忆
  perceptual_memory_enabled: true   # 启用感知记忆
```

**建议**：
- 短对话场景：`working_memory_size: 3-5`
- 长对话场景：`working_memory_size: 10-15`
- 内存受限：禁用部分记忆模块

### 检索策略配置

编辑 `config/agent.yml`:

```yaml
retrieval:
  use_multi_query: true    # 多查询扩展（提升召回率）
  use_hyde: true           # 假设文档嵌入（提升精确度）
  num_queries: 3           # MQE生成的查询数量
  rerank_enabled: true     # 重排序
```

**性能优化**：
- 快速响应：`use_multi_query: false, use_hyde: false`
- 高质量结果：`use_multi_query: true, use_hyde: true, num_queries: 5`
- 平衡模式：默认配置

### 文档处理配置

编辑 `config/chroma.yml`:

```yaml
# 文档处理
document_processing:
  use_markitdown: true              # 使用MarkItDown处理PDF
  extract_images: true              # 提取图像
  image_description_enabled: true   # 为图像生成描述

# 分块策略
chunk_size: 800                     # 分块大小（字符数）
chunk_overlap: 100                  # 重叠大小
separators: ["\n## ", "\n### ", "\n#### ", "\n\n", "\n", "。"]

# 检索参数
k: 5                                # 返回文档数量
score_threshold: 0.6                # 相似度阈值
```

**分块策略建议**：
- 短文档/FAQ：`chunk_size: 400-600`
- 长文档/教程：`chunk_size: 800-1200`
- 技术文档：`chunk_size: 1000-1500`

### 模型配置

编辑 `config/rag.yml`:

```yaml
# 使用更强大的模型
chat_model_name: qwen-plus          # 或 qwen-max, qwen-turbo
embedding_model_name: text-embedding-v3
```

**模型选择**：
- `qwen-flash`: 快速响应，适合简单问答
- `qwen-plus`: 平衡性能和质量（推荐）
- `qwen-max`: 最高质量，响应较慢

---

## ❓ 常见问题

### Q1: 如何添加新的知识文档？

**A**: 
1. 将文件放入 `data/` 目录
2. 在主程序中选择 "1. 加载知识库"
3. 系统会自动检测新文件并处理（基于MD5去重）

```bash
# 示例
cp my_training_guide.pdf data/
python main.py  # 选择1加载知识库
```

### Q2: 支持哪些文件格式？

**A**: 
- ✅ **PDF**: 多模态支持（文本+图像），通过MarkItDown转换
- ✅ **Markdown** (.md): 保留结构化信息
- ✅ **纯文本** (.txt): 基础文本文档

### Q3: 如何清空知识库重新开始？

**A**:
```bash
# Windows
rmdir /s /q rag\chroma_db
del md5.txt

# Linux/Mac
rm -rf rag/chroma_db
rm md5.txt

# 然后重新加载
python main.py  # 选择1
```

### Q4: 记忆系统如何工作？

**A**: 四层记忆架构：

| 记忆类型 | 功能 | 容量 | 用途 |
|---------|------|------|------|
| **工作记忆** | 当前对话上下文 | 最近N轮 | 理解上下文、代词消解 |
| **情景记忆** | 问答历史记录 | 无限制 | 查询历史、学习轨迹 |
| **语义记忆** | 概念知识存储 | 可扩展 | 概念理解、关系推理 |
| **感知记忆** | 文档特征 | 可扩展 | 多模态信息、文档元数据 |

### Q5: MQE和HyDE是什么？为什么需要它们？

**A**:

**多查询扩展 (MQE)**:
- 将一个问题改写为多个变体
- 例如："如何减肥？" → ["减肥的方法有哪些？", "怎样有效减脂？", "减重训练计划"]
- 优势：提高召回率，找到更多相关文档

**假设文档嵌入 (HyDE)**:
- 先生成一个假设性答案，用答案去检索
- 例如：问题 → 生成假设答案 → 用答案检索相似文档
- 优势：提高精确度，找到更准确的文档

### Q6: 如何切换到更强大的模型？

**A**: 编辑 `config/rag.yml`:

```yaml
# 选项1: 更快速（适合测试）
chat_model_name: qwen-flash
embedding_model_name: text-embedding-v3

# 选项2: 平衡性能（推荐）
chat_model_name: qwen-plus
embedding_model_name: text-embedding-v3

# 选项3: 最高质量
chat_model_name: qwen-max
embedding_model_name: text-embedding-v3
```

### Q7: 为什么回答质量不好？

**A**: 检查以下几点：

1. **知识库质量**: 确保文档内容相关且准确
2. **分块大小**: 调整 `chunk_size`（建议800-1200）
3. **检索数量**: 增加 `k` 值（建议5-10）
4. **启用高级检索**: 确保 `use_multi_query` 和 `use_hyde` 为 true
5. **模型选择**: 使用更强大的模型（qwen-plus 或 qwen-max）

### Q8: 如何查看日志排查问题？

**A**:
```bash
# 查看最新日志
# Windows
type logs\agent_20260206.log

# Linux/Mac
tail -f logs/agent_20260206.log

# 查看错误信息
# Windows
findstr "ERROR" logs\agent_20260206.log

# Linux/Mac
grep "ERROR" logs/agent_20260206.log
```

### Q9: 内存占用太大怎么办？

**A**: 优化配置：

```yaml
# config/agent.yml
memory:
  working_memory_size: 3              # 减少工作记忆
  episodic_memory_enabled: false      # 禁用情景记忆
  semantic_memory_enabled: false      # 禁用语义记忆
  perceptual_memory_enabled: false    # 禁用感知记忆

# config/chroma.yml
k: 3                                  # 减少检索数量
chunk_size: 600                       # 减小分块大小
```

### Q10: 如何在生产环境部署？

**A**: 
1. 使用虚拟环境隔离依赖
2. 配置环境变量而非 .env 文件
3. 使用进程管理器（如 supervisor）
4. 添加日志轮转
5. 监控API调用量和成本
6. 考虑使用本地模型（如 Ollama）降低成本

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 [技术架构](#) 了解实现细节
- 探索 [配置选项](#) 进行个性化定制
- 贡献你的改进和建议

## 获取帮助

- 查看日志: `logs/agent_YYYYMMDD.log`
- 提交Issue: [GitHub Issues](#)
- 查看文档: [完整文档](#)


---

## 📚 下一步

### 深入学习

1. **阅读完整文档**
   - [README.md](README.md) - 完整功能介绍
   - 项目架构和技术细节
   - 扩展开发指南

2. **探索高级功能**
   - 自定义提示词模板
   - 集成其他模型（OpenAI、本地模型）
   - 添加自定义工具和节点

3. **性能优化**
   - 调整分块策略
   - 优化检索参数
   - 配置缓存机制

### 实际应用场景

- 🏋️ **健身房助手**: 为健身房提供智能问答服务
- 📱 **运动APP**: 集成到移动应用提供训练指导
- 🎓 **教育培训**: 辅助体育教学和培训
- 🏥 **康复指导**: 提供运动康复建议（需专业审核）

### 扩展方向

1. **多模态增强**
   - 集成视觉模型理解训练动作图片
   - 生成训练动作示意图
   - 视频内容分析

2. **个性化推荐**
   - 基于用户画像定制训练计划
   - 记录训练历史和进度
   - 智能调整训练强度

3. **知识图谱**
   - 构建运动训练概念图谱
   - 实现关系推理
   - 提供结构化知识浏览

4. **实时交互**
   - Web界面（Streamlit/Gradio）
   - API服务（FastAPI）
   - 聊天机器人集成

---

## 🆘 获取帮助

### 日志查看

```bash
# Windows - 查看最新日志
type logs\agent_20260206.log

# Linux/Mac - 实时查看日志
tail -f logs/agent_20260206.log

# 搜索错误信息
# Windows
findstr "ERROR" logs\*.log
# Linux/Mac
grep "ERROR" logs/*.log
```

### 调试模式

在代码中启用详细日志：

```python
from utils.logger_handler import logger
import sys

# 设置日志级别为DEBUG
logger.remove()
logger.add(sys.stderr, level="DEBUG")
```

### 常见错误解决

**错误1**: `ModuleNotFoundError: No module named 'xxx'`
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

**错误2**: `API key not found`
```bash
# 检查.env文件
cat model/.env  # Linux/Mac
type model\.env  # Windows

# 确保格式正确
DASHSCOPE_API_KEY=sk-xxxxxxxx
```

**错误3**: `ChromaDB connection error`
```bash
# 删除并重建数据库
rm -rf rag/chroma_db  # Linux/Mac
rmdir /s /q rag\chroma_db  # Windows
python main.py  # 重新加载
```

**错误4**: `Memory error / Out of memory`
```yaml
# 减少配置参数 (config/agent.yml)
memory:
  working_memory_size: 3
retrieval:
  use_multi_query: false
  use_hyde: false
```

### 社区支持

- 💬 提交 Issue 报告问题
- 🌟 Star 项目支持开发
- 🔀 Fork 项目进行定制
- 📧 联系维护者获取帮助

---

## 📝 许可证

MIT License - 自由使用、修改和分发

---

## 🎉 开始使用

现在你已经准备好了！运行以下命令开始你的运动训练知识问答之旅：

```bash
python main.py
```

祝你使用愉快！💪
