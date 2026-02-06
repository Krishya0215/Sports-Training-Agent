"""
模型工厂
"""
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from utils.config_handler import rag_conf
from dotenv import load_dotenv

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
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


class ChatModelFactory(BaseModelFactory):
    """
    聊天模型工厂
    """
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=rag_conf["chat_model_name"])


embedding_model = EmbeddingModelFactory().generator()
chat_model = ChatModelFactory().generator()