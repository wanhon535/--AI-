# ai_caller.py
from openai import OpenAI
from prompt_templates import build_lotto_pro_prompt
from database.database_manager import DatabaseManager
from typing import List, Dict
import re


def analyze_recommendation_performance(period_number: str) -> Dict:
    """
    分析某期推荐结果的表现（命中情况）
    :param period_number: 期号
    :return: 分析结果字典
    """
    try:
        # 使用全局 db_manager 实例（已在 ai_caller.py 中初始化）
        from src.database.database_manager import DatabaseManager
        db_manager = DatabaseManager(
            host='localhost',
            user='root',
            password='root',
            database='lottery_analysis_system',
            port=3307
        )
        if not db_manager.connect():
            raise Exception("数据库连接失败")

        # 1. 查询该期实际开奖数据
        query_lottery = """
        SELECT 
            front_area_1, front_area_2, front_area_3, front_area_4, front_area_5,
            back_area_1, back_area_2
        FROM lottery_history 
        WHERE period_number = %s
        """
        lottery_result = db_manager.execute_query(query_lottery, (period_number,))
        if not lottery_result:
            return {"error": "未找到该期开奖数据"}

        # 提取开奖号码
        actual_front = set([
            lottery_result[0]["front_area_1"], lottery_result[0]["front_area_2"],
            lottery_result[0]["front_area_3"], lottery_result[0]["front_area_4"], lottery_result[0]["front_area_5"]
        ])
        actual_back = set([
            lottery_result[0]["back_area_1"], lottery_result[0]["back_area_2"]
        ])

        # 2. 查询该期推荐数据
        query_recommend = """
        SELECT 
            front_numbers, back_numbers
        FROM recommendation_details 
        WHERE recommendation_metadata_id IN (
            SELECT id FROM algorithm_recommendation WHERE period_number = %s
        )
        """
        recommendations = db_manager.execute_query(query_recommend, (period_number,))

        # 3. 分析每条推荐的命中情况
        results = []
        for rec in recommendations:
            front_nums = set(map(int, rec["front_numbers"].split(',')))
            back_nums = set(map(int, rec["back_numbers"].split(',')))

            front_hit = len(front_nums & actual_front)
            back_hit = len(back_nums & actual_back)

            results.append({
                "front_hit": front_hit,
                "back_hit": back_hit,
                "total_hit": front_hit + back_hit,
                "front_numbers": rec["front_numbers"],
                "back_numbers": rec["back_numbers"]
            })

        return {
            "period_number": period_number,
            "actual_front": list(actual_front),
            "actual_back": list(actual_back),
            "recommendations": results,
            "total_recommendations": len(results)
        }

    except Exception as e:
        print(f"❌ 分析推荐表现失败: {e}")
        return {"error": str(e)}

analysis = analyze_recommendation_performance("2025068")
print(analysis)

# 初始化数据库管理器
db_manager = DatabaseManager(
    host='localhost',
    user='root',
    password='root',
    database='lottery_analysis_system',
    port=3307
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
        """
        解析AI返回的推荐内容（支持Markdown表格和加粗格式）。
        该优化版本能更稳定地处理表头、分隔线和数据行。
        """
        recommendations = []
        if not content:
            return recommendations

        lines = content.strip().split('\n')

        # 1. 找到表格的表头行索引
        header_index = -1
        for i, line in enumerate(lines):
            # 表头通常包含“推荐类型”等关键词
            if "推荐类型" in line and "策略逻辑" in line and line.strip().startswith('|'):
                header_index = i
                break

        if header_index == -1:
            print("❌ 解析失败：未在内容中找到推荐表格的表头。")
            return recommendations

        # 2. 确定数据开始的行（智能跳过表头和分隔线）
        data_start_index = header_index + 1
        # 检查表头下方是否存在分隔线 `|---|...`，如果存在则跳过
        if data_start_index < len(lines) and '---' in lines[data_start_index]:
            data_start_index += 1

        # 3. 编译正则表达式以提高效率，用于逐行解析数据
        # 这个表达式匹配五个被'|'包围的单元格，并捕获它们的内容
        pattern = re.compile(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')

        # 4. 从数据起始行开始遍历
        for i in range(data_start_index, len(lines)):
            line = lines[i].strip()

            # 如果行不是以'|'开头，说明表格内容已结束
            if not line.startswith('|'):
                break

            match = pattern.match(line)
            if not match:
                continue  # 如果行格式不匹配，跳过

            try:
                # 依次提取五个分组的内容，并使用 re.sub() 清理加粗标记 '**' 和两端空格
                recommend_type = re.sub(r'\*\*', '', match.group(1)).strip()
                strategy_logic = re.sub(r'\*\*', '', match.group(2)).strip()
                front_numbers = re.sub(r'\*\*', '', match.group(3)).strip()
                back_numbers = re.sub(r'\*\*', '', match.group(4)).strip()
                # 清理概率字符串后，再转换为浮点数
                win_probability_str = re.sub(r'\*\*', '', match.group(5)).strip()
                win_probability = float(win_probability_str)

                recommendations.append({
                    "recommend_type": recommend_type,
                    "strategy_logic": strategy_logic,
                    "front_numbers": front_numbers,
                    "back_numbers": back_numbers,
                    "win_probability": win_probability
                })
            except (ValueError, IndexError) as e:
                # 如果概率无法转换为浮点数或分组不存在，则打印警告并忽略此行
                print(f"⚠️  警告：跳过格式不正确的行: '{line}'. 错误: {e}")
                continue

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
