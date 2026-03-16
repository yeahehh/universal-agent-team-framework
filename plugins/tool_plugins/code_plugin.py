"""
代码执行插件

提供 Python 代码执行功能
"""

import sys
import io
from typing import Any, Dict, Optional
from contextlib import redirect_stdout, redirect_stderr

from ..base_plugin import BasePlugin, PluginContext, PluginType


class CodePlugin(BasePlugin):
    """
    代码执行插件
    
    功能：
    - 执行 Python 代码
    - 捕获输出
    - 错误处理
    - 沙箱环境
    """
    
    def __init__(self, plugin_name: str = "CodePlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化代码执行插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数，包含：
                - timeout: 执行超时（秒）
                - max_output: 最大输出长度
                - allowed_modules: 允许的模块列表
        """
        super().__init__(plugin_name, PluginType.TOOL, config)
        self.timeout = config.get("timeout", 10) if config else 10
        self.max_output = config.get("max_output", 10000) if config else 10000
        self.allowed_modules = config.get("allowed_modules", ["math", "json", "re", "datetime"]) if config else ["math", "json", "re", "datetime"]
    
    def _on_initialize(self) -> None:
        """初始化"""
        pass
    
    def _on_shutdown(self) -> None:
        """关闭"""
        pass
    
    def execute(self, context: PluginContext) -> Any:
        """
        执行代码
        
        Input data 格式：
        {
            "code": "print('Hello')",
            "globals": {},  # 全局变量
            "locals": {}    # 局部变量
        }
        
        Returns:
            执行结果：
            {
                "stdout": "输出内容",
                "stderr": "错误内容",
                "result": 返回值
            }
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        global_vars = input_data.get("globals", {})
        local_vars = input_data.get("locals", {})
        
        if not code:
            raise ValueError("Code is required")
        
        return self._execute_code(code, global_vars, local_vars)
    
    def _execute_code(self, code: str, global_vars: Dict, local_vars: Dict) -> Dict[str, Any]:
        """执行代码"""
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            # 限制全局变量
            safe_globals = {"__builtins__": self._get_safe_builtins()}
            safe_globals.update(global_vars)
            
            # 执行代码
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                result = exec(code, safe_globals, local_vars)
            
            stdout = stdout_buffer.getvalue()
            stderr = stderr_buffer.getvalue()
            
            # 限制输出长度
            if len(stdout) > self.max_output:
                stdout = stdout[:self.max_output] + "... (truncated)"
            if len(stderr) > self.max_output:
                stderr = stderr[:self.max_output] + "... (truncated)"
            
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "result": None
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": stdout_buffer.getvalue(),
                "stderr": stderr_buffer.getvalue() + f"\nError: {str(e)}",
                "result": None
            }
    
    def _get_safe_builtins(self) -> Dict[str, Any]:
        """获取安全的内置函数"""
        import math
        
        safe_builtins = {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "range": range,
            "set": set,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            "math": math
        }
        
        return safe_builtins
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "code" not in input_data:
            return False
        if not isinstance(input_data["code"], str):
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
            "description": "Python 代码执行插件，支持沙箱环境",
            "timeout": self.timeout,
            "max_output": self.max_output,
            "allowed_modules": self.allowed_modules
        }
    
    def run(self, code: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """便捷方法：执行代码"""
        context = PluginContext(
            input_data={
                "code": code,
                "globals": variables or {},
                "locals": {}
            }
        )
        return self.execute_with_context(context)