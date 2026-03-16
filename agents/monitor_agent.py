"""监控 Agent 模块
负责系统监控和异常检测
"""
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

from .base_agent import BaseAgent, AgentType, AgentStatus
from core import TaskEntity, TaskStatus, Message, MessageType, exception_handler


class MonitorAgent(BaseAgent):
    """
    监控 Agent
    
    核心职责:
        1. 监控系统状态
        2. 检测异常情况
        3. 发送告警
        4. 自动恢复
    """
    
    def __init__(self, agent_name: str = "Monitor", config: Optional[Dict[str, Any]] = None):
        """
        初始化监控 Agent
        
        Args:
            agent_name: Agent 名称
            config: 配置字典
        """
        super().__init__(
            agent_name=agent_name,
            agent_type=AgentType.MONITOR,
            config=config,
            description="监控 Agent，负责系统监控和异常检测"
        )
        
        self._check_interval = self.config.get("check_interval", 10)
        self._alert_threshold = self.config.get("alert_threshold", 5)
        self._auto_recovery = self.config.get("auto_recovery", True)
        
        self._monitored_agents: List[str] = []
        self._alert_history: List[Dict[str, Any]] = []
        self._anomaly_count: Dict[str, int] = {}
        
        # 注册能力
        self.register_capability("system_monitoring")
        self.register_capability("anomaly_detection")
        self.register_capability("alerting")
        self.register_capability("auto_recovery")
        
        self._logger = logging.getLogger(f"agent.{agent_name}")
        self._logger.info(f"监控 Agent 已初始化：{self.agent_name}")
    
    def execute_task(self, task: TaskEntity) -> Any:
        """
        执行监控任务
        
        Args:
            task: 任务对象
            
        Returns:
            监控结果
        """
        if not self.start_task(task):
            return {"success": False, "error": "无法开始任务"}
        
        try:
            # 执行监控
            monitoring_result = self._perform_monitoring(task)
            
            self.complete_task(monitoring_result)
            return monitoring_result
            
        except Exception as e:
            error_msg = f"监控任务失败：{str(e)}"
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
        return task.task_type in ["monitoring", "health_check", "alert"]
    
    def monitor_agent(self, agent_id: str) -> None:
        """
        监控指定 Agent
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self._monitored_agents:
            self._monitored_agents.append(agent_id)
            self._logger.info(f"开始监控 Agent: {agent_id}")
    
    def unmonitor_agent(self, agent_id: str) -> None:
        """
        停止监控指定 Agent
        
        Args:
            agent_id: Agent ID
        """
        if agent_id in self._monitored_agents:
            self._monitored_agents.remove(agent_id)
            self._logger.info(f"停止监控 Agent: {agent_id}")
    
    def report_anomaly(self, agent_id: str, anomaly_type: str, details: str) -> None:
        """
        报告异常
        
        Args:
            agent_id: Agent ID
            anomaly_type: 异常类型
            details: 异常详情
        """
        self._logger.warning(f"检测到异常：{agent_id} - {anomaly_type}")
        
        # 记录异常
        anomaly_record = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "anomaly_type": anomaly_type,
            "details": details
        }
        self._alert_history.append(anomaly_record)
        
        # 增加异常计数
        if agent_id not in self._anomaly_count:
            self._anomaly_count[agent_id] = 0
        self._anomaly_count[agent_id] += 1
        
        # 检查是否超过阈值
        if self._anomaly_count[agent_id] >= self._alert_threshold:
            self._send_alert(agent_id, anomaly_type, details)
            
            # 自动恢复
            if self._auto_recovery:
                self._perform_recovery(agent_id)
    
    def get_monitored_agents(self) -> List[str]:
        """获取被监控的 Agent 列表"""
        return self._monitored_agents.copy()
    
    def get_alert_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取告警历史"""
        return self._alert_history[-limit:]
    
    def _perform_monitoring(self, task: TaskEntity) -> Dict[str, Any]:
        """
        执行监控
        
        Args:
            task: 任务对象
            
        Returns:
            监控结果
        """
        self._logger.info(f"执行监控任务：{task.task_name}")
        
        # 模拟监控逻辑
        monitoring_result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "monitored_agents_count": len(self._monitored_agents),
            "anomalies_detected": 0,
            "system_status": "healthy"
        }
        
        return monitoring_result
    
    def _send_alert(self, agent_id: str, anomaly_type: str, details: str) -> None:
        """
        发送告警
        
        Args:
            agent_id: Agent ID
            anomaly_type: 异常类型
            details: 异常详情
        """
        alert_message = Message(
            message_type=MessageType.SYSTEM,
            subject=f"告警：{anomaly_type}",
            content=f"Agent {agent_id} 检测到异常：{details}",
            data={
                "agent_id": agent_id,
                "anomaly_type": anomaly_type,
                "alert_level": "high"
            }
        )
        
        self.send_message(alert_message)
        self._logger.error(f"发送告警：{agent_id} - {anomaly_type}")
    
    def _perform_recovery(self, agent_id: str) -> None:
        """
        执行恢复操作
        
        Args:
            agent_id: Agent ID
        """
        self._logger.info(f"执行自动恢复：{agent_id}")
        
        # 重置异常计数
        self._anomaly_count[agent_id] = 0
        
        # 这里可以发送恢复命令给指定的 Agent
        recovery_message = Message(
            message_type=MessageType.SYSTEM,
            subject="自动恢复",
            content=f"Agent {agent_id} 已执行自动恢复",
            data={"agent_id": agent_id, "action": "recovery"}
        )
        
        self.send_message(recovery_message)