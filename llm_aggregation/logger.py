import logging
import sys
from typing import Optional

from .config import settings


def setup_logger(name: str = "llm_aggregation") -> logging.Logger:
    """
    根据配置设置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    # 获取日志配置
    log_config = settings.logging
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 设置日志级别
    level = getattr(logging, log_config.level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 清除现有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(log_config.format)
    
    # 添加控制台处理器
    if log_config.console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件处理器（如果配置了文件路径）
    if log_config.file:
        file_handler = logging.FileHandler(log_config.file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 创建默认日志记录器
logger = setup_logger()