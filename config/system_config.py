"""系统配置模块
定义系统级别的配置参数
"""

# 系统名称
SYSTEM_NAME = "通用 Agent 工作团队"

# 系统版本
SYSTEM_VERSION = "1.0.0"

# 日志配置
LOG_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "log_dir": "logs"
}

# 通信总线配置
COMM_BUS_CONFIG = {
    "max_history_size": 1000,  # 最大消息历史数量
    "queue_max_size": 5000,    # 消息队列最大容量
    "worker_threads": 4        # 工作线程数
}

# 记忆引擎配置
MEMORY_CONFIG = {
    "max_short_term_size": 1000,   # 短期记忆最大容量
    "max_long_term_size": 10000,   # 长期记忆最大容量
    "default_ttl_seconds": 3600,   # 默认过期时间（秒）
    "cleanup_interval": 300        # 清理间隔（秒）
}

# 任务配置
TASK_CONFIG = {
    "max_retries": 3,              # 最大重试次数
    "default_priority": "MEDIUM",  # 默认优先级：LOW, MEDIUM, HIGH, URGENT
    "timeout_seconds": 300         # 默认超时时间（秒）
}

# Agent 配置
AGENT_CONFIG = {
    "max_concurrent_tasks": 5,     # 最大并发任务数
    "task_queue_size": 100,        # 任务队列大小
    "heartbeat_interval": 30       # 心跳间隔（秒）
}

# 插件配置
PLUGIN_CONFIG = {
    "enabled": True,               # 是否启用插件系统
    "auto_discover": True,         # 自动发现插件
    "plugin_dirs": ["plugins"]     # 插件目录列表
}

# 性能配置
PERFORMANCE_CONFIG = {
    "enable_profiling": False,     # 是否启用性能分析
    "max_memory_mb": 2048,         # 最大内存使用（MB）
    "gc_interval": 600             # 垃圾回收间隔（秒）
}