import os
import sys
import json
import argparse
from typing import List, Dict, Any

# --- 环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 核心组件导入 ---
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from src.model.lottery_models import LotteryHistory
from src.algorithms import AVAILABLE_ALGORITHMS
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.engine.recommendation_engine import RecommendationEngine
from src.engine.imperial_senate import ImperialSenate
from src.prompt_templates import build_final_mandate_prompt
from src.llm.clients import get_llm_client

# --- 配置 ---
# <<< 核心升级 1/3: 定义您的“模型武器库” >>>
# 在这里列出您想一次性全部回测的所有LLM模型
MODELS_TO_SIMULATE = [
    "deepseek-chat",
    # "qwen-max", # 如果您配置了qwen，可以取消注释
    # "gpt-4o",   # 如果您配置了OpenAI，可以取消注释
]

NUM_PERIODS_TO_SIMULATE = 9999


def run_full_historical_simulation(force_rerun: bool = False):
    """
    V2.0: 对“模型武器库”中的每一个LLM，都执行一次完整的历史决策模拟。
    """
    db = DatabaseManager(**DB_CONFIG)
    if not db.connect():
        print("❌ 数据库连接失败，模拟终止。")
        return

    print("\n" + "#" * 70)
    print("###      🚀 开始执行【多模型并行】历史决策模拟      ###")
    print(f"###      (将对以下模型进行全面回测: {MODELS_TO_SIMULATE})      ###")
    print("#" * 70)

    try:
        if force_rerun:
            print("\n⚠️  --force 模式已启用，正在清理所有历史模拟决策...")
            # 这个清理逻辑现在是安全的，因为它会为每个模型清理
            for model_name in MODELS_TO_SIMULATE:
                sim_version_like = f"%TheFinalMandate_{model_name}%_Simulated"
                subquery = "SELECT id FROM algorithm_recommendation WHERE algorithm_version LIKE %s"

                # 安全地获取需要删除的ID列表
                ids_to_delete_raw = db.execute_query(subquery, (sim_version_like,))
                if ids_to_delete_raw:
                    ids_to_delete = tuple(item['id'] for item in ids_to_delete_raw)
                    # 使用 IN 子句进行批量删除
                    db.execute_update(
                        f"DELETE FROM backtest_results WHERE prediction_output_id IN (SELECT id FROM prediction_outputs WHERE recommendation_id IN {ids_to_delete})")
                    db.execute_update(f"DELETE FROM prediction_outputs WHERE recommendation_id IN {ids_to_delete}")
                    db.execute_update(
                        f"DELETE FROM recommendation_details WHERE recommendation_metadata_id IN {ids_to_delete}")
                    db.execute_update(f"DELETE FROM algorithm_recommendation WHERE id IN {ids_to_delete}")
                    print(f"  - ✅ 已清理模型 '{model_name}' 的所有历史模拟数据。")
            print("  - ✅ 清理完毕。")

        # --- 核心升级 2/3: 外层增加一个循环，遍历所有要测试的模型 ---
        for llm_model_name in MODELS_TO_SIMULATE:
            print("\n" + "=" * 70)
            print(f"=== 开始对模型: [{llm_model_name}] 进行回测 ===")
            print("=" * 70)

            # 找出该模型需要模拟的期号
            query_processed = "SELECT MAX(period_number) as max_p FROM algorithm_recommendation WHERE algorithm_version LIKE %s"
            sim_version_like_search = f"%TheFinalMandate_{llm_model_name}%_Simulated"
            latest_processed_raw = db.fetch_one(query_processed, (sim_version_like_search,))
            start_from_period = latest_processed_raw.get('max_p') if latest_processed_raw and latest_processed_raw.get(
                'max_p') else '2007000'

            query_all_history = "SELECT * FROM lottery_history WHERE period_number > %s ORDER BY period_number ASC LIMIT %s"
            all_history_to_simulate_raw = db.execute_query(query_all_history,
                                                           (start_from_period, NUM_PERIODS_TO_SIMULATE))

            if not all_history_to_simulate_raw:
                print(f"  - ✅ 模型 [{llm_model_name}] 的所有历史期号均已模拟过，跳至下一个模型。")
                continue

            print(f"  - 📊 模型 [{llm_model_name}] 发现 {len(all_history_to_simulate_raw)} 个历史期号需要模拟。")

            all_history_in_mem_raw = db.execute_query("SELECT * FROM lottery_history ORDER BY period_number ASC")
            all_history_in_mem = db._convert_rows_to_history_list(all_history_in_mem_raw)

            # 对该模型的每一个需要模拟的期号进行操作
            for i, target_draw_raw in enumerate(all_history_to_simulate_raw, 1):
                target_period = target_draw_raw['period_number']
                print(
                    f"\n--- 正在为 [{llm_model_name}] 模拟进度: {i}/{len(all_history_to_simulate_raw)} (期号: {target_period}) ---")

                try:
                    # ... 内部的完整决策流程完全不变，只是使用的LLM是动态的 ...
                    current_index = next(
                        idx for idx, draw in enumerate(all_history_in_mem) if draw.period_number == target_period)
                    training_data = all_history_in_mem[:current_index]
                    if len(training_data) < 30:
                        print(f"  - ⏸️  跳过: 前置历史数据不足30期。")
                        continue

                    # (学习、预测、元老院... 逻辑完全复用)
                    weights = {"FrequencyAnalysisScorer": 0.15, "HotColdScorer": 0.25, "OmissionValueScorer": 0.20,
                               "BayesianNumberPredictor": 0.15, "MarkovTransitionModel": 0.10,
                               "NumberGraphAnalyzer": 0.15}
                    dynamic_weights = {k: v / sum(weights.values()) for k, v in weights.items()}

                    base_scorers = [AlgoClass() for name, AlgoClass in AVAILABLE_ALGORITHMS.items() if
                                    name != "DynamicEnsembleOptimizer"]
                    fusion_algorithm = DynamicEnsembleOptimizer(base_algorithms=base_scorers)
                    fusion_algorithm.current_weights = dynamic_weights
                    engine = RecommendationEngine(base_scorers=base_scorers, fusion_algorithm=fusion_algorithm)
                    model_outputs = {"DynamicEnsembleOptimizer": engine.generate_fused_recommendation(training_data)}

                    senate = ImperialSenate(db, {}, model_outputs)
                    last_report_mock = "上期ROI-2%"
                    edict, quant_prop, ml_brief = senate.generate_all_briefings(training_data, last_report_mock)

                    prompt_text, _ = build_final_mandate_prompt(
                        recent_draws=training_data, model_outputs=model_outputs, performance_log={},
                        next_issue_hint=target_period, last_performance_report=last_report_mock,
                        budget=100.0, risk_preference="中性",
                        senate_edict=edict, quant_proposal=quant_prop, ml_briefing=ml_brief
                    )

                    # <<< 核心升级 3/3: 使用循环中当前的 llm_model_name >>>
                    llm_client = get_llm_client(llm_model_name)
                    response_str = llm_client.generate(system_prompt=prompt_text,
                                                       user_prompt="Your Majesty, your final decree.", json_mode=True)
                    response_data = json.loads(response_str.strip().replace('```json', '').replace('```', ''))

                    # (存储逻辑完全复用，但 model_name 是动态的)
                    # ... (省略双轨制存储代码以保持简洁，请确保您使用的是V5.2版本)

                except Exception as e:
                    print(f"\n  - ❌ 处理期号 {target_period} 时发生严重错误: {e}")
                    continue

    finally:
        if db and db.is_connected():
            db.disconnect()
            print("\n数据库连接已关闭。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行多模型并行历史决策模拟器。")
    parser.add_argument('--force', action='store_true', help='强制重新运行所有模型的模拟。')
    args = parser.parse_args()
    run_full_historical_simulation(force_rerun=args.force)