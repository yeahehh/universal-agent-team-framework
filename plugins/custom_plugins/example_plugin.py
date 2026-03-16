"""
示例自定义插件

这是一个自定义插件的示例模板，展示如何创建自己的插件
"""

from typing import Any, Dict, Optional

from ..base_plugin import BasePlugin, PluginContext, PluginType


class ExamplePlugin(BasePlugin):
    """
    示例自定义插件
    
    功能：
    - 演示插件的基本结构
    - 展示如何实现必要的方法
    - 可作为自定义插件的模板
    """
    
    def __init__(self, plugin_name: str = "ExamplePlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化示例插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数
        """
        super().__init__(plugin_name, PluginType.CUSTOM, config)
        self.custom_param = config.get("custom_param", "default") if config else "default"
    
    def _on_initialize(self) -> None:
        """初始化钩子"""
        pass
    
    def _on_shutdown(self) -> None:
        """关闭钩子"""
        pass
    
    def execute(self, context: PluginContext) -> Any:
        """
        执行插件功能
        
        Input data 格式：
        {
            "action": "process",
            "data": {}
        }
        
        Returns:
            处理结果
        """
        input_data = context.input_data
        action = input_data.get("action", "process")
        data = input_data.get("data", {})
        
        if action == "process":
            return self._process_data(data)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据"""
        return {
            "status": "success",
            "processed_data": data,
            "custom_param": self.custom_param
        }
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "action" not in input_data:
            return False
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            "plugin_id": self.plugin_id,
            "plugin_name": self.plugin_name,
            "plugin_type": self.plugin_type.value,
            "status": self.status.value,
            "version": "1.0.0",
            "description": "示例自定义插件，可作为模板使用",
            "custom_param": self.custom_param
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """便捷方法：处理数据"""
        context = PluginContext(
            input_data={
                "action": "process",
                "data": data
            }
        )
        return self.execute_with_context(context)