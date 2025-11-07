import json
from typing import Dict, Any, Optional, Callable
from src.llm.clients import get_llm_client


class LLMCallService:
    """封装 LLM 调用的服务类，用于执行三阶段推理。"""

    def __init__(self, model_name: str = "gpt-4o"):
        self.client = get_llm_client(model_name)
        self.model_name = model_name
        if not self.client:
            raise RuntimeError(f"无法初始化 LLM 客户端: {model_name}。请检查 API Key 或配置。")
        # print(f"✅ LLMCallService 初始化成功，使用模型: {model_name}") # 移到主程序打印

    def execute_strategy(self, prompt_func: Callable, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行单个 LLM 策略推理阶段。"""

        try:
            # 1. 生成提示词 (prompt_func 是 V12.0 A/B/C 的生成函数)
            prompt, _ = prompt_func(**data)
        except Exception as e:
            print(f"❌ 提示词生成失败: {prompt_func.__name__} -> {e}")
            return None

        # 2. 调用 LLM API
        try:
            # print(f"  [LLM Service] 正在调用 {self.model_name}，阶段: {prompt_func.__name__}...")

            system_instruction = "你是一名顶尖的战略分析师，请严格按照用户指定的JSON格式输出结果，不要有任何额外文字或解释。你的输出必须是合法的JSON对象。"

            response_text = self.client.call(
                prompt=prompt,
                system_instruction=system_instruction,
                json_mode=True
            )

            # 3. 解析并返回 JSON
            return json.loads(response_text)

        except Exception as e:
            print(f"  [LLM Service] ❌ LLM 调用或 JSON 解析失败: {e}")
            return None