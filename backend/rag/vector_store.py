"""
向量存储服务 - 升级版，支持智能文档处理
"""
from langchain_chroma import Chroma
from backend.utils.config_handler import chroma_conf
from backend.model.factory import embedding_model
from backend.utils.file_handler import listdir_with_allowed_type, get_file_md5_hex, check_md5, save_md5
from backend.utils.logger_handler import logger
from backend.utils.path_tool import get_abs_path
from backend.rag.document_processor import DocumentProcessor

class VectorStoreService:
    def __init__(self):
        # 初始化向量存储（使用绝对路径）
        persist_dir = get_abs_path(chroma_conf["persist_directory"])
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embedding_model,
            persist_directory=persist_dir
        )

        # 初始化文档处理器
        self.doc_processor = DocumentProcessor()


    def get_retriever(self):
        """
        获取向量存储的检索器
        :return: 向量存储的检索器
        """
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})


    def load_documents(self):
        """
        从数据文件夹内读取知识库的数据文件，使用智能文档处理器处理
        并且要计算文件的md5值实现去重功能
        """
        knowledge_files = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]), 
            tuple(chroma_conf["allowed_knowledge_file_types"])
        )
        
        for file_path in knowledge_files:
            # 先用md5值来校验文件是否存在（去重）
            md5_hex = get_file_md5_hex(file_path)
            if check_md5(md5_hex):
                logger.info(f"【载入文件到知识库】{file_path}的内容已经存在于知识库中，跳过")
                continue

            # 使用智能文档处理器处理文件
            try:
                documents = []
                
                if file_path.endswith(".pdf"):
                    documents = self.doc_processor.process_pdf(file_path)
                elif file_path.endswith(".md"):
                    documents = self.doc_processor.process_markdown(file_path)
                elif file_path.endswith(".txt"):
                    documents = self.doc_processor.process_text(file_path)
                else:
                    logger.warning(f"【载入文件到知识库】不支持的文件类型: {file_path}")
                    continue
                
                if not documents:
                    logger.error(f"【载入文件到知识库】{file_path}处理后没有有效内容")
                    continue

                # 将文档添加到向量数据库中
                self.vector_store.add_documents(documents)

                # 保存文件的md5值，维护去重功能
                save_md5(md5_hex)

                logger.info(f"【载入文件到知识库】{file_path}加载成功，共{len(documents)}个文档块")

            except Exception as e:
                logger.error(f"【载入文件到知识库】{file_path}加载失败: {e}")
                continue

if __name__ == "__main__":
    vector_store_service = VectorStoreService()
    vector_store_service.load_documents()
    retriever = vector_store_service.get_retriever()
    res = retriever.invoke("迷路")
    for doc in res:
        print(doc.page_content)
        print("-" * 20)