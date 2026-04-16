"""
文件处理工具类
"""
import os, hashlib
from backend.utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from backend.utils.path_tool import get_abs_path
from backend.utils.config_handler import chroma_conf


def get_file_md5_hex(file_path: str):
    """获取文件的md5的16进制字符串"""
    if not os.path.exists(file_path):
        logger.error(f"【md5计算错误】文件不存在: {file_path}")
        return None

    if not os.path.isfile(file_path):
        logger.error(f"【md5计算错误】{file_path}不是文件")
        return None

    md5_obj = hashlib.md5()

    chunk_size = 4096  # 4KB分片，避免文件过大导致内存溢出
    try:
        with open(file_path, "rb") as f: # 必须使用二进制模式打开文件
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        md5_hex = md5_obj.hexdigest()
        return md5_hex
    except Exception as e:
        logger.error(f"【md5计算错误】{file_path} {e}")
        return None

def check_md5(md5_str: str) -> bool:
    """检查传入的md5值是否已经存在于md5文件中"""
    md5_file = get_abs_path(chroma_conf["md5_file"])
    # 如果文件不存在
    if not os.path.exists(md5_file):
        # 创建文件
        open(md5_file, "w", encoding="utf-8").close()
        return False

    # 否则打开文件
    with open(md5_file, "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            # 如果md5值已经存在
            if md5_str == line:
                return True

        return False

def save_md5(md5_str: str):
    """保存md5值到md5文件中"""
    md5_file = get_abs_path(chroma_conf["md5_file"])
    with open(md5_file, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n")

def remove_md5(md5_str: str) -> bool:
    """从md5文件中删除指定的md5值"""
    md5_file = get_abs_path(chroma_conf["md5_file"])

    if not os.path.exists(md5_file):
        return False

    try:
        with open(md5_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 过滤掉要删除的md5值
        new_lines = [line for line in lines if line.strip() != md5_str]

        # 重写文件
        with open(md5_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        return True
    except Exception as e:
        logger.error(f"【md5删除错误】{e}")
        return False

def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """
    列出指定目录下的文件，并筛选出指定类型的文件
    :param path: 目录路径
    :param allowed_types: 允许的文件类型，如：(".txt", ".pdf")
    :return: 筛选后的文件列表
    """
    files = []
    if not os.path.exists(path):
        logger.error(f"【文件列表错误】目录不存在: {path}")
        return files

    if not os.path.isdir(path):
        logger.error(f"【文件列表错误】不是目录: {path}")
        return files

    for file in os.listdir(path):
        if file.endswith(allowed_types):
            files.append(os.path.join(path, file))

    return tuple(files) # 转为元组，避免被修改


def pdf_loader(file_path: str, passwd=None) -> list[Document]:
    """pdf文件加载器"""
    return PyPDFLoader(file_path, passwd).load()


def txt_loader(file_path: str) -> list[Document]:
    """txt文件加载器"""
    return TextLoader(file_path, encoding="utf-8").load()