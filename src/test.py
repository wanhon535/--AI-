
# ai_caller.py
import os
from openai import OpenAI
from prompt_templates import build_lotto_pro_prompt
from database.database_manager import DatabaseManager
import json
# 通义千文模型

# 初始化数据库管理器
db_manager = DatabaseManager(
    host='localhost',
    user='root',
    password='123456789',
    database='lottery_analysis_system',
    port=3309
)

# 建立数据库连接
if not db_manager.connect():
    print("数据库连接失败")
    exit(1)



try:
    # 从数据库获取数据
    recent_draws = db_manager.get_latest_lottery_history(50)  # 获取最近50期开奖数据
    print(f"获取到 {len(recent_draws)} 期历史数据")
    if recent_draws:
        print(f"最新期号: {recent_draws[0].period_number}")

    user_bets = db_manager.get_user_bets('default', 20)  # 获取用户最近20笔投注记录

    # 获取下一期期号
    next_issue = db_manager.get_next_period_number()
    print(f"预测期号: {next_issue}")

    # 构建提示词
    PROMPT_TEMPLATE_CONTENT, next_issue_result = build_lotto_pro_prompt(
        recent_draws=recent_draws,
        user_bets=user_bets,
        game_name="超级大乐透",
        next_issue_hint=next_issue
    )

    client = OpenAI(
        api_key="sk-6753a26de53a4a2fa0efaf7e5ddafdae",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": PROMPT_TEMPLATE_CONTENT},
            {"role": "user", "content": "帮我预测分析下一期的彩票号码"},
        ],
    )

    # 解析AI返回的结果（简化处理）
    response_content = completion.choices[0].message.content
    print(response_content)

    # 保存推荐记录到数据库（示例数据，实际应解析AI返回结果）
    # 这里需要根据实际返回结果进行解析和保存

finally:
    # 关闭数据库连接
    db_manager.disconnect()
