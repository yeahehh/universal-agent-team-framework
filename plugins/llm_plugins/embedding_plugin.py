"""
嵌入插件

提供文本嵌入（Embedding）功能
"""

import json
from typing import Any, Dict, Generator, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .llm_base import LLMBasePlugin
from ..base_plugin import PluginContext, PluginType


class EmbeddingPlugin(LLMBasePlugin):
    """
    嵌入插件
    
    功能：
    - 文本嵌入
    - 批量嵌入
    - 相似度计算
    """
    
    def __init__(self, plugin_name: str = "EmbeddingPlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化嵌入插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数，包含：
                - embedding_model: 嵌入模型名称
        """
        super().__init__(plugin_name, PluginType.LLM, config)
        self.embedding_model = config.get("embedding_model", "text-embedding-ada-002") if config else "text-embedding-ada-002"
        self._cache: Dict[str, List[float]] = {}
    
    def _on_initialize(self) -> None:
        """初始化"""
        if not self.api_key:
            raise ValueError("API key is required for EmbeddingPlugin")
        if not self.base_url:
            self.base_url = "https://api.openai.com/v1"
    
    def _on_shutdown(self) -> None:
        """关闭"""
        self._cache.clear()
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """不支持对话"""
        raise NotImplementedError("EmbeddingPlugin does not support chat")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """不支持流式对话"""
        raise NotImplementedError("EmbeddingPlugin does not support stream chat")
    
    def complete(self, prompt: str, **kwargs) -> str:
        """不支持补全"""
        raise NotImplementedError("EmbeddingPlugin does not support completion")
    
    def execute(self, context: PluginContext) -> Any:
        """执行嵌入"""
        input_data = context.input_data
        texts = input_data.get("texts", [])
        
        if not texts:
            raise ValueError("Texts are required for embedding")
        
        return self.embed_texts(texts)
    
    def embed_text(self, text: str) -> List[float]:
        """
        获取单个文本的嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if text in self._cache:
            return self._cache[text]
        
        embeddings = self.embed_texts([text])
        if embeddings:
            self._cache[text] = embeddings[0]
            return embeddings[0]
        return []
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取文本嵌入
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []
        
        params = {
            "model": self.embedding_model,
            "input": texts
        }
        
        try:
            response = self._send_request(params)
            embeddings = [item["embedding"] for item in response["data"]]
            
            # 缓存结果
            for text, embedding in zip(texts, embeddings):
                self._cache[text] = embedding
            
            return embeddings
        except Exception as e:
            raise Exception(f"Embedding failed: {str(e)}")
    
    def _send_request(self, params: Dict[str, Any]) -> Any:
        """发送 API 请求"""
        url = f"{self.base_url.rstrip('/')}/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = json.dumps(params).encode("utf-8")
        request = Request(url, data=data, headers=headers, method="POST")
        
        try:
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_data = json.loads(error_body)
                raise Exception(f"HTTP Error {e.code}: {error_data.get('error', {})}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP Error {e.code}: {error_body}")
        except URLError as e:
            raise Exception(f"URL Error: {e.reason}")
    
    def _get_specific_info(self) -> Dict[str, Any]:
        """获取特定信息"""
        return {
            "description": "文本嵌入插件，支持批量处理",
            "embedding_model": self.embedding_model,
            "cache_size": len(self._cache),
            "api_base": self.base_url
        }
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        计算两个嵌入向量的余弦相似度
        
        Args:
            embedding1: 嵌入向量 1
            embedding2: 嵌入向量 2
            
        Returns:
            相似度（0-1 之间）
        """
        if not embedding1 or not embedding2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()