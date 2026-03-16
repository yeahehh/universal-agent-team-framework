"""
团队组装器

负责：
- 创建和注册 Agent
- 挂载插件到 Agent
- 初始化通信总线
- 配置记忆引擎
"""

from typing import Dict, Any, Optional, List
from agents import (
    BaseAgent, ManagerAgent, ExecutorAgent,
    AnalystAgent, MonitorAgent, AgentType
)
from core.comm_bus import CommunicationBus
from core.memory_engine import MemoryEngine
from plugins.base_plugin import BasePlugin


class TeamBuilder:
    """
    团队组装器
    
    功能：
    - 创建 Agent 实例
    - 注册 Agent 到通信总线
    - 为 Agent 挂载插件
    - 初始化系统组件
    """
    
    def __init__(self, team_name: str = "DefaultTeam"):
        """
        初始化团队组装器
        
        Args:
            team_name: 团队名称
        """
        self.team_name = team_name
        self.agents: Dict[str, BaseAgent] = {}
        self.plugins: Dict[str, BasePlugin] = {}
        self.comm_bus: Optional[CommunicationBus] = None
        self.memory_engine: Optional[MemoryEngine] = None
    
    def create_comm_bus(self) -> "TeamBuilder":
        """创建通信总线"""
        self.comm_bus = CommunicationBus()
        return self
    
        
    def create_memory_engine(
        self,
        max_short_term_size: int = 1000,
        max_long_term_size: int = 10000
    ) -> "TeamBuilder":
        """
        创建记忆引擎
        
        Args:
            max_short_term_size: 短期记忆最大容量
            max_long_term_size: 长期记忆最大容量
        """
        self.memory_engine = MemoryEngine(
            max_short_term_size=max_short_term_size,
            max_long_term_size=max_long_term_size
        )
        return self
    
    def create_agent(self, agent_type: AgentType, agent_name: str, 
                     config: Optional[Dict[str, Any]] = None) -> "TeamBuilder":
        """
        创建 Agent
        
        Args:
            agent_type: Agent 类型
            agent_name: Agent 名称
            config: Agent 配置
        """
        agent_map = {
            AgentType.MANAGER: ManagerAgent,
            AgentType.EXECUTOR: ExecutorAgent,
            AgentType.ANALYST: AnalystAgent,
            AgentType.MONITOR: MonitorAgent
        }
        
        agent_class = agent_map.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent = agent_class(agent_name, config)
        self.agents[agent.agent_id] = agent
        
        # 订阅通信总线
        if self.comm_bus:
            self.comm_bus.subscribe(agent.agent_id, agent.handle_message)
        
        return self
    
    def create_default_team(self) -> "TeamBuilder":
        """创建默认团队（包含所有类型的 Agent）"""
        self.create_agent(AgentType.MANAGER, "Manager")
        self.create_agent(AgentType.EXECUTOR, "Executor-1")
        self.create_agent(AgentType.ANALYST, "Analyst-1")
        self.create_agent(AgentType.MONITOR, "Monitor-1")
        return self
    
    def mount_plugin(self, plugin: BasePlugin, agent_id: str) -> "TeamBuilder":
        """
        挂载插件到 Agent
        
        Args:
            plugin: 插件实例
            agent_id: Agent ID
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        # 初始化插件
        plugin.initialize()
        
        # 存储插件引用
        self.plugins[plugin.plugin_id] = plugin
        
        # 将插件添加到 Agent 的插件列表
        agent = self.agents[agent_id]
        if not hasattr(agent, "_plugins"):
            agent._plugins = []
        agent._plugins.append(plugin)
        
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        完成团队构建
        
        Returns:
            团队信息字典
        """
        # 记忆引擎和通信总线不需要额外初始化
        # MemoryEngine 在 __init__ 时已自动初始化
        # CommunicationBus 也不需要显式初始化
        
        return {
            "team_name": self.team_name,
            "agents": {
                agent_id: {
                    "name": agent.agent_name,
                    "type": agent.agent_type.value,
                    "status": agent.status.value
                }
                for agent_id, agent in self.agents.items()
            },
            "plugins": {
                plugin_id: {
                    "name": plugin.plugin_name,
                    "type": plugin.plugin_type.value,
                    "status": plugin.status.value
                }
                for plugin_id, plugin in self.plugins.items()
            },
            "comm_bus": self.comm_bus is not None,
            "memory_engine": self.memory_engine is not None
        }
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """获取 Agent 实例"""
        return self.agents.get(agent_id)
    
    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_id)


def build_team(team_name: str = "DefaultTeam") -> Dict[str, Any]:
    """
    便捷函数：构建默认团队
    
    Args:
        team_name: 团队名称
        
    Returns:
        团队信息
    """
    builder = TeamBuilder(team_name)
    return (builder
            .create_comm_bus()
            .create_memory_engine()
            .create_default_team()
            .build())


if __name__ == "__main__":
    # 测试团队构建
    team_info = build_team("TestTeam")
    
    print(f"团队名称：{team_info['team_name']}")
    print(f"Agent 数量：{len(team_info['agents'])}")
    print(f"插件数量：{len(team_info['plugins'])}")
    print(f"通信总线：{'已初始化' if team_info['comm_bus'] else '未初始化'}")
    print(f"记忆引擎：{'已初始化' if team_info['memory_engine'] else '未初始化'}")
    
    print("\nAgent 列表:")
    for agent_id, info in team_info["agents"].items():
        print(f"  - {info['name']} ({info['type']}) - {info['status']}")