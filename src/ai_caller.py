
# ai_caller.py
from openai import OpenAI
from prompt_templates import build_lotto_pro_prompt
from database.database_manager import DatabaseManager


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

    recommendations_data = [
        {
            "recommend_type": "热号主攻",
            "strategy_logic": "遵循最强模式 + 热号集中",
            "front_numbers": "06,10,12,21,22",
            "back_numbers": "01,06",
            "win_probability": "0.00032"
        },
        {
            "recommend_type": "冷号回补",
            "strategy_logic": "模式+冷号突破",
            "front_numbers": "03,07,14,18,29",
            "back_numbers": "02,08",
            "win_probability": "0.00031"
        },
        {
            "recommend_type": "复式 (6+3)",
            "strategy_logic": "遵循风格 + 最强模式强化",
            "front_numbers": "06,10,12,18,21,22",
            "back_numbers": "01,06,08",
            "win_probability": "0.00192"
        },
        {
            "recommend_type": "复式 (8+3)",
            "strategy_logic": "综合高潜力池全覆盖",
            "front_numbers": "03,06,07,10,12,18,21,22",
            "back_numbers": "01,06,08",
            "win_probability": "0.00512"
        }
    ]

    # 保存推荐结果到数据库并检查完整性
    save_result = db_manager.save_recommendations(next_issue, "qwen3-max-v1.0", recommendations_data)

    if save_result["success"]:
        print(f"✅ 推荐结果已完整保存到数据库 ({save_result['saved_count']}/{save_result['total_expected']})")
    elif save_result["saved_count"] > 0:
        print(f"⚠️  部分推荐结果保存成功 ({save_result['saved_count']}/{save_result['total_expected']})")
        for error in save_result["errors"]:
            print(f"   - {error}")
    else:
        print("❌ 推荐结果保存失败")
        for error in save_result["errors"]:
            print(f"   - {error}")

    # 保存推荐记录到数据库（示例数据，实际应解析AI返回结果）
    # 这里需要根据实际返回结果进行解析和保存

finally:
    # 关闭数据库连接
    db_manager.disconnect()
