"""数据类插件模块"""

from .database_plugin import DatabasePlugin
from .file_plugin import FilePlugin
from .api_plugin import ApiPlugin

__all__ = [
    "DatabasePlugin",
    "FilePlugin",
    "ApiPlugin"
]