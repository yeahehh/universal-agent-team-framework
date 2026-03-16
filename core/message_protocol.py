"""消息协议模块
定义系统中所有消息的标准化格式和协议
"""
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import uuid
import json


class MessageType(Enum):
    """消息类型枚举"""
    TASK_CREATE = "task_create"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    TASK_CANCEL = "task_cancel"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    AGENT_REGISTER = "agent_register"
    AGENT_UNREGISTER = "agent_unregister"
    AGENT_STATUS = "agent_status"
    SYSTEM = "system"
    ERROR = "error"
    LOG = "log"


class MessagePriority(Enum):
    """消息优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class MessageStatus(Enum):
    """消息状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass
class Message:
    """消息类"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    sender: Optional[str] = None
    receiver: Optional[str] = None
    subject: str = ""
    content: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "sender": self.sender
        }
    
    def mark_sent(self) -> None:
        """标记为已发送"""
        self.status = MessageStatus.SENT
    
    def mark_delivered(self) -> None:
        """标记为已投递"""
        self.status = MessageStatus.DELIVERED
    
    def mark_failed(self) -> None:
        """标记为失败"""
        self.status = MessageStatus.FAILED


message_protocol = Message()