"""任务实体模块
定义系统中所有任务的标准化数据结构
"""
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import uuid


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskEntity:
    """任务实体类"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str = ""
    task_description: str = ""
    task_type: str = "general"
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    creator: str = "system"
    executor: Optional[str] = None
    assigned_to: Optional[str] = None
    parent_task_id: Optional[str] = None
    sub_tasks: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status.value,
            "priority": self.priority.value
        }
    
    def update_status(self, new_status: TaskStatus) -> None:
        """更新任务状态"""
        self.status = new_status
        self.updated_at = datetime.now()


task_entity = TaskEntity()