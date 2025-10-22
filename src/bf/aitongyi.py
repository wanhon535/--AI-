# ai_caller.py
from openai import OpenAI
from prompt_templates import build_lotto_pro_prompt
from database.database_manager import DatabaseManager
from typing import List, Dict


# 通义千文


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

    # 解析AI返回的结果
    response_content = completion.choices[0].message.content
    print(response_content)


    def parse_ai_recommendations(content: str) -> List[Dict]:
        """解析AI返回的推荐内容"""
        recommendations = []

        # 根据实际返回格式调整解析逻辑
        lines = content.strip().split('\n')

        for line in lines:
            if line.startswith('*') and '**' in line:
                parts = line.split('**')
                if len(parts) >= 5:
                    recommend_type = parts[0].strip('*')
                    strategy_logic = parts[1].strip()
                    front_numbers = parts[2].strip()
                    back_numbers = parts[3].strip()
                    try:
                        win_probability = float(parts[4].strip())
                    except ValueError:
                        win_probability = 0.0

                    recommendations.append({
                        "recommend_type": recommend_type,
                        "strategy_logic": strategy_logic,
                        "front_numbers": front_numbers,
                        "back_numbers": back_numbers,
                        "win_probability": win_probability
                    })

        return recommendations

    # 动态解析AI推荐结果
    try:
        recommendations_data = parse_ai_recommendations(response_content)
        print(f"✅ 成功解析 {len(recommendations_data)} 条推荐")
    except Exception as e:
        print(f"❌ 解析AI推荐失败: {e}")
        # 如果解析失败，使用预设数据作为备用
        recommendations_data = [
            {
                "recommend_type": "复式 (7+3)",
                "strategy_logic": "遵循风格 + 最强模式强化",
                "front_numbers": "06,10,12,18,21,22,25",
                "back_numbers": "01,06,08",
                "win_probability": 0.00192
            },
            {
                "recommend_type": "单式A",
                "strategy_logic": "热号精选",
                "front_numbers": "06,10,12,21,22",
                "back_numbers": "01,06",
                "win_probability": 0.00032
            }
        ]

    # 1. 插入算法推荐根记录
    root_success = db_manager.insert_algorithm_recommendation_root(
        period_number=next_issue,
        model_name="qwen3-max",
        confidence_score=0.85,
        risk_level="medium"
    )

    if not root_success:
        print("❌ 算法推荐根记录插入失败")
    else:
        print("✅ 成功插入算法推荐根记录")

        # 获取刚插入的 record_id
        last_insert_id = db_manager.execute_query("SELECT LAST_INSERT_ID();")[0]['LAST_INSERT_ID()']
        print(f"📌 推荐根记录 ID: {last_insert_id}")

        # 2. 批量插入推荐详情
        details_success = db_manager.insert_recommendation_details_batch(
            recommendation_id=last_insert_id,
            details=recommendations_data
        )
        if details_success:
            print("✅ 推荐详情已成功插入")
        else:
            print("❌ 推荐详情插入失败")

        # 3. 模拟用户购买行为（可选）
        purchases = [
            {
                "user_id": "default",
                "purchase_type": "复式",
                "front_numbers_purchased": "06,10,12,18,21,22,25",
                "back_numbers_purchased": "01,06,08",
                "cost": 42.0,
                "is_hit": False,
                "front_hit_count": 0,
                "back_hit_count": 0,
                "winnings_amount": 0.0
            },
            {
                "user_id": "default",
                "purchase_type": "单式",
                "front_numbers_purchased": "06,10,12,21,22",
                "back_numbers_purchased": "01,06",
                "cost": 2.0,
                "is_hit": False,
                "front_hit_count": 0,
                "back_hit_count": 0,
                "winnings_amount": 0.0
            },
            {
                "user_id": "default",
                "purchase_type": "单式",
                "front_numbers_purchased": "03,07,14,18,29",
                "back_numbers_purchased": "02,08",
                "cost": 2.0,
                "is_hit": False,
                "front_hit_count": 0,
                "back_hit_count": 0,
                "winnings_amount": 0.0
            }
        ]

        purchase_success = db_manager.insert_user_purchase_records_batch(
            period_metadata_id=last_insert_id,
            purchases=purchases
        )

        if purchase_success:
            print("✅ 用户购买记录已成功插入")
        else:
            print("❌ 用户购买记录插入失败")

except Exception as e:
    print(f"❌ 程序执行出错: {e}")

finally:
    # 关闭数据库连接
    db_manager.disconnect()
