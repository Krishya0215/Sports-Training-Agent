"""
智能文档处理模块 - 使用MarkItDown处理多模态PDF
"""
import os
from typing import List, Dict, Any
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from utils.logger_handler import logger
from utils.config_handler import chroma_conf

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    logger.warning("MarkItDown未安装，将使用基础PDF处理")


class DocumentProcessor:
    """智能文档处理器 - 支持多模态PDF转Markdown"""
    
    def __init__(self):
        self.use_markitdown = chroma_conf.get("document_processing", {}).get("use_markitdown", False)
        self.extract_images = chroma_conf.get("document_processing", {}).get("extract_images", True)
        
        if self.use_markitdown and MARKITDOWN_AVAILABLE:
            self.markitdown = MarkItDown()
            logger.info("使用MarkItDown进行文档处理")
        else:
            self.markitdown = None
            logger.info("使用基础文档处理")
        
        # Markdown结构化分割器
        self.md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )
        
        # 递归字符分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len
        )
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """
        处理PDF文件，转换为Markdown并分块
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            Document列表
        """
        try:
            if self.markitdown:
                return self._process_with_markitdown(file_path)
            else:
                return self._process_with_pypdf(file_path)
        except Exception as e:
            logger.error(f"处理PDF文件失败 {file_path}: {e}")
            return []
    
    def _process_with_markitdown(self, file_path: str) -> List[Document]:
        """使用MarkItDown处理PDF"""
        try:
            # 转换PDF到Markdown
            result = self.markitdown.convert(file_path)
            markdown_content = result.text_content
            
            if not markdown_content:
                logger.warning(f"MarkItDown转换结果为空: {file_path}")
                return []
            
            # 基于Markdown结构分割
            md_docs = self.md_splitter.split_text(markdown_content)
            
            # 进一步分割过大的块
            documents = []
            for doc in md_docs:
                if len(doc.page_content) > chroma_conf["chunk_size"]:
                    sub_docs = self.text_splitter.split_documents([doc])
                    documents.extend(sub_docs)
                else:
                    documents.append(doc)
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "file_name": Path(file_path).name,
                    "processing_method": "markitdown",
                    "content_type": "multimodal_pdf"
                })
            
            logger.info(f"MarkItDown处理完成: {file_path}, 生成 {len(documents)} 个文档块")
            return documents
            
        except Exception as e:
            logger.error(f"MarkItDown处理失败 {file_path}: {e}")
            return self._process_with_pypdf(file_path)
    
    def _process_with_pypdf(self, file_path: str) -> List[Document]:
        """使用PyPDF处理PDF（备用方案）"""
        try:
            from langchain_community.document_loaders import PyPDFLoader
            
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # 分割文档
            documents = self.text_splitter.split_documents(pages)
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "file_name": Path(file_path).name,
                    "processing_method": "pypdf",
                    "content_type": "pdf"
                })
            
            logger.info(f"PyPDF处理完成: {file_path}, 生成 {len(documents)} 个文档块")
            return documents
            
        except Exception as e:
            logger.error(f"PyPDF处理失败 {file_path}: {e}")
            return []
    
    def process_markdown(self, file_path: str) -> List[Document]:
        """处理Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基于Markdown结构分割
            md_docs = self.md_splitter.split_text(content)
            
            # 进一步分割
            documents = []
            for doc in md_docs:
                if len(doc.page_content) > chroma_conf["chunk_size"]:
                    sub_docs = self.text_splitter.split_documents([doc])
                    documents.extend(sub_docs)
                else:
                    documents.append(doc)
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "file_name": Path(file_path).name,
                    "content_type": "markdown"
                })
            
            logger.info(f"Markdown处理完成: {file_path}, 生成 {len(documents)} 个文档块")
            return documents
            
        except Exception as e:
            logger.error(f"Markdown处理失败 {file_path}: {e}")
            return []
    
    def process_text(self, file_path: str) -> List[Document]:
        """处理纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc = Document(page_content=content, metadata={"source": file_path})
            documents = self.text_splitter.split_documents([doc])
            
            for doc in documents:
                doc.metadata.update({
                    "file_name": Path(file_path).name,
                    "content_type": "text"
                })
            
            logger.info(f"文本处理完成: {file_path}, 生成 {len(documents)} 个文档块")
            return documents
            
        except Exception as e:
            logger.error(f"文本处理失败 {file_path}: {e}")
            return []
