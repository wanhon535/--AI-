# src/llm/base.py
# 定义LLM客户端的抽象基类（ABC），作为统一的接口契约

from abc import ABC, abstractmethod
from typing import Dict

class AbstractLLMClient(ABC):
    """
    所有LLM客户端的抽象基类。
    它定义了一个所有具体实现都必须遵循的通用接口。
    """
    def __init__(self, model_name: str, config: Dict):
        self.model_name = model_name
        self.config = config
        self._validate_config()

    def _validate_config(self):
        """验证必要的配置项是否存在。"""
        if "api_key" not in self.config:
            raise ValueError(f"Configuration for model '{self.model_name}' is missing 'api_key'.")

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        从LLM生成内容的核心方法。

        :param system_prompt: 系统级指令。
        :param user_prompt: 用户 конкретный запрос.
        :return: LLM生成的文本响应。
        """
        pass