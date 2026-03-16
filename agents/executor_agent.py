"""执行 Agent 模块
负责具体任务的执行
"""
from typing import Any, Dict, List, Optional, Callable
import logging

from .base_agent import BaseAgent, AgentType, AgentStatus
from core import TaskEntity, TaskStatus, Message, MessageType


class ExecutorAgent(BaseAgent):
    """
    执行 Agent
    
    核心职责:
        1. 执行具体任务
        2. 报告执行进度
        3. 处理执行异常
        4. 返回执行结果
    """
    
    def __init__(self, agent_name: str = "Executor", config: Optional[Dict[str, Any]] = None):
        """
        初始化执行 Agent
        
        Args:
            agent_name: Agent 名称
            config: 配置字典
        """
        super().__init__(
            agent_name=agent_name,
            agent_type=AgentType.EXECUTOR,
            config=config,
            description="执行 Agent，负责具体任务执行"
        )
        
        self._task_handlers: Dict[str, Callable[[TaskEntity], Any]] = {}
        self._max_concurrent = self.config.get("max_concurrent_tasks", 3)
        self._auto_retry = self.config.get("auto_retry", True)
        
        # 注册能力
        self.register_capability("task_execution")
        self.register_capability("progress_reporting")
        
        self._logger = logging.getLogger(f"agent.{agent_name}")
        self._logger.info(f"执行 Agent 已初始化：{self.agent_name}")
    
    def execute_task(self, task: TaskEntity) -> Any:
        """
        执行任务
        
        Args:
            task: 任务对象
            
        Returns:
            任务执行结果
        """
        if not self.start_task(task):
            return {"success": False, "error": "无法开始任务"}
        
        try:
            # 查找任务处理器
            handler = self._get_task_handler(task.task_type)
            
            if handler:
                # 执行任务
                result = handler(task)
            else:
                # 使用默认处理器
                result = self._default_handler(task)
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            error_msg = f"任务执行失败：{str(e)}"
            
            # 自动重试
            if self._auto_retry and task.can_retry():
                task.increment_retry()
                self._logger.warning(f"任务执行失败，尝试重试 ({task.retry_count}/{task.max_retries})")
                return self.execute_task(task)
            
            self.fail_task(error_msg)
            return {"success": False, "error": error_msg}
    
    def can_handle(self, task: TaskEntity) -> bool:
        """
        判断是否能处理任务
        
        Args:
            task: 任务对象
            
        Returns:
            是否能处理
        """
        # 检查是否有对应的处理器
        return task.task_type in self._task_handlers or True  # 有默认处理器
    
    def register_task_handler(self, task_type: str, handler: Callable[[TaskEntity], Any]) -> None:
        """
        注册任务处理器
        
        Args:
            task_type: 任务类型
            handler: 处理器函数
        """
        self._task_handlers[task_type] = handler
        self._logger.debug(f"注册任务处理器：{task_type}")
    
    def _get_task_handler(self, task_type: str) -> Optional[Callable]:
        """
        获取任务处理器
        
        Args:
            task_type: 任务类型
            
        Returns:
            处理器函数
        """
        return self._task_handlers.get(task_type)
    
    def _default_handler(self, task: TaskEntity) -> Dict[str, Any]:
        """
        默认任务处理器
        
        Args:
            task: 任务对象
            
        Returns:
            执行结果
        """
        self._logger.info(f"执行默认任务：{task.task_name}")
        
        # 模拟任务执行
        return {
            "success": True,
            "message": f"任务 {task.task_name} 执行完成",
            "executor": self.agent_id,
            "execution_time": "N/A"
        }
    
    def report_progress(self, progress: float, message: str = "") -> None:
        """
        报告进度
        
        Args:
            progress: 进度百分比 (0-100)
            message: 进度消息
        """
        if not self.current_task:
            return
        
        progress_message = Message(
            message_type=MessageType.NOTIFICATION,
            subject=f"任务进度：{self.current_task.task_name}",
            content=message,
            data={
                "task_id": self.current_task.task_id,
                "progress": progress,
                "agent_id": self.agent_id
            }
        )
        
        self.send_message(progress_message)
        self._logger.debug(f"进度报告：{progress}% - {message}")