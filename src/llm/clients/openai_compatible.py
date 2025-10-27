# src/llm/clients/openai_compatible.py
# 为所有兼容OpenAI SDK的API（如通义千问、GPT系列）提供具体实现

from openai import OpenAI
from src.llm.bash import AbstractLLMClient

class OpenAICompatibleClient(AbstractLLMClient):
    """
    适用于OpenAI、通义千问等兼容OpenAI API格式的模型客户端。
    """
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            print(f"🧠 [OpenAI-Compatible] Calling model: {self.model_name}...")
            client = OpenAI(
                api_key=self.config["api_key"],
                base_url=self.config.get("base_url"),
            )
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"❌ [OpenAI-Compatible] Error calling {self.model_name}: {e}")
            return f"Error: Could not get a response from {self.model_name}."