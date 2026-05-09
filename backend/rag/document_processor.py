"""
智能文档处理模块 - 使用MarkItDown处理多模态PDF
"""
import os
import re
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from backend.utils.logger_handler import logger
from backend.utils.config_handler import chroma_conf

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    logger.warning("MarkItDown未安装，将使用基础PDF处理")

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("pytesseract/pdf2image未安装，OCR功能不可用")

try:
    from backend.model.multimodal_model import multimodal_llm
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    logger.warning("多模态模型未配置，图像描述功能将被禁用")


class DocumentProcessor:
    """智能文档处理器 - 支持多模态PDF转Markdown"""
    
    def __init__(self):
        self.use_markitdown = chroma_conf.get("document_processing", {}).get("use_markitdown", False)
        self.extract_images = chroma_conf.get("document_processing", {}).get("extract_images", True)
        self.image_description_enabled = chroma_conf.get("document_processing", {}).get("image_description_enabled", True)
        
        if self.use_markitdown and MARKITDOWN_AVAILABLE:
            self.markitdown = MarkItDown()
            logger.info("使用MarkItDown进行文档处理")
        else:
            self.markitdown = None
            logger.info("使用基础文档处理")
        
        # 图像输出目录
        self.image_output_dir = Path("data/extracted_images")
        self.image_output_dir.mkdir(parents=True, exist_ok=True)
        
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
                logger.warning(f"MarkItDown转换结果为空，回退到PyPDF: {file_path}")
                return self._process_with_pypdf(file_path)
            
            # 提取图像并生成描述
            image_docs = []
            if self.extract_images and self.image_description_enabled and MULTIMODAL_AVAILABLE:
                image_docs = self._extract_and_describe_images(file_path, markdown_content)
            
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
            
            # 合并文本文档和图像描述文档
            all_documents = documents + image_docs
            
            logger.info(f"MarkItDown处理完成: {file_path}, 生成 {len(documents)} 个文本块, {len(image_docs)} 个图像描述")
            return all_documents
            
        except Exception as e:
            logger.error(f"MarkItDown处理失败 {file_path}: {e}")
            return self._process_with_pypdf(file_path)
    
    def _process_with_pypdf(self, file_path: str) -> List[Document]:
        """使用PyPDF处理PDF（备用方案）"""
        try:
            from langchain_community.document_loaders import PyPDFLoader

            loader = PyPDFLoader(file_path)
            pages = loader.load()

            # 检查是否提取到有效文本（扫描版PDF文字层为空）
            total_text = "".join(p.page_content.strip() for p in pages)
            if not total_text and OCR_AVAILABLE:
                logger.info(f"PyPDF未提取到文本，尝试OCR: {file_path}")
                return self._process_with_ocr(file_path)

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

    def _process_with_ocr(self, file_path: str) -> List[Document]:
        """使用 OCR（tesseract）处理扫描版 PDF"""
        try:
            logger.info(f"开始 OCR 处理: {file_path}")
            # 将 PDF 每页渲染为图像
            images = convert_from_path(file_path, dpi=200)
            logger.info(f"PDF 共 {len(images)} 页，开始逐页 OCR...")

            all_text_parts = []
            for i, img in enumerate(images):
                text = pytesseract.image_to_string(img, lang="chi_sim+eng")
                text = text.strip()
                if text:
                    all_text_parts.append(text)
                if (i + 1) % 20 == 0:
                    logger.info(f"  OCR 进度: {i+1}/{len(images)} 页")

            full_text = "\n\n".join(all_text_parts)
            if not full_text.strip():
                logger.error(f"OCR 未提取到任何文本: {file_path}")
                return []

            # 分块
            chunks = self.text_splitter.split_text(full_text)
            documents = [
                Document(
                    page_content=chunk,
                    metadata={
                        "source": file_path,
                        "file_name": Path(file_path).name,
                        "processing_method": "ocr_tesseract",
                        "content_type": "scanned_pdf"
                    }
                )
                for chunk in chunks
            ]

            logger.info(f"OCR 处理完成: {file_path}, 生成 {len(documents)} 个文档块")
            return documents

        except Exception as e:
            logger.error(f"OCR 处理失败 {file_path}: {e}")
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
    
    def _extract_and_describe_images(self, pdf_path: str, markdown_content: str) -> List[Document]:
        """
        从PDF中提取图像并生成描述
        
        Args:
            pdf_path: PDF文件路径
            markdown_content: 转换后的Markdown内容
            
        Returns:
            图像描述文档列表
        """
        image_documents = []
        
        try:
            # 使用PyMuPDF提取图像
            import fitz  # PyMuPDF
            
            pdf_document = fitz.open(pdf_path)
            pdf_name = Path(pdf_path).stem
            
            # 为当前PDF创建图像目录
            pdf_image_dir = self.image_output_dir / pdf_name
            pdf_image_dir.mkdir(parents=True, exist_ok=True)
            
            image_count = 0
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # 保存图像
                        image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                        image_path = pdf_image_dir / image_filename
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # 生成图像描述
                        if MULTIMODAL_AVAILABLE:
                            result = multimodal_llm.generate_image_description(
                                str(image_path),
                                detail_level="detailed"
                            )
                            
                            if result["success"]:
                                # 创建图像描述文档
                                image_doc = Document(
                                    page_content=f"[图像描述] {result['description']}",
                                    metadata={
                                        "source": pdf_path,
                                        "file_name": Path(pdf_path).name,
                                        "content_type": "image_description",
                                        "image_path": str(image_path),
                                        "image_filename": image_filename,
                                        "page_number": page_num + 1,
                                        "processing_method": "multimodal_llm",
                                        "model": result["model"]
                                    }
                                )
                                image_documents.append(image_doc)
                                image_count += 1
                                logger.debug(f"图像描述生成: {image_filename}")
                        
                    except Exception as e:
                        logger.warning(f"处理图像失败 (页{page_num + 1}, 图{img_index + 1}): {e}")
                        continue
            
            pdf_document.close()
            logger.info(f"从 {pdf_path} 提取并描述了 {image_count} 张图像")
            
        except ImportError:
            logger.warning("PyMuPDF (fitz) 未安装，无法提取图像。请安装: pip install pymupdf")
        except Exception as e:
            logger.error(f"图像提取失败: {e}")
        
        return image_documents
    
    def get_image_descriptions_for_document(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        获取文档的所有图像描述
        
        Args:
            doc_id: 文档ID或文件名
            
        Returns:
            图像描述列表
        """
        pdf_image_dir = self.image_output_dir / Path(doc_id).stem
        
        if not pdf_image_dir.exists():
            return []
        
        descriptions = []
        for image_file in pdf_image_dir.glob("*"):
            if image_file.is_file():
                descriptions.append({
                    "image_path": str(image_file),
                    "image_name": image_file.name
                })
        
        return descriptions
