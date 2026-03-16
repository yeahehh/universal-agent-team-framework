"""总管 Agent 模块
负责任务分发、协调和团队管理
"""
from typing import Any, Dict, List, Optional
import logging

from .base_agent import BaseAgent, AgentType, AgentStatus
from core import TaskEntity, TaskStatus, Message, MessageType, comm_bus


class ManagerAgent(BaseAgent):
    """
    总管 Agent
    
    核心职责:
        1. 接收和分发任务
        2. 协调其他 Agent 工作
        3. 监控团队状态
        4. 做出决策和调度
    """
    
    def __init__(self, agent_name: str = "Manager", config: Optional[Dict[str, Any]] = None):
        """
        初始化总管 Agent
        
        Args:
            agent_name: Agent 名称
            config: 配置字典
        """
        super().__init__(
            agent_name=agent_name,
            agent_type=AgentType.MANAGER,
            config=config,
            description="团队总管 Agent，负责任务分发和协调"
        )
        
        self._subordinates: List[str] = []  # 下属 Agent ID 列表
        self._task_queue: List[TaskEntity] = []
        self._max_subordinates = self.config.get("max_subordinates", 10)
        
        # 注册能力
        self.register_capability("task_distribution")
        self.register_capability("team_coordination")
        self.register_capability("decision_making")
        
        self._logger = logging.getLogger(f"agent.{agent_name}")
        self._logger.info(f"总管 Agent 已初始化：{self.agent_name}")
    
    def execute_task(self, task: TaskEntity) -> Any:
        """
        执行任务：分发任务给合适的下属
        
        Args:
            task: 要执行的任务
            
        Returns:
            任务分发结果
        """
        if not self.start_task(task):
            return {"success": False, "error": "无法开始任务"}
        
        try:
            # 分析任务并分发给合适的 Agent
            assigned_agent = self._find_suitable_agent(task)
            
            if assigned_agent:
                # 发送任务给下属
                self._delegate_task(task, assigned_agent)
                result = {
                    "success": True,
                    "message": f"任务已分发给 Agent: {assigned_agent}",
                    "assigned_to": assigned_agent
                }
            else:
                # 没有合适的下属，自己处理或加入队列
                self._task_queue.append(task)
                result = {
                    "success": False,
                    "message": "没有合适的下属，任务已加入队列",
                    "queued": True
                }
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            error_msg = f"任务执行失败：{str(e)}"
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
        # 总管可以处理所有类型的任务（通过分发）
        return True
    
    def register_subordinate(self, agent_id: str) -> bool:
        """
        注册下属 Agent
        
        Args:
            agent_id: 下属 Agent ID
            
        Returns:
            是否注册成功
        """
        if len(self._subordinates) >= self._max_subordinates:
            self._logger.warning("下属数量已达上限")
            return False
        
        if agent_id not in self._subordinates:
            self._subordinates.append(agent_id)
            self._logger.info(f"注册下属 Agent: {agent_id}")
            return True
        
        return False
    
    def unregister_subordinate(self, agent_id: str) -> bool:
        """
        注销下属 Agent
        
        Args:
            agent_id: 下属 Agent ID
            
        Returns:
            是否注销成功
        """
        if agent_id in self._subordinates:
            self._subordinates.remove(agent_id)
            self._logger.info(f"注销下属 Agent: {agent_id}")
            return True
        return False
    
    def get_subordinate_count(self) -> int:
        """获取下属数量"""
        return len(self._subordinates)
    
    def get_subordinates(self) -> List[str]:
        """获取所有下属 ID 列表"""
        return self._subordinates.copy()
    
    def get_task_queue(self) -> List[TaskEntity]:
        """获取任务队列"""
        return self._task_queue.copy()
    
    def get_queue_size(self) -> int:
        """获取任务队列大小"""
        return len(self._task_queue)
    
    def _find_suitable_agent(self, task: TaskEntity) -> Optional[str]:
        """
        寻找合适的下属 Agent
        
        Args:
            task: 任务对象
            
        Returns:
            合适的 Agent ID，如果没有则返回 None
        """
        # 简单实现：返回第一个空闲的下属
        # 实际应用中应该根据任务类型、Agent 能力等更复杂的逻辑来选择
        
        for agent_id in self._subordinates:
            # 这里应该查询 Agent 状态，简单实现直接返回
            return agent_id
        
        return None
    
    def _delegate_task(self, task: TaskEntity, agent_id: str) -> None:
        """
        委派任务给下属
        
        Args:
            task: 任务对象
            agent_id: 下属 Agent ID
        """
        message = Message(
            message_type=MessageType.TASK_CREATE,
            subject=f"任务委派：{task.task_name}",
            content=task.task_description,
            data=task.to_dict()
        )
        
        self.send_message(message, receiver=agent_id)
        self._logger.info(f"任务已委派给 Agent: {agent_id}")
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Agent 信息"""
        info = super().get_info()
        info["subordinate_count"] = len(self._subordinates)
        info["task_queue_size"] = len(self._task_queue)
        return info