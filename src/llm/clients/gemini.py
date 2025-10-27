# src/llm/clients/gemini.py
# 为Google Gemini模型提供具体实现

import google.generativeai as genai
from src.llm.base import AbstractLLMClient


class GeminiClient(AbstractLLMClient):
    """
    适用于Google Gemini模型的客户端。
    """

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            print(f"✨ [Gemini] Calling model: {self.model_name}...")
            genai.configure(api_key=self.config["api_key"])

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )

            response = model.generate_content(user_prompt)
            return response.text
        except Exception as e:
            print(f"❌ [Gemini] Error calling {self.model_name}: {e}")
            return f"Error: Could not get a response from {self.model_name}."