"""大模型类插件模块"""

from .llm_base import LLMBasePlugin
from .chat_plugin import ChatPlugin
from .embedding_plugin import EmbeddingPlugin

__all__ = [
    "LLMBasePlugin",
    "ChatPlugin",
    "EmbeddingPlugin"
]