# src/llm/llm_call_service.py
import json
from openai import OpenAI
from typing import Callable, Dict, Any, Tuple

# --- 核心修改：像 4o.py 一样导入 MODEL_CONFIG ---
try:
    from src.llm.config import MODEL_CONFIG
except ImportError:
    print("❌ 严重错误: 无法从 'src/llm/config.py' 导入 'MODEL_CONFIG'。请检查文件是否存在且拼写正确。")
    MODEL_CONFIG = {}


class LLMCallService:
    """
    一个专门负责调用大语言模型并处理其响应的服务。
    [已更新] 初始化逻辑完全遵循项目配置规范 (参考 4o.py)。
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

        # 1. 从 MODEL_CONFIG 获取指定模型的配置
        model_config = MODEL_CONFIG.get(model_name)

        # 2. 检查配置是否存在
        if not model_config:
            raise RuntimeError(
                f"无法初始化 LLM 客户端: {model_name}。\n"
                f"  - ⚠️ 警告: 在 config.py 中找不到模型 '{model_name}' 的配置。"
            )

        api_key = model_config.get("api_key")
        base_url = model_config.get("base_url")

        # 3. 检查 key 和 url 是否有效
        if not api_key or not base_url:
            raise ValueError(f"模型 '{model_name}' 的配置不完整，缺少 'api_key' 或 'base_url'。")

        # 4. 使用获取到的配置初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        print(f"[LLM Service] 客户端已为模型 '{self.model_name}' 成功初始化 (从 config.py 加载)。")

    def execute_strategy(self, prompt_builder: Callable[..., Tuple[str, str]], context: Dict[str, Any]) -> Dict[
        str, Any]:
        """
        执行一个策略阶段的LLM调用。
        """
        stage_name = prompt_builder.__name__.replace('build_', '').replace('_prompt', '')
        print(f"\n--- [LLM Service] 正在执行阶段: {stage_name.upper()} ---")

        try:
            # 1. 生成Prompt
            prompt_content, issue = prompt_builder(**context)
            print(f"  [LLM Service] Prompt已为期号 {issue} 生成。")

            # 2. 调用LLM (使用与 4o.py 类似的 payload 结构)
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system",
                     "content": "You are a highly intelligent assistant that strictly follows user instructions and output formats."},
                    {"role": "user", "content": prompt_content},
                ],
                # 开启JSON模式，确保返回的是有效的JSON
                response_format={"type": "json_object"}
            )
            response_content = completion.choices[0].message.content
            print(f"  [LLM Service] LLM响应接收成功。")

            # 3. 解析JSON响应
            parsed_json = json.loads(response_content)
            print(f"  [LLM Service] JSON响应解析成功。")
            return parsed_json

        except json.JSONDecodeError as e:
            print(f"  [LLM Service] ❌ 错误: LLM返回的不是有效的JSON。错误: {e}")
            # 打印原始响应以便调试
            if 'response_content' in locals():
                print(f"  [LLM Service] 原始响应片段: {response_content[:500]}...")
            return {}
        except Exception as e:
            print(f"  [LLM Service] ❌ 错误: 在执行 {stage_name} 阶段时发生未知错误: {e}")
            import traceback
            traceback.print_exc()
            return {}