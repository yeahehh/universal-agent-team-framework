"""
插件基类模块

提供所有插件的统一接口和基础能力：
- PluginStatus: 插件状态枚举
- PluginType: 插件类型枚举
- PluginContext: 插件执行上下文
- BasePlugin: 插件抽象基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import uuid
from datetime import datetime


class PluginStatus(Enum):
    """插件状态枚举"""
    ACTIVE = "active"           # 激活状态
    INACTIVE = "inactive"       # 未激活状态
    ERROR = "error"             # 错误状态
    LOADING = "loading"         # 加载中
    UNLOADING = "unloading"     # 卸载中


class PluginType(Enum):
    """插件类型枚举"""
    DATA = "data"               # 数据类插件（数据库、文件、API）
    LLM = "llm"                 # 大模型类插件（对话、嵌入）
    TOOL = "tool"               # 工具类插件（搜索、计算、代码）
    CUSTOM = "custom"           # 自定义插件


@dataclass
class PluginContext:
    """
    插件执行上下文
    
    Attributes:
        task_id: 关联的任务 ID
        agent_id: 调用的 Agent ID
        plugin_id: 插件 ID
        input_data: 输入数据
        output_data: 输出数据
        metadata: 元数据（用于传递额外信息）
        created_at: 创建时间
        updated_at: 更新时间
    """
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    plugin_id: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """初始化后处理"""
        if not self.plugin_id:
            self.plugin_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()
    
    def update(self) -> None:
        """更新时间戳"""
        self.updated_at = datetime.now()


class BasePlugin(ABC):
    """
    插件抽象基类
    
    所有插件必须继承此类并实现抽象方法。
    插件设计原则：
    1. 单一职责：每个插件只负责一个具体功能
    2. 无状态：插件之间不互相调用，数据通过记忆引擎交互
    3. 可插拔：支持动态加载和卸载
    4. 标准化：输入输出遵循统一格式
    """
    
    def __init__(self, plugin_name: str, plugin_type: PluginType, config: Optional[Dict[str, Any]] = None):
        """
        初始化插件
        
        Args:
            plugin_name: 插件名称
            plugin_type: 插件类型
            config: 插件配置（可选）
        """
        self.plugin_id = str(uuid.uuid4())
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.status = PluginStatus.INACTIVE
        self.config = config or {}
        self._initialized = False
        self._load_time: Optional[datetime] = None
        self._execute_count = 0
        self._error_count = 0
    
    @abstractmethod
    def execute(self, context: PluginContext) -> Any:
        """
        执行插件功能（必须实现）
        
        Args:
            context: 插件执行上下文
            
        Returns:
            执行结果（任意类型）
            
        Raises:
            Exception: 执行失败时抛出异常
        """
        pass
    
    @abstractmethod
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据（必须实现）
        
        Args:
            input_data: 输入数据
            
        Returns:
            验证是否通过
        """
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息（必须实现）
        
        Returns:
            插件信息字典，包含：
            - plugin_id: 插件 ID
            - plugin_name: 插件名称
            - plugin_type: 插件类型
            - status: 当前状态
            - version: 版本号
            - description: 描述
        """
        pass
    
    def initialize(self) -> bool:
        """
        初始化插件
        
        Returns:
            初始化是否成功
        """
        try:
            self.status = PluginStatus.LOADING
            self._on_initialize()
            self._initialized = True
            self._load_time = datetime.now()
            self.status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            self.status = PluginStatus.ERROR
            self._error_count += 1
            return False
    
    def shutdown(self) -> bool:
        """
        关闭插件
        
        Returns:
            关闭是否成功
        """
        try:
            self.status = PluginStatus.UNLOADING
            self._on_shutdown()
            self._initialized = False
            self.status = PluginStatus.INACTIVE
            return True
        except Exception as e:
            self.status = PluginStatus.ERROR
            self._error_count += 1
            return False
    
    def _on_initialize(self) -> None:
        """
        初始化钩子方法（子类可重写）
        
        用于执行插件特定的初始化逻辑，如：
        - 建立数据库连接
        - 加载模型
        - 初始化配置
        """
        pass
    
    def _on_shutdown(self) -> None:
        """
        关闭钩子方法（子类可重写）
        
        用于执行插件特定的清理逻辑，如：
        - 关闭数据库连接
        - 释放资源
        - 保存状态
        """
        pass
    
    def can_execute(self, context: PluginContext) -> bool:
        """
        检查插件是否可以执行
        
        Args:
            context: 插件执行上下文
            
        Returns:
            是否可以执行
        """
        if not self._initialized:
            return False
        if self.status != PluginStatus.ACTIVE:
            return False
        if not self.validate(context.input_data):
            return False
        return True
    
    def execute_with_context(self, context: PluginContext) -> Any:
        """
        带上下文管理的执行方法
        
        Args:
            context: 插件执行上下文
            
        Returns:
            执行结果
            
        Raises:
            RuntimeError: 插件未初始化或状态异常
        """
        if not self.can_execute(context):
            raise RuntimeError(
                f"Plugin {self.plugin_name} cannot execute. "
                f"Status: {self.status}, Initialized: {self._initialized}"
            )
        
        try:
            context.plugin_id = self.plugin_id
            result = self.execute(context)
            context.output_data["result"] = result
            context.update()
            self._execute_count += 1
            return result
        except Exception as e:
            self._error_count += 1
            context.output_data["error"] = str(e)
            context.update()
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取插件统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "plugin_id": self.plugin_id,
            "plugin_name": self.plugin_name,
            "execute_count": self._execute_count,
            "error_count": self._error_count,
            "load_time": self._load_time.isoformat() if self._load_time else None,
            "status": self.status.value,
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """
        计算成功率
        
        Returns:
            成功率（0-1 之间）
        """
        if self._execute_count == 0:
            return 1.0
        return (self._execute_count - self._error_count) / self._execute_count
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.plugin_name}, type={self.plugin_type.value}, status={self.status.value})"