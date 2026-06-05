"""
LangGraph Agent - 运动训练知识问答Agent
使用状态图管理对话流程
支持智能问题分类和RAG工具调用
"""
import re
from typing import TypedDict, List, Annotated
from operator import add
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from backend.model.factory import chat_model
from backend.rag.vector_store import VectorStoreService
from backend.rag.advanced_retriever import AdvancedRetriever
from backend.memory.memory_manager import MemoryManager
from backend.utils.logger_handler import logger
from backend.utils.config_handler import agent_conf
from backend.utils.prompt_loader import load_prompt_by_key
from backend.agent.tools.agent_tools import QuestionClassifier, query_training_knowledge_base


class AgentState(TypedDict):
    """Agent状态定义"""
    question: str  # 用户问题
    chat_history: str  # 对话历史
    retrieved_docs: List[Document]  # 检索到的文档
    context: str  # 格式化的上下文
    answer: str  # 最终答案
    iteration: int  # 迭代次数
    question_type: str  # 问题类型 ('professional' 或 'chat')
    use_rag: bool  # 是否使用RAG
    classification_confidence: float  # 分类置信度
    doc_sources: List[str]  # 去重后的文档来源文件名列表
    memory_context: dict  # 用户记忆上下文


class SportsTrainingAgent:
    """运动训练知识问答Agent"""
    
    def __init__(self):
        # 初始化向量存储和检索器
        self.vector_store_service = VectorStoreService()
        base_retriever = self.vector_store_service.get_retriever()
        self.retriever = AdvancedRetriever(base_retriever)
        
        # 初始化记忆管理器
        self.memory_manager = MemoryManager()
        
        # 初始化模型
        self.model = chat_model
        
        # 加载提示词
        answer_prompt_text = load_prompt_by_key("answer_generation_prompt")
        self.answer_prompt = PromptTemplate.from_template(answer_prompt_text)
        
        # 创建答案生成链
        self.answer_chain = self.answer_prompt | self.model | StrOutputParser()
        
        # 构建LangGraph工作流
        self.graph = self._build_graph()
        
        logger.info("运动训练知识问答Agent初始化完成")
    
    def _build_graph(self) -> StateGraph:
        """
        构建LangGraph状态图
        流程：问题分类 -> 根据类型决定是否使用RAG -> 生成答案 -> 更新记忆
        """
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("classify_question", self._classify_question_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("direct_response", self._direct_response_node)  # 直接回复节点
        workflow.add_node("format_context", self._format_context_node)
        workflow.add_node("generate_answer", self._generate_answer_node)
        workflow.add_node("update_memory", self._update_memory_node)
        
        # 定义边
        workflow.set_entry_point("classify_question")
        
        # 问题分类后，根据结果选择路径
        def route_after_classification(state: AgentState):
            if state["use_rag"]:
                return "retrieve"  # 需要RAG则进入检索
            else:
                return "direct_response"  # 纯聊天则直接回复
        
        workflow.add_conditional_edges(
            "classify_question",
            route_after_classification,
            {
                "retrieve": "retrieve",
                "direct_response": "direct_response"
            }
        )
        
        # RAG路径: 检索 -> 格式化 -> 生成答案
        workflow.add_edge("retrieve", "format_context")
        workflow.add_edge("format_context", "generate_answer")
        
        # 直接回复路径
        workflow.add_edge("direct_response", "generate_answer")
        
        # 最后都进入更新记忆和结束
        workflow.add_edge("generate_answer", "update_memory")
        workflow.add_edge("update_memory", END)
        
        return workflow.compile()
    
    def _classify_question_node(self, state: AgentState) -> AgentState:
        """
        问题分类节点
        判断问题类型并决定是否需要使用RAG
        """
        question = state["question"]
        
        # 使用分类器判断
        use_rag, reason, confidence = QuestionClassifier.should_use_rag(question)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📋 问题分类")
        logger.info(f"问题: {question}")
        logger.info(f"分类结果: {'专业问题 (需要RAG)' if use_rag else '聊天问题 (直接回复)'}")
        logger.info(f"原因: {reason}")
        logger.info(f"置信度: {confidence*100:.1f}%")
        logger.info(f"{'='*60}\n")
        
        state["use_rag"] = use_rag
        state["question_type"] = "professional" if use_rag else "chat"
        state["classification_confidence"] = confidence
        
        return state
    
    def _direct_response_node(self, state: AgentState) -> AgentState:
        """
        直接回复节点
        用于纯聊天问题，不需要知识库，直接用LLM生成回复
        """
        question = state["question"]
        chat_history = self.memory_manager.get_context_for_query()

        # state["context"] 在 query() 入口已填入 memory_prompt（含饮食/训练记录等），直接读取
        memory_prompt = state.get("context", "") or ""

        logger.info(f"\n📝 直接生成回复 (无需RAG)")
        logger.info(f"记忆上下文长度: {len(memory_prompt)} 字")
        logger.info(f"问题: {question}\n")

        # 创建简化的提示词，用于聊天场景
        chat_prompt = PromptTemplate.from_template("""
你是一个专业的运动训练AI教练，名字叫卡卡(KaKa)，风格温暖、鼓励、专业。

【铁律】只有用户明确说"帮我制定计划"、"给我一份方案"、"生成计划"等包含明确动作指令和计划词的请求时，才输出训练计划。其他所有情况禁止生成训练计划。

{memory_context}

对话历史：
{chat_history}

用户输入：{question}

请自然、简洁地回应。如果用户在陈述状态（如"我手腕受伤了"），先表达关心再给简短建议；如果是提问，简洁回答要点；结尾可以询问是否需要制定计划，但禁止直接生成计划。
""")

        chat_chain = chat_prompt | self.model | StrOutputParser()

        answer = chat_chain.invoke({
            "question": question,
            "chat_history": chat_history if chat_history else "无历史对话",
            "memory_context": memory_prompt if memory_prompt else "暂无用户历史记录"
        })
        
        # 不使用知识库，所以context为空
        state["context"] = "[采用对话模式，无知识库查询]"
        state["retrieved_docs"] = []
        state["answer"] = answer
        
        logger.info(f"✓ 直接回复生成完成\n")
        
        return state
    
    def _retrieve_node(self, state: AgentState) -> AgentState:
        """
        检索节点 - 使用高级检索器
        专业问题才会进入此节点
        """
        question = state["question"]
        logger.info(f"\n📚 启动RAG知识库检索")
        logger.info(f"问题: {question}\n")
        
        # 使用高级检索器（MQE + HyDE）
        retrieved_docs = self.retriever.retrieve(question)
        
        state["retrieved_docs"] = retrieved_docs
        logger.info(f"✓ 检索完成，获得 {len(retrieved_docs)} 个文档\n")
        
        return state
    
    def _format_context_node(self, state: AgentState) -> AgentState:
        """
        格式化上下文节点
        处理RAG检索结果的格式化
        """
        retrieved_docs = state.get("retrieved_docs", [])
        memory_prompt = state.get("memory_context", {}).get("_memory_prompt", "") or ""

        if retrieved_docs:
            logger.info(f"\n📋 格式化检索上下文")
            # 格式化检索到的文档
            context_parts = []
            seen_sources = []
            for i, doc in enumerate(retrieved_docs, 1):
                source = doc.metadata.get("source", "未知来源")
                file_name = doc.metadata.get("file_name", "") or (source.split("/")[-1] if "/" in source else source)
                context_parts.append(f"[文档{i}] 来源: {file_name}\n内容: {doc.page_content}\n")
                if file_name not in seen_sources:
                    seen_sources.append(file_name)

            context = "\n".join(context_parts)
            state["context"] = context
            state["doc_sources"] = seen_sources
            logger.info(f"✓ 上下文格式化完成 ({len(retrieved_docs)} 个文档，{len(seen_sources)} 个来源)\n")
        else:
            # 没有检索到文档
            state["context"] = "[无知识库内容]"
            state["doc_sources"] = []

        # 将记忆上下文追加到context中，确保LLM能看到用户的历史记录
        if memory_prompt:
            state["context"] = f"{state['context']}\n\n{memory_prompt}"

        # 获取对话历史
        chat_history = self.memory_manager.get_context_for_query()
        state["chat_history"] = chat_history

        return state
    
    def _generate_answer_node(self, state: AgentState) -> AgentState:
        """
        生成答案节点
        处理RAG场景和直接聊天场景
        """
        question = state["question"]
        context = state.get("context", "")
        chat_history = state.get("chat_history", "")

        # 如果已经是直接回复模式，answer字段已经填充
        if state.get("answer"):
            logger.info(f"\n💬 使用已生成的直接回复")
            logger.info(f"✓ 答案生成完成\n")
            return state

        # RAG模式：需要生成答案，每次动态加载 prompt 确保文件改动即时生效
        logger.info(f"\n🤖 基于知识库生成答案")

        answer_prompt_text = load_prompt_by_key("answer_generation_prompt")
        answer_prompt = PromptTemplate.from_template(answer_prompt_text)
        answer_chain = answer_prompt | self.model | StrOutputParser()

        answer = answer_chain.invoke({
            "question": question,
            "retrieved_context": context,
            "chat_history": chat_history if chat_history else "无历史对话"
        })

        # 追加参考来源（先移除LLM可能已生成的重复参考来源块）
        answer = re.split(r'\n*(?:---\n+)?\*{0,2}📚\s*参考来源', answer)[0].rstrip()
        doc_sources = state.get("doc_sources", [])
        if doc_sources:
            sources_text = "\n".join(f"- {src}" for src in doc_sources)
            answer += f"\n\n---\n\n**📚 参考来源**\n\n{sources_text}"

        state["answer"] = answer
        logger.info(f"✓ 答案生成完成\n")

        return state
    
    def _update_memory_node(self, state: AgentState) -> AgentState:
        """
        更新记忆节点
        记录交互和问题分类信息
        """
        question = state["question"]
        answer = state["answer"]
        retrieved_docs = state.get("retrieved_docs", [])
        use_rag = state.get("use_rag", False)
        question_type = state.get("question_type", "unknown")
        confidence = state.get("classification_confidence", 0)
        
        # 提取文档来源
        doc_sources = [doc.metadata.get("source", "未知") for doc in retrieved_docs]
        
        logger.info(f"\n💾 更新记忆")
        logger.info(f"问题分类: {question_type} (置信度: {confidence*100:.1f}%)")
        logger.info(f"使用RAG: {'是' if use_rag else '否'}")
        logger.info(f"检索文档: {len(doc_sources)} 个")
        
        # 记录交互到记忆系统
        self.memory_manager.record_interaction(
            question=question,
            answer=answer,
            retrieved_docs=doc_sources,
            metadata={
                "num_docs": len(retrieved_docs),
                "use_rag": use_rag,
                "question_type": question_type,
                "classification_confidence": confidence
            }
        )
        
        logger.info(f"✓ 记忆更新完成\n")
        
        logger.info("记忆更新完成")
        return state
    
    def query(self, question: str, return_thinking: bool = True, memory_context: dict = None) -> dict:
        """
        处理用户查询

        Args:
            question: 用户问题
            return_thinking: 是否返回思考过程
            memory_context: 用户记忆上下文（语义记忆、情景记忆等）

        Returns:
            包含答案和思考过程的字典
        """
        # 构建记忆上下文字符串
        memory_prompt = ""
        if memory_context:
            from backend.memory.memory_service import memory_service
            memory_prompt = memory_service.build_memory_prompt(memory_context.get("user_id", 0) if memory_context.get("user_id") else 0, memory_context)

        # 初始化状态
        initial_state = {
            "question": question,
            "chat_history": "",
            "retrieved_docs": [],
            "context": memory_prompt or "",  # 将记忆上下文注入到 context
            "answer": "",
            "iteration": 0,
            "question_type": "unknown",
            "use_rag": False,
            "classification_confidence": 0,
            "doc_sources": [],
            "memory_context": memory_context or {}  # 传递完整的记忆上下文
        }
        
        # 执行图，添加重试逻辑
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"🚀 查询尝试 {attempt + 1}/{max_retries}")
                logger.info(f"问题: {question[:80]}")
                logger.info(f"{'='*60}\n")
                final_state = self.graph.invoke(initial_state)
                
                # 构建思考过程
                thinking_process = []
                thinking_process.append(f"📖 **接收问题**: {question}")
                
                # 添加问题分类信息
                question_type = final_state.get("question_type", "unknown")
                use_rag = final_state.get("use_rag", False)
                confidence = final_state.get("classification_confidence", 0)
                
                if question_type == "professional":
                    thinking_process.append(f"📋 **问题分类**: 专业运动训练问题 (置信度 {confidence*100:.0f}%)")
                    thinking_process.append(f"🔍 **启动RAG检索**: 在知识库中查询相关内容")
                    thinking_process.append(f"📄 **检索结果**: 找到 {len(final_state.get('retrieved_docs', []))} 个相关文档")
                    thinking_process.append(f"📝 **组织信息**: 整合知识库内容和对话历史")
                else:
                    thinking_process.append(f"💬 **问题分类**: 日常聊天问题 (置信度 {confidence*100:.0f}%)")
                    thinking_process.append(f"🤖 **模式**: 直接对话模式（不需要知识库）")
                
                thinking_process.append(f"💡 **生成答案**: 基于分类结果生成回复")
                
                result = {
                    "thinking": "\n".join(thinking_process),
                    "answer": final_state["answer"],
                    "metadata": {
                        "docs_count": len(final_state.get("retrieved_docs", [])),
                        "question_type": question_type,
                        "use_rag": use_rag,
                        "classification_confidence": confidence,
                        "attempt": attempt + 1
                    }
                }
                
                logger.info(f"\n✓ 查询成功 (第 {attempt + 1} 次尝试)\n")
                return result
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                logger.warning(f"查询失败 (第 {attempt + 1}/{max_retries}): {error_str[:100]}")
                
                # 检查是否是SSL错误或网络错误
                is_network_error = any(keyword in error_str.lower() 
                                      for keyword in ['ssl', 'timeout', 'connection', 'max retries'])
                
                if is_network_error and attempt < max_retries - 1:
                    import time
                    wait_time = 2 ** attempt  # 指数退避：1秒，2秒，4秒
                    logger.info(f"网络错误，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif attempt < max_retries - 1:
                    # 非网络错误也重试一次
                    logger.info(f"正在重试...")
                    continue
        
        # 所有重试都失败了
        logger.error(f"经过 {max_retries} 次重试后，查询仍然失败: {str(last_error)[:200]}")
        
        # 生成用户友好的错误消息
        error_msg = str(last_error)
        if 'ssl' in error_msg.lower():
            thinking = "❌ **SSL连接错误**\n\n与AI服务的连接出现问题，可能是网络故障或服务暂时不可用。"
            answer = "抱歉，我现在无法连接到AI服务。请检查您的网络连接，稍后重试。"
        elif 'timeout' in error_msg.lower():
            thinking = "❌ **请求超时**\n\nAI服务响应时间过长。"
            answer = "请求处理超时了，请稍后重试。"
        else:
            thinking = f"❌ **处理出错**\n\n{error_msg[:100]}"
            answer = f"抱歉，处理您的问题时出现错误，请稍后重试。\n\n错误信息：{error_msg[:150]}"
        
        return {
            "thinking": thinking,
            "answer": answer,
            "metadata": {
                "error": True,
                "error_type": type(last_error).__name__,
                "attempts": max_retries
            }
        }
    
    def load_knowledge_base(self):
        """加载知识库"""
        logger.info("开始加载知识库...")
        self.vector_store_service.load_documents()
        logger.info("知识库加载完成")
    
    def get_memory_summary(self):
        """获取记忆摘要"""
        return self.memory_manager.summarize_memory()
    
    def clear_working_memory(self):
        """清空工作记忆"""
        self.memory_manager.working_memory.clear()
        logger.info("工作记忆已清空")


if __name__ == "__main__":
    # 测试Agent
    agent = SportsTrainingAgent()
    
    # 加载知识库（首次运行）
    # agent.load_knowledge_base()
    
    # 测试查询
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
    
    # 查看记忆摘要
    print("\n记忆摘要:")
    print(agent.get_memory_summary())
