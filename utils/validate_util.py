"""验证工具模块
提供数据验证相关的辅助功能
"""
import re
from typing import Any, Dict, List, Optional, Union


class ValidateUtil:
    """验证工具类"""
    
    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """检查是否不为空"""
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, (list, dict, tuple, set)) and len(value) == 0:
            return False
        return True
    
    @staticmethod
    def is_empty(value: Any) -> bool:
        """检查是否为空"""
        return not ValidateUtil.is_not_empty(value)
    
    @staticmethod
    def is_string(value: Any) -> bool:
        """检查是否是字符串"""
        return isinstance(value, str)
    
    @staticmethod
    def is_integer(value: Any) -> bool:
        """检查是否是整数"""
        return isinstance(value, int) and not isinstance(value, bool)
    
    @staticmethod
    def is_float(value: Any) -> bool:
        """检查是否是浮点数"""
        return isinstance(value, float)
    
    @staticmethod
    def is_number(value: Any) -> bool:
        """检查是否是数字"""
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    
    @staticmethod
    def is_boolean(value: Any) -> bool:
        """检查是否是布尔值"""
        return isinstance(value, bool)
    
    @staticmethod
    def is_list(value: Any) -> bool:
        """检查是否是列表"""
        return isinstance(value, list)
    
    @staticmethod
    def is_dict(value: Any) -> bool:
        """检查是否是字典"""
        return isinstance(value, dict)
    
    @staticmethod
    def is_email(value: str) -> bool:
        """检查是否是有效的邮箱地址"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_phone(value: str) -> bool:
        """检查是否是有效的手机号（中国大陆）"""
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_url(value: str) -> bool:
        """检查是否是有效的 URL"""
        pattern = r'^https?://[^\s]+$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_chinese(value: str) -> bool:
        """检查是否包含中文"""
        pattern = r'[\u4e00-\u9fff]'
        return bool(re.search(pattern, value))
    
    @staticmethod
    def is_alpha(value: str) -> bool:
        """检查是否只包含字母"""
        return value.isalpha()
    
    @staticmethod
    def is_alphanumeric(value: str) -> bool:
        """检查是否只包含字母和数字"""
        return value.isalnum()
    
    @staticmethod
    def is_numeric(value: str) -> bool:
        """检查是否只包含数字"""
        return value.isnumeric()
    
    @staticmethod
    def length_between(value: str, min_len: int, max_len: int) -> bool:
        """检查长度是否在范围内"""
        length = len(value)
        return min_len <= length <= max_len
    
    @staticmethod
    def min_length(value: str, min_len: int) -> bool:
        """检查最小长度"""
        return len(value) >= min_len
    
    @staticmethod
    def max_length(value: str, max_len: int) -> bool:
        """检查最大长度"""
        return len(value) <= max_len
    
    @staticmethod
    def in_range(value: Union[int, float], min_val: Union[int, float],
                 max_val: Union[int, float]) -> bool:
        """检查数值是否在范围内"""
        return min_val <= value <= max_val
    
    @staticmethod
    def in_list(value: Any, items: List[Any]) -> bool:
        """检查是否在列表中"""
        return value in items
    
    @staticmethod
    def contains(value: str, substring: str) -> bool:
        """检查是否包含子字符串"""
        return substring in value
    
    @staticmethod
    def starts_with(value: str, prefix: str) -> bool:
        """检查是否以指定前缀开始"""
        return value.startswith(prefix)
    
    @staticmethod
    def ends_with(value: str, suffix: str) -> bool:
        """检查是否以指定后缀结束"""
        return value.endswith(suffix)
    
    @staticmethod
    def match_pattern(value: str, pattern: str) -> bool:
        """检查是否匹配正则表达式"""
        return bool(re.match(pattern, value))
    
    @staticmethod
    def validate_required(data: Dict[str, Any], required_fields: List[str]) -> tuple:
        """
        验证必填字段
        
        Args:
            data: 数据字典
            required_fields: 必填字段列表
            
        Returns:
            (是否通过，错误消息)
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or ValidateUtil.is_empty(data[field]):
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"缺少必填字段：{', '.join(missing_fields)}"
        return True, ""
    
    @staticmethod
    def validate_types(data: Dict[str, Any], type_rules: Dict[str, type]) -> tuple:
        """
        验证字段类型
        
        Args:
            data: 数据字典
            type_rules: 类型规则字典 {字段名：期望类型}
            
        Returns:
            (是否通过，错误消息)
        """
        for field, expected_type in type_rules.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    return False, f"字段 {field} 类型错误，期望 {expected_type.__name__}"
        return True, ""


# 快捷函数
def is_not_empty(value: Any) -> bool:
    return ValidateUtil.is_not_empty(value)


def is_empty(value: Any) -> bool:
    return ValidateUtil.is_empty(value)


def is_email(value: str) -> bool:
    return ValidateUtil.is_email(value)


def is_phone(value: str) -> bool:
    return ValidateUtil.is_phone(value)


def is_url(value: str) -> bool:
    return ValidateUtil.is_url(value)