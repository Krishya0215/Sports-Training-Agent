"""
高级检索模块 - 实现多查询扩展(MQE)和假设文档嵌入(HyDE)
"""
from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from backend.model.factory import chat_model, embedding_model
from backend.utils.logger_handler import logger
from backend.utils.config_handler import agent_conf, prompts_conf
from backend.utils.prompt_loader import load_prompt_by_key


class MultiQueryExpansion:
    """多查询扩展 - 生成多个查询变体提升召回率"""
    
    def __init__(self, num_queries: int = 3):
        self.num_queries = num_queries
        self.model = chat_model
        
        # 加载提示词
        prompt_text = load_prompt_by_key("multi_query_prompt")
        self.prompt = PromptTemplate.from_template(prompt_text)
        
        # 创建查询生成链
        self.chain = self.prompt | self.model | StrOutputParser()
    
    def generate_queries(self, question: str) -> List[str]:
        """
        生成多个查询变体
        
        Args:
            question: 原始问题
            
        Returns:
            查询列表（包含原始问题）
        """
        try:
            # 生成变体查询
            response = self.chain.invoke({
                "question": question,
                "num_queries": self.num_queries
            })
            
            # 解析生成的查询
            queries = [q.strip() for q in response.split('\n') if q.strip()]
            
            # 确保包含原始问题
            if question not in queries:
                queries.insert(0, question)
            
            logger.info(f"多查询扩展生成 {len(queries)} 个查询: {queries}")
            return queries[:self.num_queries + 1]
            
        except Exception as e:
            logger.error(f"多查询扩展失败: {e}")
            return [question]


class HyDERetriever:
    """假设文档嵌入 - 生成假设答案改善检索精度"""
    
    def __init__(self):
        self.model = chat_model
        
        # 加载提示词
        prompt_text = load_prompt_by_key("hyde_prompt")
        self.prompt = PromptTemplate.from_template(prompt_text)
        
        # 创建假设答案生成链
        self.chain = self.prompt | self.model | StrOutputParser()
    
    def generate_hypothetical_answer(self, question: str) -> str:
        """
        生成假设性答案
        
        Args:
            question: 用户问题
            
        Returns:
            假设答案
        """
        try:
            hypothetical_answer = self.chain.invoke({"question": question})
            logger.info(f"HyDE生成假设答案: {hypothetical_answer[:100]}...")
            return hypothetical_answer
            
        except Exception as e:
            logger.error(f"HyDE生成失败: {e}")
            return question


class AdvancedRetriever:
    """高级检索器 - 整合MQE和HyDE"""
    
    def __init__(self, base_retriever):
        """
        Args:
            base_retriever: 基础向量检索器
        """
        self.base_retriever = base_retriever
        self.config = agent_conf.get("retrieval", {})
        
        # 初始化MQE和HyDE
        self.use_multi_query = self.config.get("use_multi_query", True)
        self.use_hyde = self.config.get("use_hyde", True)
        
        if self.use_multi_query:
            num_queries = self.config.get("num_queries", 3)
            self.mq_expander = MultiQueryExpansion(num_queries=num_queries)
            logger.info("启用多查询扩展(MQE)")
        
        if self.use_hyde:
            self.hyde_retriever = HyDERetriever()
            logger.info("启用假设文档嵌入(HyDE)")
    
    def retrieve(self, question: str) -> List[Document]:
        """
        执行高级检索
        
        Args:
            question: 用户问题
            
        Returns:
            检索到的文档列表
        """
        all_docs = []
        
        # 策略1: 使用HyDE
        if self.use_hyde:
            try:
                hypothetical_answer = self.hyde_retriever.generate_hypothetical_answer(question)
                hyde_docs = self.base_retriever.invoke(hypothetical_answer)
                all_docs.extend(hyde_docs)
                logger.info(f"HyDE检索到 {len(hyde_docs)} 个文档")
            except Exception as e:
                logger.error(f"HyDE检索失败: {e}")
        
        # 策略2: 使用多查询扩展
        if self.use_multi_query:
            try:
                queries = self.mq_expander.generate_queries(question)
                for query in queries:
                    docs = self.base_retriever.invoke(query)
                    all_docs.extend(docs)
                logger.info(f"MQE检索到 {len(all_docs)} 个文档（含重复）")
            except Exception as e:
                logger.error(f"MQE检索失败: {e}")
        
        # 如果都未启用，使用基础检索
        if not self.use_hyde and not self.use_multi_query:
            all_docs = self.base_retriever.invoke(question)
        
        # 去重（基于page_content）
        unique_docs = self._deduplicate_documents(all_docs)
        logger.info(f"去重后保留 {len(unique_docs)} 个文档")
        
        # 可选：重排序
        if self.config.get("rerank_enabled", False):
            unique_docs = self._rerank_documents(unique_docs, question)
        
        return unique_docs
    
    def _deduplicate_documents(self, documents: List[Document]) -> List[Document]:
        """去重文档"""
        seen = set()
        unique_docs = []
        
        for doc in documents:
            content_hash = hash(doc.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_docs.append(doc)
        
        return unique_docs
    
    def _rerank_documents(self, documents: List[Document], question: str) -> List[Document]:
        """
        重排序文档（简单实现：基于关键词匹配）
        可以集成更复杂的重排序模型
        """
        # 简单的关键词匹配评分
        keywords = set(question.lower().split())
        
        scored_docs = []
        for doc in documents:
            content_lower = doc.page_content.lower()
            score = sum(1 for kw in keywords if kw in content_lower)
            scored_docs.append((score, doc))
        
        # 按分数降序排序
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for _, doc in scored_docs]
