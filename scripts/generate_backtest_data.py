# 文件: scripts/generate_backtest_data.py (V6 - 历史顺序修复版)

import os
import sys
import json
from datetime import datetime

# --- 环境设置 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 核心组件导入 ---
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from src.model.lottery_models import LotteryHistory
from src.engine.algorithm_factory import create_algorithms_from_db
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.engine.recommendation_engine import RecommendationEngine
from src.llm.clients import get_llm_client
from src.prompt_templates import build_lotto_pro_prompt_v14_omega

# --- 配置 ---
BACKFILL_LLM_MODEL = "qwen3-max"


def run_full_historical_simulation():
    """
    执行一次完整的历史模拟，为所有缺失的期号生成包括LLM决策在内的完整推荐记录。
    """
    db_manager = DatabaseManager(**DB_CONFIG)
    if not db_manager.connect():
        print("❌ 数据库连接失败")
        return

    print("\n" + "#" * 70)
    print("###      🚀 开始执行全流程历史回测模拟      ###")
    print(f"###      (将使用模型: {BACKFILL_LLM_MODEL})      ###")
    print("#" * 70)

    try:
        # 1. 找出需要回填的“空档期”
        all_history_periods_raw = db_manager.execute_query(
            "SELECT period_number FROM lottery_history ORDER BY period_number ASC")
        processed_periods_raw = db_manager.execute_query(
            "SELECT DISTINCT period_number FROM algorithm_recommendation WHERE algorithm_version LIKE %s",
            (f"{BACKFILL_LLM_MODEL}%",)
        )
        all_history_periods = {p['period_number'] for p in all_history_periods_raw}
        processed_periods = {p['period_number'] for p in processed_periods_raw}
        periods_to_fill = sorted(list(all_history_periods - processed_periods))

        if not periods_to_fill:
            print("  - ✅ 恭喜！所有历史期号都已有模型的回测推荐记录，无需回填。")
            return

        print(f"  - 📊 发现 {len(periods_to_fill)} 个历史期号需要生成完整的模拟推荐。")

        # 2. 准备固定的组件
        base_algorithms = create_algorithms_from_db(db_manager)
        llm_client = get_llm_client(BACKFILL_LLM_MODEL)
        if not base_algorithms or not llm_client:
            print("  - ❌ 错误: 无法加载算法或LLM客户端，回填终止。")
            return

        # --- 核心修复：确保加载的数据是按期号升序排列 ---
        # 我们需要一个能返回 LotteryHistory 对象列表的方法
        # 假设 db_manager 内部的 get_lottery_history 是降序的，我们需要自己写SQL
        all_history_raw = db_manager.execute_query("SELECT * FROM lottery_history ORDER BY period_number ASC")
        if not all_history_raw:
            print("❌ 历史数据为空。")
            return

        # 手动将字典列表转换为对象列表，确保顺序正确
        all_history_data = [LotteryHistory.from_dict(d) for d in all_history_raw]
        # (注意: 您需要在 LotteryHistory 类中添加一个 from_dict 的类方法)

        # 3. 遍历所有“空档期”，执行完整的预测与存储流程
        for i, period in enumerate(periods_to_fill, 1):
            print(f"\n--- 正在模拟进度: {i}/{len(periods_to_fill)} (期号: {period}) ---")

            try:
                # a. 准备“当时”的训练数据
                current_index = next(idx for idx, draw in enumerate(all_history_data) if draw.period_number == period)
                training_data = all_history_data[:current_index]
                if len(training_data) < 30:
                    print(f"  - ⏸️  跳过: 历史数据不足30期。")
                    continue

                # ... (后续的 b, c, d, e 步骤完全保持不变) ...
                individual_predictions, algorithm_parameters = {}, {}
                for algo in base_algorithms:
                    algo.train(training_data)
                    prediction = algo.predict(training_data)
                    individual_predictions[algo.name] = prediction
                    algorithm_parameters[algo.name] = {'version': getattr(algo, 'version', '1.0')}

                optimizer = DynamicEnsembleOptimizer(base_algorithms)
                optimizer.train(training_data)
                engine = RecommendationEngine()
                engine.set_meta_algorithm(optimizer)
                final_report = engine.generate_final_recommendation(
                    history_data=training_data,
                    individual_predictions=individual_predictions
                )

                prompt_text, _ = build_lotto_pro_prompt_v14_omega(
                    recent_draws=training_data, model_outputs=final_report,
                    performance_log=optimizer.current_weights, next_issue_hint=period
                )
                print(f"  - 🧠 正在调用 {BACKFILL_LLM_MODEL} 为期号 {period} 进行决策...")
                response_str = llm_client.generate(system_prompt=prompt_text, user_prompt="Execute final analysis.")
                response_data = json.loads(response_str)

                final_summary = response_data.get('final_summary', {})
                recommendations_from_llm = response_data['cognitive_cycle_outputs']['phase4_portfolio_construction'][
                    'recommendations']

                root_id = db_manager.insert_algorithm_recommendation_root(
                    period_number=period,
                    algorithm_version=f"{BACKFILL_LLM_MODEL} (Backfill V1)",
                    algorithm_parameters=json.dumps(algorithm_parameters, ensure_ascii=False),
                    model_weights=json.dumps(optimizer.current_weights, ensure_ascii=False),
                    confidence_score=final_summary.get('confidence_level', 0.8),
                    risk_level=final_summary.get('risk_assessment', 'medium'),
                    analysis_basis=json.dumps(final_report, ensure_ascii=False),
                    llm_cognitive_details=json.dumps(response_data.get('cognitive_cycle_outputs', {}),
                                                     ensure_ascii=False),
                    key_patterns=json.dumps({}, ensure_ascii=False),
                    models=','.join([a.name for a in base_algorithms])
                )
                if not root_id: raise Exception("插入主记录失败")

                details_to_insert = [
                    {"recommend_type": rec.get('type', 'Unknown'), "strategy_logic": rec.get('role_in_portfolio', ''),
                     "front_numbers": ','.join(map(str, rec.get('front_numbers', []))),
                     "back_numbers": ','.join(map(str, rec.get('back_numbers', []))),
                     "win_probability": rec.get('confidence_score', 0.0)}
                    for rec in recommendations_from_llm
                ]
                db_manager.insert_recommendation_details_batch(root_id, details_to_insert)
                print(f"  - ✅ 成功存储期号 {period} 的完整模拟推荐 (ID: {root_id})。")

            except Exception as e:
                print(f"\n  - ❌ 处理期号 {period} 时发生错误: {e}")
                continue
    # ... (finally 块保持不变) ...
    finally:
        if db_manager and db_manager.is_connected():
            db_manager.disconnect()


if __name__ == "__main__":
    run_full_historical_simulation()