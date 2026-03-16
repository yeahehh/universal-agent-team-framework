"""
文件操作插件

提供文件读写、解析、转换功能
"""

import os
import json
import csv
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..base_plugin import BasePlugin, PluginContext, PluginType


class FilePlugin(BasePlugin):
    """
    文件操作插件
    
    功能：
    - 读取文件内容
    - 写入文件内容
    - 解析 JSON/CSV 文件
    - 文件转换
    """
    
    def __init__(self, plugin_name: str = "FilePlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化文件插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数，包含：
                - base_dir: 基础目录
                - encoding: 默认编码
                - max_size: 最大文件大小（字节）
        """
        super().__init__(plugin_name, PluginType.DATA, config)
        self.base_dir = Path(config.get("base_dir", ".")) if config else Path(".")
        self.encoding = config.get("encoding", "utf-8") if config else "utf-8"
        self.max_size = config.get("max_size", 10 * 1024 * 1024) if config else 10 * 1024 * 1024
    
    def _on_initialize(self) -> None:
        """初始化：确保基础目录存在"""
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _on_shutdown(self) -> None:
        """关闭时清理资源"""
        pass
    
    def execute(self, context: PluginContext) -> Any:
        """
        执行文件操作
        
        Input data 格式：
        {
            "operation": "read" | "write" | "append" | "delete" | "exists",
            "file_path": "文件路径",
            "content": "内容",  # write/append 时需要
            "file_type": "txt" | "json" | "csv",  # 可选
            "encoding": "编码"  # 可选，覆盖默认编码
        }
        
        Returns:
            操作结果
        """
        input_data = context.input_data
        operation = input_data.get("operation", "read")
        file_path = input_data.get("file_path")
        content = input_data.get("content")
        file_type = input_data.get("file_type", "txt")
        encoding = input_data.get("encoding", self.encoding)
        
        if not file_path:
            raise ValueError("File path is required")
        
        full_path = self.base_dir / file_path
        
        if operation == "read":
            return self._read_file(full_path, file_type, encoding)
        elif operation == "write":
            return self._write_file(full_path, content, file_type, encoding)
        elif operation == "append":
            return self._append_file(full_path, content, file_type, encoding)
        elif operation == "delete":
            return self._delete_file(full_path)
        elif operation == "exists":
            return full_path.exists()
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _read_file(self, path: Path, file_type: str, encoding: str) -> Any:
        """读取文件"""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if path.stat().st_size > self.max_size:
            raise ValueError(f"File too large: {path.stat().st_size} > {self.max_size}")
        
        if file_type == "json":
            with open(path, "r", encoding=encoding) as f:
                return json.load(f)
        elif file_type == "csv":
            with open(path, "r", encoding=encoding, newline="") as f:
                reader = csv.DictReader(f)
                return list(reader)
        else:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
    
    def _write_file(self, path: Path, content: Any, file_type: str, encoding: str) -> bool:
        """写入文件"""
        if content is None:
            raise ValueError("Content is required for write operation")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_type == "json":
            with open(path, "w", encoding=encoding) as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        elif file_type == "csv":
            if not isinstance(content, list):
                raise ValueError("CSV content must be a list of dicts")
            with open(path, "w", encoding=encoding, newline="") as f:
                if content:
                    writer = csv.DictWriter(f, fieldnames=content[0].keys())
                    writer.writeheader()
                    writer.writerows(content)
        else:
            with open(path, "w", encoding=encoding) as f:
                f.write(str(content))
        
        return True
    
    def _append_file(self, path: Path, content: Any, file_type: str, encoding: str) -> bool:
        """追加文件"""
        if content is None:
            raise ValueError("Content is required for append operation")
        
        if file_type == "json":
            raise ValueError("JSON files do not support append operation")
        elif file_type == "csv":
            if not isinstance(content, list):
                raise ValueError("CSV content must be a list of dicts")
            with open(path, "a", encoding=encoding, newline="") as f:
                if content:
                    writer = csv.DictWriter(f, fieldnames=content[0].keys())
                    if path.stat().st_size == 0:
                        writer.writeheader()
                    writer.writerows(content)
        else:
            with open(path, "a", encoding=encoding) as f:
                f.write(str(content))
        
        return True
    
    def _delete_file(self, path: Path) -> bool:
        """删除文件"""
        if path.exists():
            path.unlink()
            return True
        return False
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "operation" not in input_data:
            return False
        if input_data["operation"] not in ["read", "write", "append", "delete", "exists"]:
            return False
        if input_data["operation"] in ["read", "write", "append", "delete"] and "file_path" not in input_data:
            return False
        if input_data["operation"] in ["write", "append"] and "content" not in input_data:
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
            "description": "文件操作插件，支持 TXT、JSON、CSV 格式",
            "base_dir": str(self.base_dir),
            "encoding": self.encoding,
            "max_size": self.max_size
        }
    
    def read_json(self, file_path: str) -> Any:
        """便捷方法：读取 JSON 文件"""
        context = PluginContext(
            input_data={
                "operation": "read",
                "file_path": file_path,
                "file_type": "json"
            }
        )
        return self.execute_with_context(context)
    
    def write_json(self, file_path: str, data: Any) -> bool:
        """便捷方法：写入 JSON 文件"""
        context = PluginContext(
            input_data={
                "operation": "write",
                "file_path": file_path,
                "file_type": "json",
                "content": data
            }
        )
        return self.execute_with_context(context)
    
    def read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """便捷方法：读取 CSV 文件"""
        context = PluginContext(
            input_data={
                "operation": "read",
                "file_path": file_path,
                "file_type": "csv"
            }
        )
        return self.execute_with_context(context)
    
    def read_text(self, file_path: str) -> str:
        """便捷方法：读取文本文件"""
        context = PluginContext(
            input_data={
                "operation": "read",
                "file_path": file_path
            }
        )
        return self.execute_with_context(context)