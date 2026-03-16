"""
数据库操作插件

提供数据库连接和 CRUD 操作功能
"""

from typing import Any, Dict, Optional, List
from ..base_plugin import BasePlugin, PluginContext, PluginType


class DatabasePlugin(BasePlugin):
    """
    数据库操作插件
    
    功能：
    - 连接数据库
    - 执行 SQL 查询
    - 执行 CRUD 操作
    - 事务管理
    """
    
    def __init__(self, plugin_name: str = "DatabasePlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化数据库插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数，包含：
                - db_type: 数据库类型 (mysql, postgresql, sqlite 等)
                - host: 数据库主机
                - port: 数据库端口
                - database: 数据库名
                - username: 用户名
                - password: 密码
        """
        super().__init__(plugin_name, PluginType.DATA, config)
        self._connection = None
        self._db_type = config.get("db_type", "sqlite") if config else "sqlite"
    
    def _on_initialize(self) -> None:
        """初始化数据库连接"""
        db_type = self.config.get("db_type", "sqlite")
        if db_type == "sqlite":
            self._init_sqlite()
        elif db_type == "mysql":
            self._init_mysql()
        elif db_type == "postgresql":
            self._init_postgresql()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _init_sqlite(self) -> None:
        """初始化 SQLite 连接"""
        import sqlite3
        db_path = self.config.get("database", ":memory:")
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
    
    def _init_mysql(self) -> None:
        """初始化 MySQL 连接"""
        try:
            import pymysql
            self._connection = pymysql.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 3306),
                database=self.config.get("database", ""),
                user=self.config.get("username", "root"),
                password=self.config.get("password", ""),
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
        except ImportError:
            raise ImportError("Please install pymysql: pip install pymysql")
    
    def _init_postgresql(self) -> None:
        """初始化 PostgreSQL 连接"""
        try:
            import psycopg2
            self._connection = psycopg2.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 5432),
                database=self.config.get("database", ""),
                user=self.config.get("username", "postgres"),
                password=self.config.get("password", "")
            )
        except ImportError:
            raise ImportError("Please install psycopg2: pip install psycopg2")
    
    def _on_shutdown(self) -> None:
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute(self, context: PluginContext) -> Any:
        """
        执行数据库操作
        
        Input data 格式：
        {
            "operation": "query" | "insert" | "update" | "delete" | "execute",
            "sql": "SQL 语句",
            "params": [],  # 可选，参数列表
            "fetch": "one" | "all" | "none"  # 可选，查询结果获取方式
        }
        
        Returns:
            查询结果或受影响的行数
        """
        input_data = context.input_data
        operation = input_data.get("operation", "query")
        sql = input_data.get("sql")
        params = input_data.get("params", [])
        fetch_mode = input_data.get("fetch", "all")
        
        if not sql:
            raise ValueError("SQL statement is required")
        
        cursor = self._connection.cursor()
        
        try:
            if operation == "query":
                cursor.execute(sql, params if params else ())
                if fetch_mode == "one":
                    result = cursor.fetchone()
                elif fetch_mode == "all":
                    result = cursor.fetchall()
                else:
                    result = []
            elif operation in ["insert", "update", "delete"]:
                cursor.execute(sql, params if params else ())
                self._connection.commit()
                result = cursor.rowcount
            elif operation == "execute":
                cursor.execute(sql, params if params else ())
                self._connection.commit()
                result = {"rowcount": cursor.rowcount}
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # 转换结果为字典格式
            if hasattr(result, "__iter__") and not isinstance(result, (str, bytes, int)):
                result = [dict(row) if hasattr(row, "keys") else row for row in result]
            
            return result
        finally:
            cursor.close()
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "operation" not in input_data:
            return False
        if input_data["operation"] not in ["query", "insert", "update", "delete", "execute"]:
            return False
        if input_data["operation"] != "query" and "sql" not in input_data:
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
            "description": "数据库操作插件，支持 SQLite、MySQL、PostgreSQL",
            "db_type": self._db_type
        }
    
    def execute_query(self, sql: str, params: Optional[List] = None, fetch: str = "all") -> Any:
        """
        便捷方法：执行查询
        
        Args:
            sql: SQL 查询语句
            params: 参数列表
            fetch: 获取方式 (one/all)
            
        Returns:
            查询结果
        """
        context = PluginContext(
            input_data={
                "operation": "query",
                "sql": sql,
                "params": params or [],
                "fetch": fetch
            }
        )
        return self.execute_with_context(context)
    
    def execute_update(self, sql: str, params: Optional[List] = None) -> int:
        """
        便捷方法：执行更新/插入/删除
        
        Args:
            sql: SQL 语句
            params: 参数列表
            
        Returns:
            受影响的行数
        """
        context = PluginContext(
            input_data={
                "operation": "update",
                "sql": sql,
                "params": params or []
            }
        )
        return self.execute_with_context(context)