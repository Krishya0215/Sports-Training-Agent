"""
LangGraph Agent - 运动训练知识问答Agent
使用状态图管理对话流程
"""
from typing import TypedDict, List, Annotated
from operator import add
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from model.factory import chat_model
from rag.vector_store import VectorStoreService
from rag.advanced_retriever import AdvancedRetriever
from memory.memory_manager import MemoryManager
from utils.logger_handler import logger
from utils.config_handler import agent_conf
from utils.prompt_loader import load_prompt_by_key


class AgentState(TypedDict):
    """Agent状态定义"""
    question: str  # 用户问题
    chat_history: str  # 对话历史
    retrieved_docs: List[Document]  # 检索到的文档
    context: str  # 格式化的上下文
    answer: str  # 最终答案
    iteration: int  # 迭代次数


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
        """构建LangGraph状态图"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("format_context", self._format_context_node)
        workflow.add_node("generate_answer", self._generate_answer_node)
        workflow.add_node("update_memory", self._update_memory_node)
        
        # 定义边
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "format_context")
        workflow.add_edge("format_context", "generate_answer")
        workflow.add_edge("generate_answer", "update_memory")
        workflow.add_edge("update_memory", END)
        
        return workflow.compile()
    
    def _retrieve_node(self, state: AgentState) -> AgentState:
        """检索节点 - 使用高级检索器"""
        question = state["question"]
        logger.info(f"开始检索: {question}")
        
        # 使用高级检索器（MQE + HyDE）
        retrieved_docs = self.retriever.retrieve(question)
        
        state["retrieved_docs"] = retrieved_docs
        logger.info(f"检索完成，获得 {len(retrieved_docs)} 个文档")
        
        return state
    
    def _format_context_node(self, state: AgentState) -> AgentState:
        """格式化上下文节点"""
        retrieved_docs = state["retrieved_docs"]
        
        # 格式化检索到的文档
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.metadata.get("source", "未知来源")
            context_parts.append(f"[文档{i}] 来源: {source}\n内容: {doc.page_content}\n")
        
        context = "\n".join(context_parts)
        state["context"] = context
        
        # 获取对话历史
        chat_history = self.memory_manager.get_context_for_query()
        state["chat_history"] = chat_history
        
        logger.info("上下文格式化完成")
        return state
    
    def _generate_answer_node(self, state: AgentState) -> AgentState:
        """生成答案节点"""
        question = state["question"]
        context = state["context"]
        chat_history = state["chat_history"]
        
        logger.info("开始生成答案")
        
        # 使用答案生成链
        answer = self.answer_chain.invoke({
            "question": question,
            "retrieved_context": context,
            "chat_history": chat_history if chat_history else "无历史对话"
        })
        
        state["answer"] = answer
        logger.info("答案生成完成")
        
        return state
    
    def _update_memory_node(self, state: AgentState) -> AgentState:
        """更新记忆节点"""
        question = state["question"]
        answer = state["answer"]
        retrieved_docs = state["retrieved_docs"]
        
        # 提取文档来源
        doc_sources = [doc.metadata.get("source", "未知") for doc in retrieved_docs]
        
        # 记录交互到记忆系统
        self.memory_manager.record_interaction(
            question=question,
            answer=answer,
            retrieved_docs=doc_sources,
            metadata={"num_docs": len(retrieved_docs)}
        )
        
        logger.info("记忆更新完成")
        return state
    
    def query(self, question: str) -> str:
        """
        处理用户查询
        
        Args:
            question: 用户问题
            
        Returns:
            答案
        """
        # 初始化状态
        initial_state = {
            "question": question,
            "chat_history": "",
            "retrieved_docs": [],
            "context": "",
            "answer": "",
            "iteration": 0
        }
        
        # 执行图
        try:
            final_state = self.graph.invoke(initial_state)
            return final_state["answer"]
        except Exception as e:
            logger.error(f"查询处理失败: {e}")
            return f"抱歉，处理您的问题时出现错误: {str(e)}"
    
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
