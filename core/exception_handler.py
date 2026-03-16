"""异常处理模块
负责系统中所有异常的捕获、记录和报告
"""
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import traceback


logger = logging.getLogger(__name__)


@dataclass
class ExceptionInfo:
    """异常信息类"""
    exception_type: str
    message: str
    traceback_str: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


class ExceptionHandler:
    """异常处理器"""
    
    def __init__(self):
        self._history: list = []
    
    def handle(self, exc: Exception, context: Optional[Dict[str, Any]] = None) -> ExceptionInfo:
        """处理异常"""
        info = ExceptionInfo(
            exception_type=type(exc).__name__,
            message=str(exc),
            traceback_str=traceback.format_exc(),
            context=context or {}
        )
        self._history.append(info)
        logger.error(f"异常：{info.exception_type} - {info.message}")
        return info
    
    def get_history(self, limit: int = 10) -> list:
        """获取异常历史"""
        return self._history[-limit:]
    
    def clear_history(self) -> None:
        """清空异常历史"""
        self._history.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {"total_exceptions": len(self._history)}


exception_handler = ExceptionHandler()