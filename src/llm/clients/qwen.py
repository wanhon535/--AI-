# src/llm/clients/qwen.py
import os
from openai import OpenAI

class QwenClient:
    def __init__(self, model_name: str, config: dict):
        self.model_name = model_name
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        if not self.api_key:
            raise ValueError(f"API key for model '{model_name}' not found.")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        print(f"✅ Qwen Client initialized for model: '{self.model_name}'")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            completion = self.client.chat.completions.create(
                model=self.model_name, messages=messages,
                response_format={"type": "json_object"}, temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Qwen API call failed: {e}")
            raise