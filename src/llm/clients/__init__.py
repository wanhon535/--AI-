# src/llm/__init__.py
# 包的入口点，提供一个工厂函数来创建正确的模型客户端实例。

from src.llm.config import MODEL_CONFIG
from src.llm.bash import AbstractLLMClient
from src.llm.clients.openai_compatible import OpenAICompatibleClient
from src.llm.clients.gemini import GeminiClient

def get_llm_client(model_name: str) -> AbstractLLMClient:
    """
    工厂函数，根据模型名称返回相应的LLM客户端实例。
    这是外部调用此模块的主要入口。
    """
    if model_name not in MODEL_CONFIG:
        raise ValueError(f"Model '{model_name}' is not configured in src/llm/config.py.")

    config = MODEL_CONFIG[model_name]
    client_type = config.get("client_type")

    if client_type == "openai_compatible":
        return OpenAICompatibleClient(model_name, config)
    elif client_type == "gemini":
        return GeminiClient(model_name, config)
    else:
        raise ValueError(f"Unknown client type '{client_type}' for model '{model_name}'.")