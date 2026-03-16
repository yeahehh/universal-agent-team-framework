"""
系统整体测试脚本

验证整个 Agent 团队系统的功能
"""

import sys
import logging

# 禁用详细日志
logging.disable(logging.CRITICAL)

def test_system():
    """测试系统整体功能"""
    print("=" * 60)
    print("系统整体测试")
    print("=" * 60)
    
    from main import AgentTeamSystem
    from core.task_entity import TaskPriority
    
    # 创建系统
    system = AgentTeamSystem("TestTeam")
    
    # 初始化
    success = system.initialize()
    assert success, "系统初始化失败"
    print("✓ 系统初始化成功")
    
    # 检查 Agent 数量
    agent_count = len(system.team_info["agents"])
    assert agent_count == 4, f"Agent 数量错误：{agent_count}"
    print(f"✓ Agent 数量正确：{agent_count}")
    
    # 检查系统状态
    status = system.get_status()
    assert status["running"] == True, "系统未运行"
    print("✓ 系统运行状态正常")
    
    # 检查通信总线
    assert status["comm_bus"] == True, "通信总线未初始化"
    print("✓ 通信总线已初始化")
    
    # 检查记忆引擎
    assert status["memory_engine"] == True, "记忆引擎未初始化"
    print("✓ 记忆引擎已初始化")
    
    # 测试任务提交
    task_id = system.submit_task("测试任务", TaskPriority.HIGH)
    assert task_id is not None, "任务提交失败"
    print(f"✓ 任务提交成功：{task_id}")
    
    # 获取 Manager
    manager = system.get_manager()
    assert manager is not None, "Manager 未找到"
    assert manager.agent_name == "Manager", "Manager 名称错误"
    print("✓ Manager Agent 正常")
    
    # 关闭系统
    system.shutdown()
    assert system._running == False, "系统未关闭"
    print("✓ 系统关闭成功")
    
    print("\n" + "=" * 60)
    print("🎉 所有系统测试通过！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)