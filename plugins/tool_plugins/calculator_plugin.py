"""
计算器插件

提供数学计算功能
"""

import ast
import operator
from typing import Any, Dict, List, Optional, Union

from ..base_plugin import BasePlugin, PluginContext, PluginType


class CalculatorPlugin(BasePlugin):
    """
    计算器插件
    
    功能：
    - 基础运算（加减乘除）
    - 高级运算（幂、开方、三角函数）
    - 表达式解析
    - 安全计算
    """
    
    def __init__(self, plugin_name: str = "CalculatorPlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化计算器插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数
        """
        super().__init__(plugin_name, PluginType.TOOL, config)
        self._operators = self._init_operators()
    
    def _init_operators(self) -> Dict[type, Dict[str, callable]]:
        """初始化支持的运算符"""
        import math
        
        return {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
    
    def _on_initialize(self) -> None:
        """初始化"""
        pass
    
    def _on_shutdown(self) -> None:
        """关闭"""
        pass
    
    def execute(self, context: PluginContext) -> Any:
        """
        执行计算
        
        Input data 格式：
        {
            "expression": "1 + 2 * 3",
            "precision": 10  # 小数精度
        }
        
        Returns:
            计算结果
        """
        input_data = context.input_data
        expression = input_data.get("expression", "")
        precision = input_data.get("precision", 10)
        
        if not expression:
            raise ValueError("Expression is required")
        
        result = self._safe_eval(expression)
        
        if isinstance(result, float):
            result = round(result, precision)
        
        return result
    
    def _safe_eval(self, expression: str) -> Union[int, float]:
        """
        安全计算表达式
        
        Args:
            expression: 数学表达式
            
        Returns:
            计算结果
            
        Raises:
            ValueError: 表达式不安全或无效
        """
        try:
            node = ast.parse(expression, mode="eval").body
            return self._eval_node(node)
        except Exception as e:
            raise ValueError(f"Invalid expression: {expression}. Error: {str(e)}")
    
    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """评估 AST 节点"""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self._operators:
                return self._operators[op_type](left, right)
            else:
                raise ValueError(f"Unsupported operator: {op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self._operators:
                return self._operators[op_type](operand)
            else:
                raise ValueError(f"Unsupported unary operator: {op_type}")
        else:
            raise ValueError(f"Unsupported expression element: {type(node)}")
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "expression" not in input_data:
            return False
        if not isinstance(input_data["expression"], str):
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
            "description": "计算器插件，支持安全数学表达式计算"
        }
    
    def calculate(self, expression: str, precision: int = 10) -> Union[int, float]:
        """便捷方法：计算表达式"""
        context = PluginContext(
            input_data={
                "expression": expression,
                "precision": precision
            }
        )
        return self.execute_with_context(context)
    
    def evaluate(self, expression: str, variables: Optional[Dict[str, float]] = None) -> Union[int, float]:
        """
        评估带变量的表达式
        
        Args:
            expression: 表达式
            variables: 变量字典
            
        Returns:
            计算结果
        """
        if variables:
            for var_name, var_value in variables.items():
                expression = expression.replace(var_name, str(var_value))
        return self.calculate(expression)