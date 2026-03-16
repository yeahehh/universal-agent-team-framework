"""通信总线模块
负责系统中所有组件之间的消息传递和通信
"""
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import threading
import queue
import logging

from .message_protocol import Message, MessageType, MessageStatus


logger = logging.getLogger(__name__)


@dataclass
class Subscriber:
    """订阅者信息"""
    subscriber_id: str
    callback: Callable[[Message], Any]
    message_types: Set[MessageType] = field(default_factory=set)
    is_active: bool = True


class CommunicationBus:
    """通信总线类"""
    
    def __init__(self):
        self._subscribers: Dict[str, Subscriber] = {}
        self._topic_subscribers: Dict[str, Set[str]] = defaultdict(set)
        self._message_queue: queue.Queue = queue.Queue()
        self._lock = threading.RLock()
        self._running = True
    
    def subscribe(self, subscriber_id: str, callback: Callable[[Message], Any], 
                  message_types: Optional[List[MessageType]] = None) -> None:
        """订阅消息"""
        with self._lock:
            types_set = set(message_types) if message_types else set(MessageType)
            subscriber = Subscriber(
                subscriber_id=subscriber_id,
                callback=callback,
                message_types=types_set,
                is_active=True
            )
            self._subscribers[subscriber_id] = subscriber
    
    def unsubscribe(self, subscriber_id: str) -> None:
        """取消订阅"""
        with self._lock:
            if subscriber_id in self._subscribers:
                del self._subscribers[subscriber_id]
    
    def publish(self, message: Message) -> int:
        """发布消息"""
        with self._lock:
            delivered_count = 0
            for subscriber in self._subscribers.values():
                if subscriber.is_active:
                    try:
                        subscriber.callback(message)
                        delivered_count += 1
                    except Exception as e:
                        logger.error(f"投递失败：{e}")
            return delivered_count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {"subscriber_count": len(self._subscribers)}


comm_bus = CommunicationBus()