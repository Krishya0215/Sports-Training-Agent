"""
健壮的API调用包装器
处理SSL错误、连接问题和重试逻辑
"""
import asyncio
import time
from typing import Callable, Any
from utils.logger_handler import logger


class APICallError(Exception):
    """API调用错误"""
    pass


async def robust_query_with_retry(
    query_func: Callable,
    question: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> dict:
    """
    健壮的查询函数，支持重试和错误处理
    
    Args:
        query_func: 查询函数
        question: 用户问题
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        backoff_factor: 延迟倍增因子
        
    Returns:
        查询结果字典
    """
    last_error = None
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试查询 (第 {attempt + 1}/{max_retries}): {question[:50]}")
            
            # 调用查询函数
            result = query_func(question)
            
            logger.info(f"查询成功 (第 {attempt + 1} 次尝试)")
            return result
            
        except Exception as e:
            last_error = e
            error_msg = str(e)
            
            # 记录错误
            logger.warning(f"查询失败 (第 {attempt + 1}/{max_retries}): {error_msg[:100]}")
            
            # 检查是否是SSL错误
            if 'SSL' in error_msg or 'ssl' in error_msg.lower():
                logger.error(f"SSL错误: {error_msg}")
                
                # SSL错误通常是暂时的，继续重试
                if attempt < max_retries - 1:
                    wait_time = delay * (backoff_factor ** attempt)
                    logger.info(f"SSL连接失败，{wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
                    continue
            
            # 其他错误也尝试重试
            elif attempt < max_retries - 1:
                wait_time = delay * (backoff_factor ** attempt)
                logger.info(f"请求失败，{wait_time}秒后重试...")
                await asyncio.sleep(wait_time)
                continue
    
    # 所有重试都失败了
    logger.error(f"经过 {max_retries} 次重试后，查询仍然失败")
    
    # 返回包含错误信息的结果
    return {
        "thinking": "❌ **多次重试失败**\n\n系统遇到网络连接问题，可能是：\n1. 暂时网络故障\n2. API服务暂时不可用\n3. SSL/TLS连接问题\n\n请稍候几分钟后重试。",
        "answer": f"抱歉，我现在无法处理您的请求。\n\n错误信息：{str(last_error)[:200]}\n\n请稍候几分钟后重试，或检查网络连接。",
        "error": True,
        "error_msg": str(last_error)
    }


def get_user_friendly_error_message(error: Exception) -> tuple[str, str]:
    """
    将技术错误转换为用户友好的错误消息
    
    Args:
        error: 异常对象
        
    Returns:
        (thinking_msg, answer_msg) 的元组
    """
    error_msg = str(error).lower()
    
    if 'ssl' in error_msg:
        return (
            "❌ **SSL连接错误**\n\n正在尝试重新连接到AI服务...",
            "网络连接出现问题，请稍后重试。"
        )
    elif 'timeout' in error_msg or 'timed out' in error_msg:
        return (
            "❌ **请求超时**\n\nAI服务响应较慢，请稍候...",
            "请求处理超时，请稍后重试。"
        )
    elif 'connection' in error_msg:
        return (
            "❌ **连接错误**\n\n检查网络连接...",
            "网络连接失败，请检查您的网络。"
        )
    else:
        return (
            f"❌ **处理错误**\n\n错误类型：{error_msg[:50]}",
            "处理您的请求时出现错误，请稍后重试。"
        )
