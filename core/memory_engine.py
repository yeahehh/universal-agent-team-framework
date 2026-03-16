"""记忆引擎模块
负责管理和存储 Agent 团队的记忆数据
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import OrderedDict
import threading
import logging


logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: Any
    memory_type: str = "short_term"
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at


class MemoryEngine:
    """记忆引擎类"""
    
    def __init__(self, max_short_term_size: int = 1000, max_long_term_size: int = 10000):
        self._short_term: OrderedDict[str, MemoryEntry] = OrderedDict()
        self._long_term: Dict[str, MemoryEntry] = {}
        self._working_memory: Dict[str, Any] = {}
        self._max_short_term_size = max_short_term_size
        self._max_long_term_size = max_long_term_size
        self._lock = threading.RLock()
    
    def set_short_term(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """设置短期记忆"""
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds else None
            entry = MemoryEntry(key=key, value=value, memory_type="short_term", expires_at=expires_at)
            if key in self._short_term:
                self._short_term.move_to_end(key)
            self._short_term[key] = entry
            if len(self._short_term) > self._max_short_term_size:
                self._short_term.popitem(last=False)
    
    def get_short_term(self, key: str, default: Any = None) -> Any:
        """获取短期记忆"""
        with self._lock:
            if key not in self._short_term:
                return default
            entry = self._short_term[key]
            if entry.is_expired():
                del self._short_term[key]
                return default
            entry.access_count += 1
            return entry.value
    
    def set_long_term(self, key: str, value: Any) -> None:
        """设置长期记忆"""
        with self._lock:
            entry = MemoryEntry(key=key, value=value, memory_type="long_term")
            self._long_term[key] = entry
    
    def get_long_term(self, key: str, default: Any = None) -> Any:
        """获取长期记忆"""
        with self._lock:
            if key not in self._long_term:
                return default
            return self._long_term[key].value
    
    def set_working_memory(self, key: str, value: Any) -> None:
        """设置工作记忆"""
        self._working_memory[key] = value
    
    def get_working_memory(self, key: str, default: Any = None) -> Any:
        """获取工作记忆"""
        return self._working_memory.get(key, default)
    
    def clear_working_memory(self) -> None:
        """清空工作记忆"""
        self._working_memory.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "short_term_count": len(self._short_term),
            "long_term_count": len(self._long_term),
            "working_memory_count": len(self._working_memory)
        }


memory_engine = MemoryEngine()