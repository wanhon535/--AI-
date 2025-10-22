# file: src/ai_caller.py
# 优化版本
import re
import json
from typing import List, Dict
from openai import OpenAI

# 1. 导入新的 V9 Prompt 构建函数
from src.prompt_templates import build_lotto_pro_prompt_v9
# 2. 导入您的数据库管理器
from src.database.database_manager import DatabaseManager
# 3. 导入分析模块的函数
from src.analysis.performance_analyzer import analyze_recommendation_performance, generate_performance_summary


def parse_ai_recommendations(content: str) -> List[Dict]:
    """
    解析AI返回的推荐内容（支持Markdown表格和加粗格式）。
    这是一个独立的工具函数，放在顶层方便调用。
    """
    recommendations = []
    if not content:
        return recommendations

    lines = content.strip().split('\n')
    header_index = -1
    for i, line in enumerate(lines):
        if "推荐类型" in line and "策略逻辑" in line and line.strip().startswith('|'):
            header_index = i
            break

    if header_index == -1:
        print("⚠️  警告：未在AI响应中找到标准的推荐表格，将使用备用数据。")
        return []

    data_start_index = header_index + 1
    if data_start_index < len(lines) and '---' in lines[data_start_index]:
        data_start_index += 1

    pattern = re.compile(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')

    for i in range(data_start_index, len(lines)):
        line = lines[i].strip()
        if not line.startswith('|') or not line.endswith('|'):
            break

        match = pattern.match(line)
        if not match:
            continue

        try:
            # 提取并清理数据
            recommend_type = re.sub(r'\*\*', '', match.group(1)).strip()
            strategy_logic = re.sub(r'\*\*', '', match.group(2)).strip()
            front_numbers = re.sub(r'\*\*', '', match.group(3)).strip()
            back_numbers = re.sub(r'\*\*', '', match.group(4)).strip()
            win_prob_str = re.sub(r'[\*\s%]|\[理论EV\]', '', match.group(5)).strip()
            win_probability = float(win_prob_str) if win_prob_str else 0.0

            recommendations.append({
                "recommend_type": recommend_type,
                "strategy_logic": strategy_logic,
                "front_numbers": front_numbers,
                "back_numbers": back_numbers,
                "win_probability": win_probability
            })
        except (ValueError, IndexError) as e:
            print(f"⚠️  警告：跳过格式不正确的行: '{line}'. 错误: {e}")
            continue

    return recommendations


def main():
    """
    主执行函数，串联“分析-反馈-预测-存储”的完整AI工作流。
    """
    db_manager = None
    try:
        # --- 步骤 1: 初始化数据库 ---
        db_manager = DatabaseManager(
            host='localhost', user='root', password='root',
            database='lottery_analysis_system', port=3307
        )
        if not db_manager.connect():
            raise ConnectionError("数据库连接失败")
        print("✅ 数据库连接成功。")

        # --- 步骤 2: 确定期号并生成反馈报告 ---
        latest_draw = db_manager.get_latest_lottery_history(1)
        if not latest_draw:
            raise ValueError("数据库中没有历史开奖数据，无法启动流程。")

        last_period_to_analyze = latest_draw[0].period_number
        next_period_to_predict = str(int(last_period_to_analyze) + 1)
        print(f"🔄 最新开奖期为 {last_period_to_analyze}，即将预测第 {next_period_to_predict} 期。")

        print(f"\n--- 正在分析第 {last_period_to_analyze} 期表现以生成反馈报告 ---")
        analysis_data = analyze_recommendation_performance(last_period_to_analyze)
        performance_feedback_report = generate_performance_summary(analysis_data)
        print("✅ 反馈报告已生成。")

        # --- 步骤 3: 获取构建Prompt所需的数据 ---
        recent_draws = db_manager.get_latest_lottery_history(50)
        user_bets = db_manager.get_user_bets('default', 20)
        print(f"📊 已获取最近 {len(recent_draws)} 期数据和 {len(user_bets)} 条用户投注记录。")

        # --- 步骤 4: 构建 V9 版本的智能Prompt ---
        final_prompt, _ = build_lotto_pro_prompt_v9(
            recent_draws=recent_draws,
            user_bets=user_bets,
            next_issue_hint=next_period_to_predict,
            last_performance_report=performance_feedback_report  # 关键：传入反馈报告
        )
        print("\n--- 正在调用AI模型，请稍候... ---")

        # --- 步骤 5: 调用 AI 模型 ---
        client = OpenAI(
            api_key="sk-...",  # 请替换为您的真实API Key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-max",  # 确保模型名称正确
            messages=[{"role": "user", "content": final_prompt}],
            temperature=0.7  # 增加一点创造性
        )
        response_content = completion.choices[0].message.content
        print("✅ AI模型响应成功！\n" + response_content)

        # --- 步骤 6: 解析并存储结果 ---
        recommendations_data = parse_ai_recommendations(response_content)
        if not recommendations_data:  # 如果解析失败或为空
            print("❌ 解析AI推荐失败或无数据，流程终止。")
            return

        print(f"\n✅ 成功解析 {len(recommendations_data)} 条推荐，正在存入数据库...")

        root_success = db_manager.insert_algorithm_recommendation_root(
            period_number=next_period_to_predict, model_name="qwen-max-v9",
            confidence_score=0.9, risk_level="medium"
        )
        if not root_success:
            raise RuntimeError("❌ 算法推荐根记录插入失败")

        last_insert_id = db_manager.execute_query("SELECT LAST_INSERT_ID();")[0]['LAST_INSERT_ID()']
        details_success = db_manager.insert_recommendation_details_batch(
            recommendation_id=last_insert_id, details=recommendations_data
        )
        if details_success:
            print("✅ 推荐详情已成功插入数据库！")
        else:
            raise RuntimeError("❌ 推荐详情插入失败")

    except Exception as e:
        print(f"\n❌ 程序执行过程中发生严重错误: {e}")
    finally:
        if db_manager and db_manager.is_connected():
            db_manager.disconnect()
            print("\n⏹️ 数据库连接已关闭，流程结束。")


if __name__ == "__main__":
    main()