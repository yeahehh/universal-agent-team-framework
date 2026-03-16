"""Agent 配置模块
定义各类 Agent 的配置参数
"""

# Manager Agent 配置
MANAGER_AGENT_CONFIG = {
    "name": "Manager",
    "description": "团队总管 Agent，负责任务分发和协调",
    "max_subordinates": 10,        # 最大下属数量
    "decision_timeout": 60,        # 决策超时（秒）
    "auto_delegate": True,         # 自动委派任务
    "monitor_status": True         # 监控状态
}

# Executor Agent 配置
EXECUTOR_AGENT_CONFIG = {
    "name": "Executor",
    "description": "执行 Agent，负责具体任务执行",
    "max_concurrent_tasks": 3,     # 最大并发任务数
    "execution_timeout": 300,      # 执行超时（秒）
    "auto_retry": True,            # 自动重试
    "report_progress": True        # 报告进度
}

# Analyst Agent 配置
ANALYST_AGENT_CONFIG = {
    "name": "Analyst",
    "description": "分析 Agent，负责数据分析和决策支持",
    "analysis_depth": "deep",      # 分析深度：shallow, medium, deep
    "cache_results": True,         # 缓存结果
    "max_cache_size": 100          # 最大缓存数量
}

# Monitor Agent 配置
MONITOR_AGENT_CONFIG = {
    "name": "Monitor",
    "description": "监控 Agent，负责系统监控和异常检测",
    "check_interval": 10,          # 检查间隔（秒）
    "alert_threshold": 5,          # 告警阈值
    "auto_recovery": True,         # 自动恢复
    "log_anomalies": True          # 记录异常
}

# Agent 状态配置
AGENT_STATUS_CONFIG = {
    "idle": "空闲",
    "busy": "忙碌",
    "paused": "暂停",
    "error": "错误",
    "offline": "离线"
}

# Agent 优先级配置
AGENT_PRIORITY_CONFIG = {
    "manager": 1,      # 最高优先级
    "monitor": 2,      # 高优先级
    "analyst": 3,      # 中优先级
    "executor": 4      # 低优先级
}