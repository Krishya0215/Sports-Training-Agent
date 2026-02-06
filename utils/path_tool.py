"""
为整个工程提供统一的绝对路径
"""
import os

def get_project_root():
    """
    获取项目所在的根目录
    :return:根目录字符串
    """
    # 获取当前文件所在的目录
    cur_abs_path = os.path.abspath(__file__)
    cur_dir = os.path.dirname(cur_abs_path)
    # 获取项目所在的根目录
    return os.path.dirname(cur_dir)


def get_abs_path(relative_path: str) -> str:
    """
    获取绝对路径
    :param relative_path: 相对路径
    :return: 绝对路径字符串
    """
    return os.path.join(get_project_root(), relative_path)