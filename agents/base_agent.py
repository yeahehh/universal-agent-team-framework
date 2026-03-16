"""Agent 基类模块
定义所有 Agent 的通用属性和方法
"""
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import uuid
import logging

from core import TaskEntity, TaskStatus, Message, MessageType, comm_bus
from utils import get_logger


class AgentStatus(Enum):
    """Agent 状态枚举"""
    IDLE = "idle"              # 空闲
    BUSY = "busy"              # 忙碌
    PAUSED = "paused"          # 暂停
    ERROR = "error"            # 错误
    OFFLINE = "offline"        # 离线


class AgentType(Enum):
    """Agent 类型枚举"""
    MANAGER = "manager"        # 总管
    EXECUTOR = "executor"      # 执行者
    ANALYST = "analyst"        # 分析师
    MONITOR = "monitor"        # 监控者
    CUSTOM = "custom"          # 自定义


class BaseAgent(ABC):
    """
    Agent 基类
    
    所有 Agent 必须继承此类并实现抽象方法
    
    属性:
        agent_id: Agent 唯一标识符
        agent_name: Agent 名称
        agent_type: Agent 类型
        status: Agent 当前状态
        created_at: 创建时间
        description: Agent 描述
        capabilities: Agent 能力列表
        current_task: 当前执行的任务
        task_history: 任务历史列表
        config: Agent 配置字典
        metadata: 元数据
    """
    
    def __init__(self, agent_name: str, agent_type: AgentType,
                 config: Optional[Dict[str, Any]] = None,
                 description: str = ""):
        """
        初始化 Agent
        
        Args:
            agent_name: Agent 名称
            agent_type: Agent 类型
            config: 配置字典
            description: Agent 描述
        """
        self.agent_id = str(uuid.uuid4())
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now()
        self.description = description
        self.capabilities: List[str] = []
        self.current_task: Optional[TaskEntity] = None
        self.task_history: List[TaskEntity] = []
        self.config = config or {}
        self.metadata: Dict[str, Any] = {}
        
        self._logger = get_logger(f"agent.{agent_name}")
        self._message_callbacks: List[Callable[[Message], None]] = []
        
        self._logger.info(f"Agent 已创建：{self.agent_name} ({self.agent_type.value})")
    
    @abstractmethod
    def execute_task(self, task: TaskEntity) -> Any:
        """
        执行任务（抽象方法，子类必须实现）
        
        Args:
            task: 要执行的任务
            
        Returns:
            任务执行结果
        """
        pass
    
    @abstractmethod
    def can_handle(self, task: TaskEntity) -> bool:
        """
        判断是否能处理给定任务（抽象方法，子类必须实现）
        
        Args:
            task: 任务对象
            
        Returns:
            是否能处理
        """
        pass
    
    def start_task(self, task: TaskEntity) -> bool:
        """
        开始执行任务
        
        Args:
            task: 任务对象
            
        Returns:
            是否成功开始
        """
        if self.status != AgentStatus.IDLE:
            self._logger.warning(f"Agent 当前状态无法执行任务：{self.status.value}")
            return False
        
        if not self.can_handle(task):
            self._logger.warning(f"Agent 无法处理该任务：{task.task_type}")
            return False
        
        self.current_task = task
        self.status = AgentStatus.BUSY
        task.update_status(TaskStatus.IN_PROGRESS)
        task.executor = self.agent_id
        
        self._logger.info(f"开始执行任务：{task.task_name}")
        self._send_status_update()
        
        return True
    
    def complete_task(self, result: Any = None) -> None:
        """
        完成任务
        
        Args:
            result: 任务执行结果
        """
        if not self.current_task:
            self._logger.warning("没有正在执行的任务")
            return
        
        self.current_task.update_status(TaskStatus.COMPLETED)
        if result is not None:
            self.current_task.output_data["result"] = result
        
        self.task_history.append(self.current_task)
        self._logger.info(f"任务完成：{self.current_task.task_name}")
        
        self.current_task = None
        self.status = AgentStatus.IDLE
        self._send_status_update()
    
    def fail_task(self, error_message: str) -> None:
        """
        任务失败
        
        Args:
            error_message: 错误消息
        """
        if not self.current_task:
            self._logger.warning("没有正在执行的任务")
            return
        
        self.current_task.update_status(TaskStatus.FAILED)
        self.current_task.output_data["error"] = error_message
        self._logger.error(f"任务失败：{self.current_task.task_name} - {error_message}")
        
        self.current_task = None
        self.status = AgentStatus.ERROR
        self._send_status_update()
    
    def pause(self) -> None:
        """暂停 Agent"""
        if self.status == AgentStatus.BUSY:
            self._logger.warning("Agent 正在执行任务，无法暂停")
            return
        
        self.status = AgentStatus.PAUSED
        self._logger.info(f"Agent 已暂停：{self.agent_name}")
        self._send_status_update()
    
    def resume(self) -> None:
        """恢复 Agent"""
        if self.status != AgentStatus.PAUSED:
            self._logger.warning("Agent 未处于暂停状态")
            return
        
        self.status = AgentStatus.IDLE
        self._logger.info(f"Agent 已恢复：{self.agent_name}")
        self._send_status_update()
    
    def register_capability(self, capability: str) -> None:
        """
        注册能力
        
        Args:
            capability: 能力名称
        """
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self._logger.debug(f"注册能力：{capability}")
    
    def has_capability(self, capability: str) -> bool:
        """
        检查是否具有指定能力
        
        Args:
            capability: 能力名称
            
        Returns:
            是否具有该能力
        """
        return capability in self.capabilities
    
    def on_message(self, callback: Callable[[Message], None]) -> None:
        """
        注册消息回调
        
        Args:
            callback: 消息回调函数
        """
        self._message_callbacks.append(callback)
    
    def send_message(self, message: Message, receiver: Optional[str] = None) -> int:
        """
        发送消息
        
        Args:
            message: 消息对象
            receiver: 接收者 ID（可选）
            
        Returns:
            投递数量
        """
        message.sender = self.agent_id
        if receiver:
            message.receiver = receiver
        
        return comm_bus.publish(message)
    
    def _send_status_update(self) -> None:
        """发送状态更新消息"""
        message = Message(
            message_type=MessageType.AGENT_STATUS,
            content=f"Agent {self.agent_name} status: {self.status.value}",
            data={
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "status": self.status.value,
                "current_task": self.current_task.task_id if self.current_task else None
            }
        )
        self.send_message(message)
    
    def handle_message(self, message: Message) -> None:
        """
        处理接收到的消息
        
        Args:
            message: 消息对象
        """
        for callback in self._message_callbacks:
            try:
                callback(message)
            except Exception as e:
                self._logger.error(f"消息回调执行失败：{e}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取 Agent 信息
        
        Returns:
            Agent 信息字典
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "description": self.description,
            "capabilities": self.capabilities,
            "has_current_task": self.current_task is not None,
            "task_history_count": len(self.task_history),
            "created_at": self.created_at.isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取 Agent 统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "total_tasks": len(self.task_history),
            "completed_tasks": len([t for t in self.task_history if t.is_completed()]),
            "failed_tasks": len([t for t in self.task_history if t.is_failed()]),
            "status": self.status.value,
            "capabilities": self.capabilities
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.agent_type.value.capitalize()}({self.agent_name}, {self.status.value})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (
            f"BaseAgent(agent_id='{self.agent_id}', agent_name='{self.agent_name}', "
            f"agent_type={self.agent_type.name}, status={self.status.value})"
        )