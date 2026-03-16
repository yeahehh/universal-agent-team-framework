"""
对话插件

基于 OpenAI API 的对话功能实现
"""

import json
from typing import Any, Dict, Generator, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .llm_base import LLMBasePlugin
from ..base_plugin import PluginContext, PluginType

class ChatPlugin(LLMBasePlugin):
    """
    对话插件
    
    功能：
    - 多轮对话
    - 流式输出
    - 上下文管理
    """
    
    def __init__(self, plugin_name: str = "ChatPlugin", config: Optional[Dict[str, Any]] = None):
        """
        初始化对话插件
        
        Args:
            plugin_name: 插件名称
            config: 配置参数，继承 LLMBasePlugin 的配置
        """
        super().__init__(plugin_name, PluginType.LLM, config)
        self._conversation_history: List[Dict[str, str]] = []
    
    def _on_initialize(self) -> None:
        """初始化"""
        if not self.api_key:
            raise ValueError("API key is required for ChatPlugin")
        if not self.base_url:
            self.base_url = "https://api.openai.com/v1"
    
    def _on_shutdown(self) -> None:
        """关闭"""
        self.clear_history()
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送对话请求"""
        processed_messages = self._prepare_messages(messages)
        params = self._build_request_params(**kwargs)
        params["messages"] = processed_messages
        
        try:
            response = self._send_request(params, stream=False)
            content = response["choices"][0]["message"]["content"]
            
            # 保存对话历史
            self._conversation_history.extend(processed_messages)
            self._conversation_history.append({"role": "assistant", "content": content})
            
            return content
        except Exception as e:
            raise Exception(f"Chat failed: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """流式对话"""
        processed_messages = self._prepare_messages(messages)
        params = self._build_request_params(**kwargs)
        params["messages"] = processed_messages
        params["stream"] = True
        
        try:
            full_response = ""
            for chunk in self._send_request(params, stream=True):
                if chunk:
                    yield chunk
                    full_response += chunk
            
            # 保存对话历史
            self._conversation_history.extend(processed_messages)
            self._conversation_history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            raise Exception(f"Stream chat failed: {str(e)}")
    
    def complete(self, prompt: str, **kwargs) -> str:
        """文本补全"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def _send_request(self, params: Dict[str, Any], stream: bool = False) -> Any:
        """发送 API 请求"""
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = json.dumps(params).encode("utf-8")
        request = Request(url, data=data, headers=headers, method="POST")
        
        try:
            with urlopen(request, timeout=60) as response:
                response_data = response.read().decode("utf-8")
                
                if stream:
                    return self._parse_stream_response(response_data)
                else:
                    return json.loads(response_data)
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_data = json.loads(error_body)
                raise Exception(f"HTTP Error {e.code}: {error_data.get('error', {})}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP Error {e.code}: {error_body}")
        except URLError as e:
            raise Exception(f"URL Error: {e.reason}")
    
    def _parse_stream_response(self, response_data: str) -> Generator[str, None, None]:
        """解析流式响应"""
        for line in response_data.split("\n"):
            if line.startswith("data: "):
                data = line[6:]
                if data.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    content = chunk["choices"][0]["delta"].get("content", "")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
    
    def _get_specific_info(self) -> Dict[str, Any]:
        """获取特定信息"""
        return {
            "description": "OpenAI 对话插件，支持流式输出",
            "conversation_length": len(self._conversation_history),
            "api_base": self.base_url
        }
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self._conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self._conversation_history.copy()
    
    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示"""
        # 移除旧的系统提示
        self._conversation_history = [
            msg for msg in self._conversation_history if msg["role"] != "system"
        ]
        # 添加新的系统提示
        self._conversation_history.insert(0, {"role": "system", "content": prompt})