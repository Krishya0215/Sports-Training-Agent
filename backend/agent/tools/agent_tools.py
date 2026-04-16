"""
AI教练工具库
提供RAG知识库查询和其他辅助工具
"""
from typing import Optional, List
import re
from langchain_core.tools import tool
from backend.rag.vector_store import VectorStoreService
from backend.rag.advanced_retriever import AdvancedRetriever
from backend.utils.logger_handler import logger


class QuestionClassifier:
    """
    问题分类器
    判断用户问题是否属于专业运动训练问题
    """
    
    # 运动训练专业关键词
    PROFESSIONAL_KEYWORDS = {
        # 训练相关
        '训练', '锻炼', '健身', '运动', '训练计划', '训练方案', '健身计划',
        '力量训练', '有氧训练', '耐力训练', '爆发力', '柔韧性',
        '训练强度', '训练频率', '训练方法', '训练技巧', '训练动作',
        
        # 目标相关
        '减脂', '减重', '增肌', '塑形', '体态', '核心', '线条',
        '肌肉', '肌力', '体能', '耐力', '速度', '敏捷',
        
        # 恢复相关
        '恢复', '放松', '拉伸', '瑜伽', '冥想', '睡眠', '营养',
        '蛋白质', '碳水', '脂肪', '热量', '补充剂',
        
        # 伤病相关
        '伤病', '受伤', '疼痛', '酸痛', '肌肉拉伤', '关节', '膝盖', '腰部',
        '肩部', '脚踝', '肘部', '风险', '禁忌', '避免',
        
        # 运动类型
        '跑步', '走路', 'HIIT', '瑜伽', '普拉提', '舞蹈',
        'hiit', '跳绳', '骑车', '游泳', '划船', '椭圆机',
        
        # 生理指标
        '心率', '血压', '血糖', '体重', 'BMI', '体脂', 'VO2',
        
        # 科学方法
        '进度', '数据', '记录', '评估', '测试', '基准', '目标',
    }
    
    # 纯聊天关键词（不需要RAG）
    CHAT_KEYWORDS = {
        '你好', '嗨', '你是谁', '怎么样', '最近', '天气', '今天',
        '感觉', '心情', '聊天', '问候', '谢谢', '再见',
        '在吗', '忙吗', '怎么称呼', '叫什么名字', '来自哪',
    }
    
    @classmethod
    def classify(cls, question: str) -> tuple[str, float]:
        """
        分类问题类型
        
        Args:
            question: 用户问题
            
        Returns:
            (类型, 置信度) - ('professional'|'chat', 0.0-1.0)
        """
        question_lower = question.lower()
        
        # 统计关键词出现次数
        professional_count = sum(1 for kw in cls.PROFESSIONAL_KEYWORDS 
                                if kw in question_lower)
        chat_count = sum(1 for kw in cls.CHAT_KEYWORDS 
                        if kw in question_lower)
        
        # 基于关键词计算置信度
        total = professional_count + chat_count
        
        if professional_count > chat_count:
            confidence = professional_count / (total + 1) if total > 0 else 0.6
            return ('professional', min(confidence, 1.0))
        elif chat_count > 0:
            confidence = chat_count / (total + 1)
            return ('chat', min(confidence, 1.0))
        
        # 默认启发式规则
        # 较长、包含多个句子的通常是专业问题
        if len(question) > 30 and ('？' in question or '?' in question):
            return ('professional', 0.6)
        
        return ('chat', 0.5)
    
    @classmethod
    def should_use_rag(cls, question: str) -> tuple[bool, str, float]:
        """
        判断是否应该使用RAG
        
        Returns:
            (应该使用RAG, 理由, 置信度)
        """
        question_type, confidence = cls.classify(question)
        
        if question_type == 'professional':
            reason = "检测到运动训练相关的专业问题，将启动知识库查询"
            return (True, reason, confidence)
        else:
            reason = "检测到日常聊天问题，直接通过对话模型回复"
            return (False, reason, confidence)


@tool
def query_training_knowledge_base(question: str) -> str:
    """
    运动训练知识库检索工具
    
    功能说明：
    - 从专业运动训练知识库中检索相关文档
    - 支持多查询扩展（MQE）和假设性文档嵌入（HyDE）
    - 返回最相关的训练知识片段
    
    适用场景：
    - 运动训练计划制定
    - 训练方法和技巧咨询
    - 伤病预防和恢复建议
    - 营养补充和恢复策略
    - 进度评估和优化方案
    
    使用示例：
    - "我想增肌，应该如何安排训练"
    - "膝盖疼痛期间可以做哪些训练"
    - "HIIT训练的正确做法"
    
    Args:
        question: 用户的训练相关问题
        
    Returns:
        从知识库检索到的相关信息
    """
    try:
        logger.info(f"🔍 启动RAG知识库检索: {question}")
        
        # 初始化向量存储和检索器
        vector_store_service = VectorStoreService()
        base_retriever = vector_store_service.get_retriever()
        retriever = AdvancedRetriever(base_retriever)
        
        # 检索相关文档
        retrieved_docs = retriever.retrieve(question)
        
        if not retrieved_docs:
            logger.warning("知识库中未找到相关文档")
            return "知识库中暂未找到相关内容，我将基于通用知识为您回答。"
        
        # 格式化检索结果
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.metadata.get("source", "未知来源")
            content = doc.page_content.strip()
            context_parts.append(f"【文档{i}】来源: {source}\n{content}")
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"✓ 成功检索 {len(retrieved_docs)} 个相关文档")
        logger.debug(f"检索结果摘要: {context[:200]}...")
        
        return context
        
    except Exception as e:
        logger.error(f"RAG知识库检索失败: {e}")
        return f"知识库查询出错，我将基于通用知识为您回答。"


@tool
def detect_question_type(question: str) -> str:
    """
    问题类型检测工具
    
    功能说明：
    - 自动识别用户问题是否为专业运动训练问题
    - 评估是否需要调用知识库
    - 提供分类置信度
    
    返回信息：
    - 问题类型 (professional/chat)
    - 分类理由
    - 置信度评分 (0-100%)
    
    Args:
        question: 用户问题
        
    Returns:
        问题类型检测结果
    """
    should_use_rag, reason, confidence = QuestionClassifier.should_use_rag(question)
    
    result = {
        "question": question,
        "should_use_rag": should_use_rag,
        "reason": reason,
        "confidence": f"{confidence*100:.1f}%",
        "question_type": "专业问题" if should_use_rag else "聊天问题"
    }
    
    logger.info(f"问题分类结果: {result}")
    return str(result)


# 导出所有工具
TOOLS = [
    query_training_knowledge_base,
    detect_question_type,
]

__all__ = [
    'QuestionClassifier',
    'query_training_knowledge_base',
    'detect_question_type',
    'TOOLS',
]
