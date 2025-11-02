# 文件: src/llm/clients/__init__.py (或 ai_caller.py)

import os
from src.llm.config import MODEL_CONFIG
from .openai_compatible import OpenAICompatibleClient
from .gemini import GeminiClient  # 假设您有 Gemini 客户端

# 将客户端类型映射到具体的类
CLIENT_MAP = {
    "openai_compatible": OpenAICompatibleClient,
    "gemini": GeminiClient,
    # 在这里添加其他客户端类型
}


def get_llm_client(model_name: str):
    """
    根据模型名称，从配置中动态创建并返回一个LLM客户端实例 (V3 - 终极健壮版)
    """
    model_conf = MODEL_CONFIG.get(model_name)
    if not model_conf:
        print(f"  - ⚠️ 警告: 在 config.py 中找不到模型 '{model_name}' 的配置。")
        return None

    client_type = model_conf.get("client_type")
    client_class = CLIENT_MAP.get(client_type)
    if not client_class:
        print(f"  - ⚠️ 警告: 找不到类型为 '{client_type}' 的客户端实现。")
        return None

    # 准备构造函数参数：复制配置，移除我们内部使用的'client_type'
    init_params = model_conf.copy()
    init_params.pop('client_type', None)

    # 将模型名称本身也作为参数传给客户端，方便客户端内部使用
    if 'model_name' not in init_params:
        init_params['model_name'] = model_name

    try:
        # 使用 **init_params 解包，将所有配置项(api_key, base_url, supports_json_mode等)
        # 作为关键字参数传递给客户端的构造函数
        return client_class(**init_params)
    except Exception as e:
        print(f"  - ❌ 错误: 创建客户端 '{client_class.__name__}' 时出错。请检查配置。错误: {e}")
        import traceback
        traceback.print_exc()
        return None