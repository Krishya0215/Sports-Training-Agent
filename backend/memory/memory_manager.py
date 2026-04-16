"""
多层次记忆管理模块
- 工作记忆：管理当前任务和上下文
- 情景记忆：记录学习事件和查询历史
- 语义记忆：存储概念知识和理解
- 感知记忆：处理文档特征和多模态信息
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.model.factory import chat_model
from backend.utils.logger_handler import logger
from backend.utils.config_handler import agent_conf
from backend.utils.prompt_loader import load_prompt_by_key


class WorkingMemory:
    """工作记忆 - 管理当前对话上下文"""
    
    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self.messages: deque = deque(maxlen=max_size * 2)  # 每轮包含问答两条消息
        logger.info(f"工作记忆初始化，容量: {max_size}轮对话")
    
    def add_message(self, role: str, content: str):
        """添加消息到工作记忆"""
        if role == "human":
            self.messages.append(HumanMessage(content=content))
        elif role == "ai":
            self.messages.append(AIMessage(content=content))
        
        logger.debug(f"工作记忆添加消息: {role}")
    
    def get_messages(self) -> List[BaseMessage]:
        """获取所有消息"""
        return list(self.messages)
    
    def get_context_string(self) -> str:
        """获取格式化的上下文字符串"""
        context = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                context.append(f"用户: {msg.content}")
            elif isinstance(msg, AIMessage):
                context.append(f"助手: {msg.content}")
        return "\n".join(context)
    
    def clear(self):
        """清空工作记忆"""
        self.messages.clear()
        logger.info("工作记忆已清空")


class EpisodicMemory:
    """情景记忆 - 记录查询历史和学习事件"""
    
    def __init__(self):
        self.episodes: List[Dict[str, Any]] = []
        logger.info("情景记忆初始化")
    
    def add_episode(self, question: str, answer: str, retrieved_docs: List[str], 
                   metadata: Optional[Dict] = None):
        """记录一次问答情景"""
        episode = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "retrieved_docs": retrieved_docs,
            "metadata": metadata or {}
        }
        self.episodes.append(episode)
        logger.debug(f"情景记忆记录: {question[:50]}...")
    
    def get_recent_episodes(self, n: int = 5) -> List[Dict[str, Any]]:
        """获取最近的N个情景"""
        return self.episodes[-n:]
    
    def search_episodes(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索包含关键词的情景"""
        results = []
        for episode in self.episodes:
            if keyword.lower() in episode["question"].lower() or \
               keyword.lower() in episode["answer"].lower():
                results.append(episode)
        return results
    
    def get_all_episodes(self) -> List[Dict[str, Any]]:
        """获取所有情景"""
        return self.episodes


class SemanticMemory:
    """语义记忆 - 存储概念知识和理解"""
    
    def __init__(self):
        self.concepts: Dict[str, Any] = {}
        self.relationships: List[Dict[str, str]] = []
        logger.info("语义记忆初始化")
    
    def add_concept(self, concept: str, definition: str, examples: Optional[List[str]] = None):
        """添加概念"""
        self.concepts[concept] = {
            "definition": definition,
            "examples": examples or [],
            "created_at": datetime.now().isoformat()
        }
        logger.debug(f"语义记忆添加概念: {concept}")
    
    def add_relationship(self, concept1: str, relation: str, concept2: str):
        """添加概念关系"""
        self.relationships.append({
            "from": concept1,
            "relation": relation,
            "to": concept2
        })
        logger.debug(f"语义记忆添加关系: {concept1} {relation} {concept2}")
    
    def get_concept(self, concept: str) -> Optional[Dict[str, Any]]:
        """获取概念信息"""
        return self.concepts.get(concept)
    
    def get_related_concepts(self, concept: str) -> List[str]:
        """获取相关概念"""
        related = []
        for rel in self.relationships:
            if rel["from"] == concept:
                related.append(rel["to"])
            elif rel["to"] == concept:
                related.append(rel["from"])
        return list(set(related))


class PerceptualMemory:
    """感知记忆 - 处理文档特征和多模态信息"""
    
    def __init__(self):
        self.document_features: Dict[str, Any] = {}
        self.image_descriptions: Dict[str, str] = {}
        self.image_metadata: Dict[str, Dict[str, Any]] = {}
        logger.info("感知记忆初始化")
    
    def add_document_features(self, doc_id: str, features: Dict[str, Any]):
        """添加文档特征"""
        self.document_features[doc_id] = {
            "features": features,
            "timestamp": datetime.now().isoformat()
        }
        logger.debug(f"感知记忆添加文档特征: {doc_id}")
    
    def add_image_description(self, image_id: str, description: str, metadata: Optional[Dict[str, Any]] = None):
        """
        添加图像描述
        
        Args:
            image_id: 图像唯一标识
            description: 图像的文本描述
            metadata: 图像元数据（来源、页码、模型等）
        """
        self.image_descriptions[image_id] = description
        if metadata:
            self.image_metadata[image_id] = {
                **metadata,
                "timestamp": datetime.now().isoformat()
            }
        logger.debug(f"感知记忆添加图像描述: {image_id}")
    
    def get_document_features(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取文档特征"""
        return self.document_features.get(doc_id)
    
    def get_image_description(self, image_id: str) -> Optional[str]:
        """获取图像描述"""
        return self.image_descriptions.get(image_id)
    
    def get_image_metadata(self, image_id: str) -> Optional[Dict[str, Any]]:
        """获取图像元数据"""
        return self.image_metadata.get(image_id)
    
    def get_all_image_descriptions(self) -> Dict[str, str]:
        """获取所有图像描述"""
        return self.image_descriptions
    
    def search_images_by_source(self, source: str) -> List[Dict[str, Any]]:
        """
        根据来源文档搜索图像
        
        Args:
            source: 文档来源路径
            
        Returns:
            匹配的图像信息列表
        """
        results = []
        for image_id, metadata in self.image_metadata.items():
            if metadata.get("source") == source:
                results.append({
                    "image_id": image_id,
                    "description": self.image_descriptions.get(image_id),
                    "metadata": metadata
                })
        return results


class MemoryManager:
    """统一记忆管理器"""
    
    def __init__(self):
        config = agent_conf.get("memory", {})
        
        # 初始化各层记忆
        working_memory_size = config.get("working_memory_size", 5)
        self.working_memory = WorkingMemory(max_size=working_memory_size)
        
        if config.get("episodic_memory_enabled", True):
            self.episodic_memory = EpisodicMemory()
        else:
            self.episodic_memory = None
        
        if config.get("semantic_memory_enabled", True):
            self.semantic_memory = SemanticMemory()
        else:
            self.semantic_memory = None
        
        if config.get("perceptual_memory_enabled", True):
            self.perceptual_memory = PerceptualMemory()
        else:
            self.perceptual_memory = None
        
        logger.info("记忆管理器初始化完成")
    
    def record_interaction(self, question: str, answer: str, 
                          retrieved_docs: Optional[List[str]] = None,
                          metadata: Optional[Dict] = None):
        """记录一次完整的交互"""
        # 工作记忆
        self.working_memory.add_message("human", question)
        self.working_memory.add_message("ai", answer)
        
        # 情景记忆
        if self.episodic_memory:
            self.episodic_memory.add_episode(
                question=question,
                answer=answer,
                retrieved_docs=retrieved_docs or [],
                metadata=metadata
            )
        
        # 感知记忆 - 记录文档特征
        if self.perceptual_memory and metadata:
            # 提取图像相关信息
            if "image_descriptions" in metadata:
                for img_info in metadata["image_descriptions"]:
                    self.perceptual_memory.add_image_description(
                        image_id=img_info.get("image_id"),
                        description=img_info.get("description"),
                        metadata=img_info.get("metadata")
                    )
        
        logger.info("交互记录完成")
    
    def get_context_for_query(self) -> str:
        """获取用于查询的上下文"""
        return self.working_memory.get_context_string()
    
    def summarize_memory(self) -> Dict[str, Any]:
        """总结记忆状态"""
        summary = {
            "working_memory_size": len(self.working_memory.messages),
            "episodic_memory_size": len(self.episodic_memory.episodes) if self.episodic_memory else 0,
            "semantic_concepts": len(self.semantic_memory.concepts) if self.semantic_memory else 0,
            "perceptual_documents": len(self.perceptual_memory.document_features) if self.perceptual_memory else 0,
            "perceptual_images": len(self.perceptual_memory.image_descriptions) if self.perceptual_memory else 0
        }
        return summary
