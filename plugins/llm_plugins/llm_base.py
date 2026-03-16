"""
LLM 基类插件

提供大语言模型的基础接口和通用功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generator

from ..base_plugin import BasePlugin, PluginContext, PluginType


class LLMBasePlugin(BasePlugin, ABC):
    """
    LLM 基类插件
    
    所有 LLM 相关插件必须继承此类。
    提供统一的对话、补全、嵌入等接口。
    """
    
    def __init__(self, plugin_name: str, plugin_type: PluginType, config: Optional[Dict[str, Any]] = None):
        """
        初始化 LLM 插件
        
        Args:
            plugin_name: 插件名称
            plugin_type: 插件类型（固定为 LLM）
            config: 配置参数，包含：
                - api_key: API 密钥
                - base_url: API 基础 URL
                - model: 模型名称
                - temperature: 温度参数
                - max_tokens: 最大 token 数
        """
        super().__init__(plugin_name, PluginType.LLM, config)
        self.api_key = config.get("api_key", "") if config else ""
        self.base_url = config.get("base_url", "") if config else ""
        self.model = config.get("model", "gpt-3.5-turbo") if config else "gpt-3.5-turbo"
        self.temperature = config.get("temperature", 0.7) if config else 0.7
        self.max_tokens = config.get("max_tokens", 2048) if config else 2048
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        对话接口（必须实现）
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "你好"}]
            **kwargs: 其他参数
            
        Returns:
            模型回复的文本
        """
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """
        流式对话接口（必须实现）
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Yields:
            逐步生成的回复文本
        """
        pass
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """
        文本补全接口（必须实现）
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数
            
        Returns:
            补全的文本
        """
        pass
    
    def execute(self, context: PluginContext) -> Any:
        """执行 LLM 调用"""
        input_data = context.input_data
        operation = input_data.get("operation", "chat")
        
        if operation == "chat":
            messages = input_data.get("messages", [])
            return self.chat(messages, **input_data.get("kwargs", {}))
        elif operation == "chat_stream":
            messages = input_data.get("messages", [])
            return list(self.chat_stream(messages, **input_data.get("kwargs", {})))
        elif operation == "complete":
            prompt = input_data.get("prompt", "")
            return self.complete(prompt, **input_data.get("kwargs", {}))
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "operation" not in input_data:
            return False
        
        operation = input_data["operation"]
        if operation == "chat" and "messages" not in input_data:
            return False
        if operation == "complete" and "prompt" not in input_data:
            return False
        
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        base_info = {
            "plugin_id": self.plugin_id,
            "plugin_name": self.plugin_name,
            "plugin_type": self.plugin_type.value,
            "status": self.status.value,
            "version": "1.0.0",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # 子类可以扩展此方法添加特定信息
        specific_info = self._get_specific_info()
        base_info.update(specific_info)
        
        return base_info
    
    @abstractmethod
    def _get_specific_info(self) -> Dict[str, Any]:
        """
        获取子类特定信息（必须实现）
        
        Returns:
            特定信息字典
        """
        pass
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        预处理消息列表
        
        Args:
            messages: 原始消息列表
            
        Returns:
            处理后的消息列表
        """
        processed = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                processed.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        return processed
    
    def _build_request_params(self, **kwargs) -> Dict[str, Any]:
        """
        构建请求参数
        
        Args:
            **kwargs: 额外参数
            
        Returns:
            请求参数字典
        """
        params = {
            "model": self.model,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        # 添加其他可选参数
        optional_params = ["top_p", "frequency_penalty", "presence_penalty", "stop"]
        for param in optional_params:
            if param in kwargs:
                params[param] = kwargs[param]
        
        return params