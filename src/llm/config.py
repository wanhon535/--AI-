# src/llm/config.py

# 最佳实践: 实际项目中应使用环境变量或专门的密钥管理服务加载API密钥
# import os
# api_key = os.environ.get("YOUR_API_KEY_NAME")

MODEL_CONFIG = {
    "qwen3-max": {
        "api_key": "sk-6753a26de53a4a2fa0efaf7e5ddafdae", # 您的通义千问密钥
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "client_type": "openai_compatible"
    },
    "gemini-1.5-pro": {
        "api_key": "YOUR_GEMINI_API_KEY", # <--- 替换为您自己的GEMINI密钥
        "client_type": "gemini"
    },
    "gpt-4o": {
        "api_key": "YOUR_OPENAI_API_KEY", # <--- 替换为您自己的OPENAI密钥
        "base_url": "https://api.openai.com/v1",
        "client_type": "openai_compatible"
    }
    # 未来可在此处添加更多模型配置
}