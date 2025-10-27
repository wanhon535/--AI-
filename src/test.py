# test.py (位于项目根目录)

import json
import random
from typing import List, Dict, Any

# --------------------------------------------------------------------------
# 1. 导入您需要测试的函数和它依赖的类
#    我们使用相对导入，因为 test.py 在根目录，可以访问 src 包
# --------------------------------------------------------------------------
from src.prompt_templates import build_lotto_pro_prompt_v14_omega
from src.model.lottery_models import LotteryHistory


# --------------------------------------------------------------------------
# 2. 创建一个辅助函数来生成逼真的模拟数据
#    这是测试中最关键的部分，确保输入数据的格式和类型正确
# --------------------------------------------------------------------------
def generate_mock_data() -> Dict[str, Any]:
    """生成一组用于测试 V14.5 Prompt 的完整模拟数据。"""

    print(" MOCK: Generating mock data for the test...")

    # a. 模拟最近的开奖历史 (List[LotteryHistory])
    recent_draws = [
        LotteryHistory(
            period_number='2025121',
            front_area=[2, 8, 15, 22, 31],
            back_area=[3, 10]
        ),
        LotteryHistory(
            period_number='2025120',
            front_area=[5, 11, 19, 21, 34],
            back_area=[6, 7]
        ),
        LotteryHistory(
            period_number='2025119',
            front_area=[1, 9, 10, 25, 33],
            back_area=[1, 11]
        )
    ]

    # b. 模拟各个算法模型的输出 (Dict[str, Any])
    #    注意：这里的内部结构可以简化，因为Prompt本身不解析深层内容，只关心键的存在。
    model_outputs = {
        'bayesian': {'top_picks': [2, 11, 22, 31], 'confidence': 0.7},
        'markov': {'transitions': {'5': 19, '11': 2}, 'confidence': 0.6},
        'graph': {'communities': [[1, 9, 10], [25, 33]], 'confidence': 0.65},
        'neural': {'heatmap': {'8': 0.08, '23': 0.07}, 'confidence': 0.8},
        'hit_optimizer': {'optimized_set': [8, 15, 21, 23, 34], 'expected_hits': 1.2},
        'ensemble': {'final_recommendation': [2, 8, 21, 22, 33], 'confidence': 0.85},
        'backtest': {'avg_hits': 1.1, 'win_rate': 0.2}
    }

    # c. 模拟算法的历史表现日志 (Dict[str, float])
    #    这些值将用于计算动态权重
    performance_log = {
        'bayesian': 0.78,
        'markov': 0.45,
        'graph': 0.65,
        'neural': 0.85,
        'hit_optimizer': 0.72,
        'ensemble': 0.91
    }

    # d. 模拟用户的约束条件 (Dict[str, Any])
    user_constraints = {
        'max_bets': 4,
        'budget': 200.0,
        'risk_level': '激进'  # 这个字段在V14.5中被 risk_preference 参数替代
    }

    # e. 模拟上一期的复盘报告 (str)
    last_performance_report = """
    报告期号: 2025121
    策略: "核心热号追击策略"
    表现: 命中 前区1+后区1。
    结论: 策略过于集中于追逐热号（22, 31），但当期冷号（2, 8, 15）反弹，导致命中率不佳。
    经验教训: 单一策略风险敞口过大，需要引入对冲机制来平衡冷热号分布。
    """

    print(" MOCK: Mock data generation complete.\n")

    return {
        "recent_draws": recent_draws,
        "model_outputs": model_outputs,
        "performance_log": performance_log,
        "user_constraints": user_constraints,
        "last_performance_report": last_performance_report,
        "next_issue_hint": "2025122",
        "budget": 200.0,
        "risk_preference": "激进"
    }


# --------------------------------------------------------------------------
# 3. 主执行逻辑
#    在这里，我们调用函数并打印结果
# --------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("🚀  STARTING TEST FOR: build_lotto_pro_prompt_v14_omega")
    print("=" * 50)

    # 获取模拟数据
    mock_data = generate_mock_data()

    # 调用你的 V14.5 Prompt 生成函数
    # 使用 **mock_data 将字典中的所有键值对作为参数传递给函数
    print("📞  Calling the prompt generation function...")
    generated_prompt, next_issue = build_lotto_pro_prompt_v14_omega(**mock_data)
    print("✅  Prompt function executed successfully!\n")

    # 打印结果以进行验证
    print("-" * 50)
    print("🔍  VERIFICATION OF OUTPUTS")
    print("-" * 50)

    print(f"\n[ NEXT ISSUE IDENTIFIED ]\n{next_issue}\n")

    print("\n[ GENERATED PROMETHEUS-Ω PROMPT ]")
    print("--- START OF PROMPT ---")
    print(generated_prompt)
    print("--- END OF PROMPT ---\n")

    # 作为一个额外的健全性检查，我们可以尝试解析Prompt中包含的JSON模板
    # 这有助于确保模板本身是有效的
    try:
        # 从Prompt末尾提取JSON模板字符串
        json_template_str = generated_prompt.split("```json").split("```")[0].strip()
        json.loads(json_template_str)
        print("✅  Sanity Check: The JSON template within the prompt is valid.")
    except Exception as e:
        print(f"❌  Sanity Check FAILED: The JSON template within the prompt is invalid. Error: {e}")

    print("\n=" * 50)
    print("🏁  TEST COMPLETE")
    print("=" * 50)