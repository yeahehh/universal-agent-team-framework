"""分析 Agent 模块
负责数据分析和决策支持
"""
from typing import Any, Dict, List, Optional
import logging

from .base_agent import BaseAgent, AgentType, AgentStatus
from core import TaskEntity, TaskStatus, Message, MessageType


class AnalystAgent(BaseAgent):
    """
    分析 Agent
    
    核心职责:
        1. 数据分析
        2. 模式识别
        3. 提供决策建议
        4. 生成分析报告
    """
    
    def __init__(self, agent_name: str = "Analyst", config: Optional[Dict[str, Any]] = None):
        """
        初始化分析 Agent
        
        Args:
            agent_name: Agent 名称
            config: 配置字典
        """
        super().__init__(
            agent_name=agent_name,
            agent_type=AgentType.ANALYST,
            config=config,
            description="分析 Agent，负责数据分析和决策支持"
        )
        
        self._analysis_depth = self.config.get("analysis_depth", "medium")
        self._cache_results = self.config.get("cache_results", True)
        self._result_cache: Dict[str, Any] = {}
        
        # 注册能力
        self.register_capability("data_analysis")
        self.register_capability("pattern_recognition")
        self.register_capability("decision_support")
        
        self._logger = logging.getLogger(f"agent.{agent_name}")
        self._logger.info(f"分析 Agent 已初始化：{self.agent_name}")
    
    def execute_task(self, task: TaskEntity) -> Any:
        """
        执行分析任务
        
        Args:
            task: 任务对象
            
        Returns:
            分析结果
        """
        if not self.start_task(task):
            return {"success": False, "error": "无法开始任务"}
        
        try:
            # 检查缓存
            cache_key = self._get_cache_key(task)
            if self._cache_results and cache_key in self._result_cache:
                self._logger.debug("使用缓存结果")
                result = self._result_cache[cache_key]
            else:
                # 执行分析
                result = self._analyze_data(task)
                
                # 缓存结果
                if self._cache_results:
                    self._result_cache[cache_key] = result
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            error_msg = f"分析失败：{str(e)}"
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
        return task.task_type in ["analysis", "data_analysis", "report"]
    
    def _get_cache_key(self, task: TaskEntity) -> str:
        """
        生成缓存键
        
        Args:
            task: 任务对象
            
        Returns:
            缓存键
        """
        return f"{task.task_type}:{hash(str(task.input_data))}"
    
    def _analyze_data(self, task: TaskEntity) -> Dict[str, Any]:
        """
        分析数据
        
        Args:
            task: 任务对象
            
        Returns:
            分析结果
        """
        self._logger.info(f"执行分析任务：{task.task_name}")
        
        # 模拟分析逻辑
        analysis_result = {
            "success": True,
            "analysis_type": self._analysis_depth,
            "findings": [],
            "recommendations": [],
            "confidence_score": 0.95
        }
        
        # 根据输入数据生成分析
        if task.input_data:
            analysis_result["data_points"] = len(task.input_data)
            analysis_result["findings"].append(f"分析了 {len(task.input_data)} 个数据点")
        
        return analysis_result
    
    def clear_cache(self) -> None:
        """清空结果缓存"""
        self._result_cache.clear()
        self._logger.info("分析缓存已清空")
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self._result_cache)