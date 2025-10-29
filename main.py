# main.py (V5.0 - Final Integrated Self-Learning System)

import json
import os
import sys
import traceback

# --- 1. Project Environment Setup ---
# This ensures that Python can find all your modules in the 'src' directory
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"项目根目录已添加到路径: {project_root}")

# --- 2. Import All System Components ---
from src.database.database_manager import DatabaseManager
from src.engine.performance_logger import PerformanceLogger
from src.engine.recommendation_engine import RecommendationEngine
from src.llm.clients import get_llm_client
from src.prompt_templates import build_lotto_pro_prompt_v14_omega

# --- Import all algorithms ---
# a) Meta-Algorithm (The "Chief Strategy Officer")
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
# b) Base Algorithms (The "Department Managers")
from src.algorithms.statistical_algorithms import (
    FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, OmissionValueAlgorithm
)
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer


def main():
    """
    Main function to orchestrate the entire 'Learn -> Predict -> Decide -> Store' pipeline.
    """
    print("\n" + "=" * 60)
    print("🔥  启动 LOTTO-PRO 自学习预测管道 V5.0")
    print("=" * 60)

    db_manager = None
    try:
        # --- [PIPELINE STEP 1/5: INITIALIZATION & DATA FETCHING] ---
        print("\n[PIPELINE STEP 1/5] 初始化组件并获取数据...")

        # Initialize and connect to the database
        db_manager = DatabaseManager(
            host='localhost', user='root', password='123456789',
            database='lottery_analysis_system', port=3309
        )
        if not db_manager.connect():
            raise ConnectionError("数据库连接失败。")

        # Initialize the learning component, injecting the database manager
        performance_logger = PerformanceLogger(db_manager=db_manager, hist_window=5)

        # Fetch primary data for the prediction
        recent_draws = db_manager.get_latest_lottery_history(100)
        if recent_draws:
            print("----------- 诊断信息：第一条历史数据的结构 -----------")
            print(recent_draws[0])
            print("----------------------------------------------------")

        next_issue = db_manager.get_next_period_number()
        print(f"✅ 组件初始化成功。目标期号: {next_issue}")

        # --- [PIPELINE STEP 2/5: ADAPTIVE WEIGHT LEARNING] ---
        print("\n[PIPELINE STEP 2/5] 从历史表现中学习动态权重...")

        # Fetch the latest learned weights from the database
        latest_weights = performance_logger.dao.get_average_scores_last_n_issues(n_issues=5)

        if not latest_weights:
            print("  - ⚠️ 警告: 未找到历史表现数据。优化器将使用默认等权重。")
        else:
            print(f"  - ✅ 已从数据库加载自适应权重: {json.dumps(latest_weights, indent=2)}")

        # --- [PIPELINE STEP 3/5: ALGORITHM ENGINE EXECUTION] ---
        print("\n[PIPELINE STEP 3/5] 运行元算法引擎...")

        # 1. Assemble the team of base algorithms
        base_algorithms = [
            FrequencyAnalysisAlgorithm(), HotColdNumberAlgorithm(), OmissionValueAlgorithm(),
            BayesianNumberPredictor(), MarkovTransitionModel(), NumberGraphAnalyzer(),
        ]

        # 2. Appoint the "Chief Strategy Officer" and inject the learned weights
        chief_strategy_officer = DynamicEnsembleOptimizer(base_algorithms)
        if latest_weights:
            chief_strategy_officer.current_weights = latest_weights
            print("  - 已将学习到的权重注入优化器。")

        # 3. Initialize the main engine and set the meta-algorithm
        engine = RecommendationEngine()
        engine.set_meta_algorithm(chief_strategy_officer)

        # 4. Run the entire stack to get the final, optimized report
        final_report = engine.generate_final_recommendation(recent_draws)

        # --- [PIPELINE STEP 4/5: LLM FINAL JUDGEMENT] ---
        print("\n[PIPELINE STEP 4/5] 提交综合报告给大语言模型进行最终裁决...")

        prompt_text, _ = build_lotto_pro_prompt_v14_omega(
            recent_draws=recent_draws,
            model_outputs=final_report,
            performance_log=chief_strategy_officer.current_weights,
            last_performance_report="[System Log] Weights are auto-adjusted based on the average score from the last 5 evaluated periods.",
            next_issue_hint=next_issue,
        )
        print("  - Prompt 构建成功。")

        MODEL_TO_USE = "qwen3-max"
        llm_client = get_llm_client(MODEL_TO_USE)
        response_str = llm_client.generate(
            system_prompt=prompt_text,
            user_prompt="Based on the integrated strategy report, execute your final analysis and generate the complete JSON investment portfolio."
        )
        print("  - ✅ LLM 最终决策已接收。")

        # --- [PIPELINE STEP 5/5: PARSING & STORING RESULTS] ---
        print("\n[PIPELINE STEP 5/5] 解析决策并保存至数据库...")
        try:
            response_data = json.loads(response_str)
            print("----------- LLM 原始响应 (格式化后) -----------")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            print("-------------------------------------------------")
            recommendations_from_llm = response_data['cognitive_cycle_outputs']['phase4_portfolio_construction'][
                'recommendations']

            # 1. Insert recommendation root record
            final_summary = response_data.get('final_summary', {})
            root_id = db_manager.insert_algorithm_recommendation_root(
                period_number=next_issue,
                model_name=f"{MODEL_TO_USE} ({response_data.get('request_meta', {}).get('engine_version', 'Prometheus')})",
                confidence_score=final_summary.get('confidence_level', 0.8),
                risk_level=final_summary.get('risk_assessment', 'medium')
            )

            if not root_id:
                raise Exception("插入推荐主记录失败，未返回ID。")

            print(f"  - ✅ 推荐主记录已保存，ID: {root_id}")

            # 2. Prepare and insert recommendation details
            details_to_insert = []
            for rec in recommendations_from_llm:
                details_to_insert.append({
                    "recommend_type": rec.get('type', 'Unknown'),
                    "strategy_logic": rec.get('role_in_portfolio', ''),
                    "front_numbers": ','.join(map(str, rec.get('front_numbers', []))),
                    "back_numbers": ','.join(map(str, rec.get('back_numbers', []))),
                    "win_probability": rec.get('confidence_score', 0.0)
                })

            success = db_manager.insert_recommendation_details_batch(
                recommendation_id=root_id,
                details=details_to_insert
            )

            if success:
                print(f"  - ✅ {len(details_to_insert)} 条推荐详情已成功保存。")
            else:
                raise Exception("批量插入推荐详情失败。")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  - ❌ 严重错误: 解析或保存LLM决策时失败。错误: {e}")
            with open("error_response.log", "w", encoding="utf-8") as f:
                f.write(response_str)
            print("  - 原始响应已保存至 error_response.log。")

    except Exception as e:
        print(f"\n❌ 管道执行期间发生意外错误: {e}")
        traceback.print_exc()
    finally:
        if db_manager and db_manager._connected:
            db_manager.disconnect()
            print("\n数据库连接已关闭。")

        print("\n" + "=" * 60)
        print("🏁  管道执行完毕。")
        print("=" * 60)


if __name__ == "__main__":
    main()