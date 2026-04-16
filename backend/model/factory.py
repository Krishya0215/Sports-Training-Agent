"""
模型工厂
"""
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from backend.utils.config_handler import rag_conf
from dotenv import load_dotenv
import os

load_dotenv()

class BaseModelFactory(ABC):
    """
    模型工厂抽象类
    """
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """
        生成模型
        """
        pass


class EmbeddingModelFactory(BaseModelFactory):
    """
    嵌入模型工厂
    """
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        try:
            # 检查 API Key 是否存在
            if not os.getenv("DASHSCOPE_API_KEY"):
                print("⚠️  警告: DASHSCOPE_API_KEY 未设置，嵌入模型将在需要时延迟初始化")
                return None
            return DashScopeEmbeddings(
                model=rag_conf["embedding_model_name"],
            )
        except Exception as e:
            print(f"⚠️  警告: 嵌入模型初始化失败 - {e}")
            return None


class ChatModelFactory(BaseModelFactory):
    """
    聊天模型工厂
    支持重试和连接优化
    """
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        try:
            # 检查 API Key 是否存在
            if not os.getenv("DASHSCOPE_API_KEY"):
                print("⚠️  警告: DASHSCOPE_API_KEY 未设置，聊天模型将在需要时延迟初始化")
                return None
            return build_chat_model()
        except Exception as e:
            print(f"⚠️  警告: 聊天模型初始化失败 - {e}")
            return None


def build_chat_model(
    *,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 2048,
    request_timeout: int = 60,
    max_retries: int = 3
) -> Optional[BaseChatModel]:
    """按需构建聊天模型，便于为不同场景设置更轻量的推理参数"""
    if not os.getenv("DASHSCOPE_API_KEY"):
        return None

    return ChatTongyi(
        model=rag_conf["chat_model_name"],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        request_timeout=request_timeout,
        max_retries=max_retries
    )


try:
    embedding_model = EmbeddingModelFactory().generator()
    chat_model = ChatModelFactory().generator()
except Exception as e:
    print(f"⚠️  警告: 模型初始化异常 - {e}")
    embedding_model = None
    chat_model = None
