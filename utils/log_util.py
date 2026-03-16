"""日志工具模块
提供统一的日志管理功能
"""
import logging
import os
from datetime import datetime
from typing import Optional


class LogUtil:
    """日志工具类"""
    
    _instances = {}
    
    def __init__(self, name: str = "default", log_dir: Optional[str] = None,
                 level: int = logging.INFO):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 可选：创建文件处理器
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(
                    log_dir,
                    f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
                )
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    @classmethod
    def get_instance(cls, name: str = "default", log_dir: Optional[str] = None):
        """获取单例实例
        
        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录
            
        Returns:
            LogUtil 单例实例
        """
        if name not in cls._instances:
            cls._instances[name] = LogUtil(name, log_dir)
        return cls._instances[name]
    
    def debug(self, msg: str) -> None:
        """调试日志"""
        self.logger.debug(msg)
    
    def info(self, msg: str) -> None:
        """信息日志"""
        self.logger.info(msg)
    
    def warning(self, msg: str) -> None:
        """警告日志"""
        self.logger.warning(msg)
    
    def error(self, msg: str) -> None:
        """错误日志"""
        self.logger.error(msg)
    
    def critical(self, msg: str) -> None:
        """严重错误日志"""
        self.logger.critical(msg)
    
    def exception(self, msg: str) -> None:
        """异常日志"""
        self.logger.exception(msg)


def get_logger(name: str = "default", log_dir: Optional[str] = None) -> logging.Logger:
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        
    Returns:
        logging.Logger 实例
    """
    log_util = LogUtil.get_instance(name, log_dir)
    return log_util.logger


# 默认日志记录器
default_logger = get_logger("agent_team")