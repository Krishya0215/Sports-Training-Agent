"""
日志工具
"""
import os
import logging
from datetime import datetime

from backend.utils.path_tool import get_abs_path

# 日志保存的绝对路径
LOG_DIR = get_abs_path("logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志格式
LOGGER_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None
) -> logging.Logger:
    # 创建日志对象
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(LOGGER_FORMAT)
    logger.addHandler(console_handler)

    # 文件Handler
    if not log_file:
        log_file = os.path.join(LOG_DIR, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(LOGGER_FORMAT)
    logger.addHandler(file_handler)

    return logger

logger = get_logger()

if __name__ == "__main__":
    logger.info("hello world")
    logger.error("hello world")
    logger.debug("hello world")
    logger.warning("hello world")