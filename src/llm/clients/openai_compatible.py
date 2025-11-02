# 文件: src/llm/clients/openai_compatible.py
from openai import OpenAI
from src.llm.bash import AbstractLLMClient # 假设基类在这里

class OpenAICompatibleClient(AbstractLLMClient):
    def __init__(self, api_key: str, base_url: str, model_name: str, **kwargs):
        if not api_key: raise ValueError("API key is required")
        config_for_parent = {'api_key': api_key, 'base_url': base_url, 'model_name': model_name, **kwargs}
        super().__init__(model_name=model_name, config=config_for_parent)
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.supports_json_mode = kwargs.get('supports_json_mode', False)

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        request_params = {"model": self.model_name, "messages": messages, "temperature": 0.5}
        if json_mode and self.supports_json_mode:
            print("    - ✨ 启用原生JSON模式进行API调用。")
            request_params["response_format"] = {"type": "json_object"}
        try:
            completion = self.client.chat.completions.create(**request_params)
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"    - ❌ OpenAI API调用失败: {e}")
            return f'{{"error": "API call failed", "details": "{str(e)}"}}'