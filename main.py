"""
通用 Agent 工作团队 - 主启动入口

功能：
- 初始化系统配置
- 构建 Agent 团队
- 加载插件
- 启动任务调度
- 处理用户输入
"""

import logging
from typing import Dict, Any, Optional
from team_builder import TeamBuilder, build_team
from agents import AgentType, ManagerAgent
from core.task_entity import TaskEntity, TaskPriority, TaskStatus
from core.message_protocol import Message, MessageType
from utils.log_util import get_logger


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = get_logger("main")


class AgentTeamSystem:
    """
    Agent 团队系统主类
    
    功能：
    - 系统初始化
    - 团队管理
    - 任务调度
    - 生命周期管理
    """
    
    def __init__(self, team_name: str = "DefaultTeam"):
        """
        初始化系统
        
        Args:
            team_name: 团队名称
        """
        self.team_name = team_name
        self.team_builder: Optional[TeamBuilder] = None
        self.team_info: Dict[str, Any] = {}
        self._running = False
    
    def initialize(self) -> bool:
        """
        初始化系统
        
        Returns:
            初始化是否成功
        """
        try:
            logger.info(f"正在初始化系统：{self.team_name}")
            
            # 构建团队
            self.team_builder = TeamBuilder(self.team_name)
            self.team_info = (self.team_builder
                             .create_comm_bus()
                             .create_memory_engine()
                             .create_default_team()
                             .build())
            
            logger.info(f"团队构建完成：{len(self.team_info['agents'])} 个 Agent")
            
            # 挂载示例插件（可选）
            # self._load_plugins()
            
            self._running = True
            logger.info("系统初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化失败：{e}")
            return False
    
    def _load_plugins(self) -> None:
        """加载插件到 Agent"""
        # 示例：加载插件到执行 Agent
        # from plugins.tool_plugins import CalculatorPlugin
        # calculator = CalculatorPlugin("Calc")
        # executor_id = list(self.team_builder.agents.keys())[1]  # 获取第一个执行 Agent
        # self.team_builder.mount_plugin(calculator, executor_id)
        pass
    
    def get_manager(self) -> Optional[ManagerAgent]:
        """获取 Manager Agent"""
        for agent_id, agent in self.team_builder.agents.items():
            if agent.agent_type == AgentType.MANAGER:
                return agent
        return None
    

    def submit_task(self, task_description: str, priority: TaskPriority = TaskPriority.MEDIUM) -> Optional[str]:
        """
        提交任务
        
        Args:
            task_description: 任务描述
            priority: 任务优先级
            
        Returns:
            任务 ID（如果成功）
        """
        manager = self.get_manager()
        if not manager:
            logger.error("Manager Agent 未找到")
            return None
        
        task = TaskEntity(
            task_description=task_description,
            priority=priority
        )
        
        # 将任务交给 Manager 处理
        manager.start_task(task)
        
        logger.info(f"任务已提交：{task.task_id}")
        return task.task_id
    
    def shutdown(self) -> None:
        """关闭系统"""
        logger.info("正在关闭系统...")
        self._running = False
        
        # 清理资源
        if self.team_builder:
            # 关闭所有插件
            for plugin in self.team_builder.plugins.values():
                plugin.shutdown()
            
            # 清理记忆引擎
            if self.team_builder.memory_engine:
                pass  # MemoryEngine 不需要显式关闭
        
        logger.info("系统已关闭")
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "team_name": self.team_name,
            "running": self._running,
            "agents": self.team_info.get("agents", {}),
            "plugins": self.team_info.get("plugins", {}),
            "comm_bus": self.team_info.get("comm_bus", False),
            "memory_engine": self.team_info.get("memory_engine", False)
        }


def main():
    """主函数"""
    print("=" * 60)
    print("通用 Agent 工作团队系统")
    print("=" * 60)
    
    # 创建系统
    system = AgentTeamSystem("MyTeam")
    
    # 初始化
    if not system.initialize():
        logger.error("系统初始化失败")
        return
    
    # 显示系统状态
    status = system.get_status()
    print(f"\n团队名称：{status['team_name']}")
    print(f"运行状态：{'运行中' if status['running'] else '已停止'}")
    print(f"Agent 数量：{len(status['agents'])}")
    print(f"插件数量：{len(status['plugins'])}")
    
    print("\nAgent 列表:")
    for agent_id, info in status["agents"].items():
        print(f"  - {info['name']} ({info['type']}) - {info['status']}")
    
    # 示例：提交任务
    print("\n" + "=" * 60)
    print("示例任务提交")
    print("=" * 60)
    
    task_id = system.submit_task("分析数据并生成报告", TaskPriority.HIGH)
    if task_id:
        print(f"任务已提交：{task_id}")
    
    # 模拟用户交互（简单示例）
    print("\n" + "=" * 60)
    print("系统已就绪，输入 'quit' 退出")
    print("=" * 60)
    
    try:
        while system._running:
            user_input = input("\n请输入命令：").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            elif user_input.lower() == "status":
                status = system.get_status()
                print(f"运行状态：{status['running']}")
                print(f"Agent 数量：{len(status['agents'])}")
            else:
                # 将用户输入作为任务提交
                task_id = system.submit_task(user_input)
                if task_id:
                    print(f"任务已提交：{task_id}")
    except KeyboardInterrupt:
        print("\n检测到中断信号")
    finally:
        system.shutdown()


if __name__ == "__main__":
    main()