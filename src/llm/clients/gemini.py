# 文件: src/llm/clients/gemini.py

import google.generativeai as genai
# 假设您的抽象基类在这个路径
from src.llm.bash  import AbstractLLMClient


class GeminiClient(AbstractLLMClient):
    """
    适用于Google Gemini系列模型的客户端 (V2 - 优化版)。
    """

    def __init__(self, api_key: str, model_name: str, **kwargs):
        """
        在创建客户端实例时，就配置好API密钥和模型。
        """
        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            raise ValueError(f"无效的Gemini API密钥。请在 src/llm/config.py 中配置 '{model_name}' 的 api_key。")

        # --- 核心修复：将参数传递给父类 ---
        # 将 model_name 和包含所有配置的字典传递给 super().__init__()
        # 我们创建一个 config 字典来包含所有相关信息
        config_for_parent = {
            'api_key': api_key,
            'model_name': model_name,
            **kwargs  # 把其他所有额外参数也放进去
        }
        super().__init__(model_name=model_name, config=config_for_parent)
        # ------------------------------------

        # 子类自己的逻辑保持不变
        self.api_key = api_key

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            print(f"✅ Gemini客户端 '{self.model_name}' 初始化并配置成功。")
        except Exception as e:
            print(f"❌ Gemini客户端初始化失败: {e}")
            raise

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """
        使用配置好的模型生成内容。
        """
        try:
            print(f"  - ✨ [Gemini] 正在调用模型: {self.model_name}...")

            # Gemini的最佳实践是将系统提示和用户提示合并
            # 如果模型支持 system_instruction (如1.5 Pro)，则在初始化时已设置
            # 否则，我们将它和用户提示合并

            # 创建一个新的模型实例以应用 system_prompt
            # (注意: genai库的最佳实践是在每次调用时根据需要创建，特别是当system_prompt会变时)
            model_with_system_prompt = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )

            # 如果请求JSON模式，我们可以在提示中再次强调
            final_user_prompt = user_prompt
            if json_mode:
                final_user_prompt += "\n\n请确保你的回答是一个完整的、语法正确的JSON对象，不要包含任何额外的解释或Markdown标记。"

            response = model_with_system_prompt.generate_content(final_user_prompt)

            # Gemini的响应可能包含Markdown代码块的标记，我们需要清理它
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            return cleaned_text.strip()

        except Exception as e:
            print(f"  - ❌ [Gemini] 调用 {self.model_name} 时出错: {e}")
            return f'{{"error": "Gemini API call failed", "details": "{str(e)}"}}'