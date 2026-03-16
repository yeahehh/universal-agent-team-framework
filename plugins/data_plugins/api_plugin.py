"""
API 调用插件

提供 HTTP 请求功能，支持 RESTful API 调用
"""

import json
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, quote

from ..base_plugin import BasePlugin, PluginContext, PluginType


class ApiPlugin(BasePlugin):
    """
    API 调用插件
    
    功能：
    - 发送 HTTP 请求（GET、POST、PUT、DELETE）
    - 处理请求头
    - 处理请求参数
    - 解析响应数据
    """
    
    def __init__(self, plugin_name: str = "ApiPlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化 API 插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数，包含：
                - base_url: 基础 URL
                - timeout: 超时时间（秒）
                - default_headers: 默认请求头
        """
        super().__init__(plugin_name, PluginType.DATA, config)
        self.base_url = config.get("base_url", "") if config else ""
        self.timeout = config.get("timeout", 30) if config else 30
        self.default_headers = config.get("default_headers", {}) if config else {}
    
    def _on_initialize(self) -> None:
        """初始化"""
        pass
    
    def _on_shutdown(self) -> None:
        """关闭"""
        pass
    
    def execute(self, context: PluginContext) -> Any:
        """
        执行 API 调用
        
        Input data 格式：
        {
            "method": "GET" | "POST" | "PUT" | "DELETE" | "PATCH",
            "url": "完整 URL 或相对路径",
            "params": {},  # URL 参数
            "data": {},  # 请求体
            "headers": {},  # 请求头
            "is_json": true  # 是否以 JSON 格式发送
        }
        
        Returns:
            响应数据（字典或列表）
        """
        input_data = context.input_data
        method = input_data.get("method", "GET").upper()
        url = input_data.get("url")
        params = input_data.get("params", {})
        data = input_data.get("data", {})
        headers = input_data.get("headers", {})
        is_json = input_data.get("is_json", True)
        
        if not url:
            raise ValueError("URL is required")
        
        full_url = self._build_url(url, params)
        request_headers = self._build_headers(headers, is_json)
        
        try:
            request = Request(full_url, headers=request_headers, method=method)
            
            if method in ["POST", "PUT", "PATCH"] and data:
                if is_json:
                    request.data = json.dumps(data).encode("utf-8")
                else:
                    request.data = urlencode(data).encode("utf-8")
            
            with urlopen(request, timeout=self.timeout) as response:
                response_data = response.read().decode("utf-8")
                if response_data:
                    try:
                        return json.loads(response_data)
                    except json.JSONDecodeError:
                        return response_data
                return {}
        
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_data = json.loads(error_body)
            except json.JSONDecodeError:
                error_data = {"error": error_body}
            raise Exception(f"HTTP Error {e.code}: {error_data}")
        except URLError as e:
            raise Exception(f"URL Error: {e.reason}")
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def _build_url(self, url: str, params: Dict[str, Any]) -> str:
        """构建完整 URL"""
        if url.startswith("http://") or url.startswith("https://"):
            full_url = url
        else:
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        
        if params:
            query_string = urlencode(params, doseq=True)
            separator = "&" if "?" in full_url else "?"
            full_url = f"{full_url}{separator}{query_string}"
        
        return full_url
    
    def _build_headers(self, headers: Dict[str, str], is_json: bool) -> Dict[str, str]:
        """构建请求头"""
        final_headers = self.default_headers.copy()
        final_headers.update(headers)
        
        if is_json and "Content-Type" not in final_headers:
            final_headers["Content-Type"] = "application/json"
        
        return final_headers
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "url" not in input_data:
            return False
        if "method" in input_data and input_data["method"].upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
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
            "description": "API 调用插件，支持 HTTP 请求",
            "base_url": self.base_url,
            "timeout": self.timeout
        }
    
    def get(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        """便捷方法：GET 请求"""
        context = PluginContext(
            input_data={
                "method": "GET",
                "url": url,
                "params": params or {},
                "headers": headers or {}
            }
        )
        return self.execute_with_context(context)
    
    def post(self, url: str, data: Dict, params: Optional[Dict] = None, 
             headers: Optional[Dict] = None, is_json: bool = True) -> Any:
        """便捷方法：POST 请求"""
        context = PluginContext(
            input_data={
                "method": "POST",
                "url": url,
                "params": params or {},
                "data": data,
                "headers": headers or {},
                "is_json": is_json
            }
        )
        return self.execute_with_context(context)
    
    def put(self, url: str, data: Dict, params: Optional[Dict] = None,
            headers: Optional[Dict] = None, is_json: bool = True) -> Any:
        """便捷方法：PUT 请求"""
        context = PluginContext(
            input_data={
                "method": "PUT",
                "url": url,
                "params": params or {},
                "data": data,
                "headers": headers or {},
                "is_json": is_json
            }
        )
        return self.execute_with_context(context)
    
    def delete(self, url: str, params: Optional[Dict] = None,
               headers: Optional[Dict] = None) -> Any:
        """便捷方法：DELETE 请求"""
        context = PluginContext(
            input_data={
                "method": "DELETE",
                "url": url,
                "params": params or {},
                "headers": headers or {}
            }
        )
        return self.execute_with_context(context)