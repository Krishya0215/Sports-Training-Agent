"""
提示词加载工具
"""
from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


def load_prompt_by_key(key: str) -> str:
    """
    根据配置键加载提示词
    
    Args:
        key: 配置文件中的键名
        
    Returns:
        提示词内容
    """
    try:
        if key not in prompts_conf:
            logger.error(f"【加载提示词错误】配置中不存在键: {key}")
            raise KeyError(f"配置中不存在键: {key}")
        
        prompt_path = get_abs_path(prompts_conf[key])
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"【加载提示词错误】{key}: {e}")
        raise e


def load_system_prompt():
    """加载系统提示词（兼容旧代码）"""
    return load_prompt_by_key("system_prompt_path")


def load_rag_prompt():
    """加载RAG提示词（兼容旧代码）"""
    try:
        return load_prompt_by_key("rag_summarize_prompt_path")
    except KeyError:
        # 尝试新的配置键
        return load_prompt_by_key("rag_qa_prompt")


def load_report_prompt():
    """加载报告提示词（兼容旧代码）"""
    return load_prompt_by_key("report_prompt_path")


if __name__ == "__main__":
    print(load_system_prompt())
    print(load_rag_prompt())
    print(load_report_prompt())
