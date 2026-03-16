"""
搜索插件

提供网络搜索功能
"""

import json
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote

from ..base_plugin import BasePlugin, PluginContext, PluginType


class SearchPlugin(BasePlugin):
    """
    搜索插件
    
    功能：
    - 网络搜索
    - 新闻搜索
    - 图片搜索
    - 结果解析
    """
    
    def __init__(self, plugin_name: str = "SearchPlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化搜索插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数，包含：
                - search_engine: 搜索引擎 (google, bing, baidu)
                - api_key: API 密钥（如需使用 API）
                - results_per_page: 每页结果数
        """
        super().__init__(plugin_name, PluginType.TOOL, config)
        self.search_engine = config.get("search_engine", "google") if config else "google"
        self.api_key = config.get("api_key", "") if config else ""
        self.results_per_page = config.get("results_per_page", 10) if config else 10
    
    def _on_initialize(self) -> None:
        """初始化"""
        pass
    
    def _on_shutdown(self) -> None:
        """关闭"""
        pass
    
    def execute(self, context: PluginContext) -> Any:
        """
        执行搜索
        
        Input data 格式：
        {
            "query": "搜索关键词",
            "type": "web" | "news" | "image",
            "num_results": 10,
            "language": "zh-CN"
        }
        
        Returns:
            搜索结果列表
        """
        input_data = context.input_data
        query = input_data.get("query", "")
        search_type = input_data.get("type", "web")
        num_results = input_data.get("num_results", self.results_per_page)
        language = input_data.get("language", "zh-CN")
        
        if not query:
            raise ValueError("Search query is required")
        
        if search_type == "web":
            return self._search_web(query, num_results, language)
        elif search_type == "news":
            return self._search_news(query, num_results, language)
        elif search_type == "image":
            return self._search_images(query, num_results, language)
        else:
            raise ValueError(f"Unknown search type: {search_type}")
    
    def _search_web(self, query: str, num_results: int, language: str) -> List[Dict[str, Any]]:
        """网页搜索"""
        if self.api_key and self.search_engine == "google":
            return self._google_search(query, num_results, language)
        elif self.search_engine == "bing":
            return self._bing_search(query, num_results, language)
        else:
            return self._mock_search(query, num_results, "web")
    
    def _search_news(self, query: str, num_results: int, language: str) -> List[Dict[str, Any]]:
        """新闻搜索"""
        return self._mock_search(query, num_results, "news")
    
    def _search_images(self, query: str, num_results: int, language: str) -> List[Dict[str, Any]]:
        """图片搜索"""
        return self._mock_search(query, num_results, "image")
    
    def _google_search(self, query: str, num_results: int, language: str) -> List[Dict[str, Any]]:
        """Google 自定义搜索 API"""
        cx = self.config.get("cx", "")
        url = f"https://www.googleapis.com/customsearch/v1?q={quote(query)}&key={self.api_key}&cx={cx}&num={min(num_results, 10)}"
        
        try:
            with urlopen(url) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [
                    {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google"
                    }
                    for item in data.get("items", [])
                ]
        except Exception as e:
            raise Exception(f"Google search failed: {str(e)}")
    
    def _bing_search(self, query: str, num_results: int, language: str) -> List[Dict[str, Any]]:
        """Bing 搜索 API"""
        url = f"https://api.bing.microsoft.com/v7.0/search?q={quote(query)}&count={min(num_results, 50)}&mkt={language}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        
        try:
            request = Request(url, headers=headers)
            with urlopen(request) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [
                    {
                        "title": item.get("name", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "bing"
                    }
                    for item in data.get("webPages", {}).get("value", [])
                ]
        except Exception as e:
            raise Exception(f"Bing search failed: {str(e)}")
    
    def _mock_search(self, query: str, num_results: int, search_type: str) -> List[Dict[str, Any]]:
        """模拟搜索结果（用于测试）"""
        return [
            {
                "title": f"{search_type.title()} Result {i+1} for '{query}'",
                "link": f"https://example.com/result-{i+1}",
                "snippet": f"This is a mock {search_type} result for query: {query}",
                "source": "mock"
            }
            for i in range(num_results)
        ]
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        if "query" not in input_data:
            return False
        if not isinstance(input_data["query"], str) or not input_data["query"].strip():
            return False
        if "type" in input_data and input_data["type"] not in ["web", "news", "image"]:
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
            "description": "网络搜索插件，支持 Google、Bing 等搜索引擎",
            "search_engine": self.search_engine,
            "has_api_key": bool(self.api_key)
        }
    
    def search(self, query: str, num_results: int = 10, search_type: str = "web") -> List[Dict[str, Any]]:
        """便捷方法：执行搜索"""
        context = PluginContext(
            input_data={
                "query": query,
                "type": search_type,
                "num_results": num_results
            }
        )
        return self.execute_with_context(context)