"""Agent 工作团队系统
通用多 Agent 协作框架
"""
from . import core
from . import utils
from . import config
from . import agents
from . import plugins

__version__ = "1.0.0"
__author__ = "Agent Team"

__all__ = ["core", "utils", "config", "agents", "plugins"]