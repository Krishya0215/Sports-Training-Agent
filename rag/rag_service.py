"""
RAG总结服务：用户提问，搜索参考资料，将用户提问和参考资料提交给模型，让模型给出总结概括
"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model

def print_prompt(prompt):
    print("-" * 20)
    print(prompt.to_string())
    print("-" * 20)
    return prompt

class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService() # 向量存储服务
        self.retriever = self.vector_store.get_retriever() # 向量检索器
        self.prompt_text = load_rag_prompt() # 提示词文本
        self.prompt_template = PromptTemplate.from_template(self.prompt_text) # 提示词模版
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        """
        初始化链
        :return:
        """
        # chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain


    def retrieve_docs(self, query: str) -> list[Document]:
        """
        根据用户提问检索参考资料
        :param query: 用户提问
        :return: 参考资料
        """
        return self.retriever.invoke(query) # 调用向量检索器，获取参考资料


    def rag_summarize(self, query: str) -> str:
        """
        RAG总结
        :param query: 用户提问
        :return: 总结
        """
        docs = self.retrieve_docs(query)
        context = ""
        cnt = 0
        for doc in docs:
            cnt += 1
            context += f"\n【参考资料{cnt}】：{doc.page_content} [资料元数据]：{doc.metadata} \n"

        return self.chain.invoke({"input": query, "context": context})



if __name__ == "__main__":
    rag_service = RagSummarizeService()
    print(rag_service.rag_summarize("小户型适合哪些扫地机器人"))