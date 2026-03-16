![License](https://img.shields.io/github/license/yeahehh/universal-agent-team-framework?color=blue)
![GitHub stars](https://img.shields.io/github/stars/yeahehh/universal-agent-team-framework?style=social)
![GitHub issues](https://img.shields.io/github/issues/yeahehh/universal-agent-team-framework?color=orange)
![GitHub forks](https://img.shields.io/github/forks/yeahehh/universal-agent-team-framework?style=social)
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)

# 通用 Agent 工作团队框架

一个基于 Python 的多 Agent 协作系统框架，支持插件化扩展和灵活配置。

## 📋 目录

- [项目简介](#-项目简介)
- [核心特性](#-核心特性)
- [项目架构](#-项目架构)
- [快速开始](#-快速开始)
- [使用示例](#-使用示例)
- [插件开发](#-插件开发)
- [配置说明](#-配置说明)
- [测试运行](#-测试运行)
- [开发规范](#-开发规范)
- [常见问题](#-常见问题)

---

## 🎯 项目简介

本项目是一个**通用多 Agent 协作框架**，采用工程化设计，提供：

- **标准化 Agent 体系**：Manager、Executor、Analyst、Monitor 四种角色
- **可插拔插件系统**：数据类、LLM 类、工具类、自定义插件
- **灵活通信机制**：发布/订阅模式的通信总线
- **多层记忆引擎**：短期记忆、长期记忆、工作记忆
- **完善异常处理**：统一异常捕获和日志记录

### 适用场景

- 自动化任务调度系统
- 智能客服团队
- 数据分析工作流
- 代码审查系统
- 任何需要多角色协作的场景

---

## ✨ 核心特性

### 1. Agent 角色体系

| Agent 类型   | 职责               | 特点                     |
| ------------ | ------------------ | ------------------------ |
| **Manager**  | 团队协调、任务分配 | 管理下属 Agent、任务队列 |
| **Executor** | 任务执行           | 重试机制、超时控制       |
| **Analyst**  | 数据分析           | 数据缓存、分析优化       |
| **Monitor**  | 系统监控           | 性能监控、异常告警       |

### 2. 插件分类

| 插件类型   | 功能     | 示例                 |
| ---------- | -------- | -------------------- |
| **DATA**   | 数据操作 | 数据库、文件、API    |
| **LLM**    | 大模型   | 对话、文本嵌入       |
| **TOOL**   | 工具类   | 搜索、计算、代码执行 |
| **CUSTOM** | 自定义   | 任意扩展功能         |

### 3. 设计原则

- ✅ **单一职责**：每个 Agent/插件只负责一个功能
- ✅ **无状态设计**：插件间不互相调用
- ✅ **可插拔**：支持动态加载和卸载
- ✅ **标准化**：输入输出遵循统一格式
- ✅ **无硬编码**：所有参数放入配置文件

---

## 🏗️ 项目架构

agent_team_system/
├── core/                  # 核心底层（稳定后仅修 bug）
│   ├── task_entity.py     # 任务实体
│   ├── message_protocol.py # 消息协议
│   ├── comm_bus.py        # 通信总线
│   ├── memory_engine.py   # 记忆引擎
│   └── exception_handler.py # 异常处理
├── agents/                # Agent 角色
│   ├── base_agent.py      # Agent 基类
│   ├── manager_agent.py   # 管理 Agent
│   ├── executor_agent.py  # 执行 Agent
│   ├── analyst_agent.py   # 分析 Agent
│   └── monitor_agent.py   # 监控 Agent
├── plugins/               # 插件系统（可无限扩展）
│   ├── base_plugin.py     # 插件基类
│   ├── data_plugins/      # 数据类插件
│   ├── llm_plugins/       # LLM 类插件
│   ├── tool_plugins/      # 工具类插件
│   └── custom_plugins/    # 自定义插件
├── config/                # 配置文件
│   ├── system_config.py   # 系统配置
│   └── agent_config.py    # Agent 配置
├── utils/                 # 工具类
│   ├── log_util.py        # 日志工具
│   ├── time_util.py       # 时间工具
│   └── validate_util.py   # 验证工具
├── team_builder.py        # 团队组装器
├── main.py                # 系统启动入口
├── requirements.txt       # 依赖清单
├── test_plugins.py        # 插件测试
├── test_system.py         # 系统测试
└── README.md              # 本文档

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- Windows / Linux / macOS

### 2. 安装依赖

```bash
cd agent_team_system
pip install -r requirements.txt
```

### 3. 启动系统

```bash
python main.py
```

### 4. 运行测试

```bash
# 测试插件系统
python test_plugins.py

# 测试整体系统
python test_system.py
```

---

## 💡 使用示例

### 示例 1：创建自定义团队

```python
from team_builder import TeamBuilder
from agents import AgentType

# 创建团队构建器
builder = TeamBuilder("MyTeam")

# 构建团队
team_info = (builder
    .create_comm_bus()
    .create_memory_engine()
    .create_agent(AgentType.MANAGER, "Boss")
    .create_agent(AgentType.EXECUTOR, "Worker-1")
    .create_agent(AgentType.EXECUTOR, "Worker-2")
    .create_agent(AgentType.ANALYST, "Analyzer")
    .build())

print(f"团队名称：{team_info['team_name']}")
print(f"Agent 数量：{len(team_info['agents'])}")
```

### 示例 2：挂载插件到 Agent

```python
from plugins.tool_plugins import CalculatorPlugin
from team_builder import TeamBuilder

builder = TeamBuilder()
builder.create_comm_bus().create_default_team()

# 创建插件
calculator = CalculatorPlugin("Calc")

# 获取第一个 Agent
agent_id = list(builder.agents.keys())[0]

# 挂载插件
builder.mount_plugin(calculator, agent_id)

print(f"已挂载插件：{len(builder.plugins)}")
```

### 示例 3：使用插件

```python
from plugins.tool_plugins import CalculatorPlugin
from plugins.base_plugin import PluginContext

# 创建并初始化插件
plugin = CalculatorPlugin("MyCalc")
plugin.initialize()

# 执行计算
context = PluginContext(
    input_data={"expression": "1 + 2 * 3"}
)
result = plugin.execute_with_context(context)
print(f"计算结果：{result}")  # 输出：7
```

### 示例 4：提交任务

```python
from main import AgentTeamSystem
from core.task_entity import TaskPriority

# 创建系统
system = AgentTeamSystem("TestTeam")
system.initialize()

# 提交任务
task_id = system.submit_task(
    "分析数据并生成报告",
    priority=TaskPriority.HIGH
)
print(f"任务已提交：{task_id}")

# 关闭系统
system.shutdown()
```

---

## 🔌 插件开发

### 开发步骤

#### 1. 继承基类

```python
from plugins.base_plugin import BasePlugin, PluginContext, PluginType

class MyPlugin(BasePlugin):
    def __init__(self, plugin_name="MyPlugin", config=None):
        super().__init__(plugin_name, PluginType.CUSTOM, config)
    
    def execute(self, context: PluginContext) -> any:
        # 实现插件功能
        pass
    
    def validate(self, input_data: dict) -> bool:
        # 验证输入
        return True
    
    def get_info(self) -> dict:
        return {
            "plugin_name": self.plugin_name,
            "plugin_type": self.plugin_type.value
        }
```

#### 2. 实现钩子方法（可选）

```python
def _on_initialize(self) -> None:
    """初始化时调用"""
    pass

def _on_shutdown(self) -> None:
    """关闭时调用"""
    pass
```

#### 3. 添加到模块导出

编辑 `plugins/custom_plugins/__init__.py`：

```python
from .my_plugin import MyPlugin

__all__ = ["MyPlugin"]
```

### 插件模板

项目已提供 `plugins/custom_plugins/example_plugin.py` 作为开发模板。

---

## ⚙️ 配置说明

### 系统配置 (config/system_config.py)

```python
SYSTEM_CONFIG = {
    "log_level": "INFO",
    "max_workers": 10,
    "timeout_seconds": 300
}
```

### Agent 配置 (config/agent_config.py)

```python
AGENT_CONFIG = {
    "manager": {
        "max_subordinates": 10,
        "task_queue_size": 100
    },
    "executor": {
        "max_retries": 3,
        "timeout_seconds": 60
    }
}
```

### 插件配置

每个插件在初始化时接收配置字典：

```python
plugin = DatabasePlugin("DB", config={
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "mydb"
})
```

---

## 🧪 测试运行

### 单元测试

```bash
# 运行所有插件测试
python test_plugins.py

# 运行系统整体测试
python test_system.py
```

### 测试覆盖

当前测试覆盖：
- ✅ 插件基类
- ✅ 数据类插件
- ✅ LLM 类插件
- ✅ 工具类插件
- ✅ 自定义插件
- ✅ 团队构建器
- ✅ 系统整体流程

---

## 📏 开发规范

### 代码规范

- 遵循 PEP8 编码规范
- 命名见名知意，禁止无意义简写
- 文件/类/函数必须加注释
- 禁止跨模块直接调用

### 开发边界

- 单次任务：单个文件 + 单个功能
- Agent 仅做调度，具体执行封装为插件
- 插件之间无依赖
- 所有参数放入 config 目录

### 提交流程

1. 创建/修改文件
2. 运行测试验证
3. 更新 CHANGELOG.md
4. 提交代码

---

## ❓ 常见问题

### Q1: 如何添加新的 Agent 类型？

A: 继承 `agents/base_agent.py` 中的 `BaseAgent` 类，实现抽象方法。

### Q2: 插件如何与 Agent 通信？

A: 通过通信总线（CommunicationBus）发布/订阅消息。

### Q3: 如何持久化记忆数据？

A: 配置 `MemoryEngine` 的长期存储功能，或使用数据库插件。

### Q4: 支持哪些 LLM 模型？

A: 默认支持 OpenAI 系列，可通过插件扩展支持其他模型（如 Ollama、文心一言等）。

### Q5: 如何调试 Agent 行为？

A: 查看日志文件（logs/目录），或启用 DEBUG 级别日志。

---

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License

---

## 📧 联系方式

如有问题或建议，请提交 Issue 或联系维护者。

---

**🎉 感谢使用通用 Agent 工作团队框架！**