# main.py (V7.0 - 全自动智能管家)

import json
import os
import sys
import traceback

# --- 1. 项目环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 2. 导入所有核心组件 ---
from src.database.database_manager import DatabaseManager
from src.engine.performance_logger import PerformanceLogger
from src.engine.recommendation_engine import RecommendationEngine
from src.llm.clients import get_llm_client
from src.prompt_templates import build_lotto_pro_prompt_v14_omega
from src.engine.system_orchestrator import SystemOrchestrator
# <<< 关键集成：直接导入回测运行器 >>>
from run_backtest_simulation import BacktestRunner

# --- 3. 算法导入 ---
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.algorithms.statistical_algorithms import (
    FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, OmissionValueAlgorithm
)
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer

# --- 4. 全局配置 ---
DB_CONFIG = dict(
    host='localhost', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)


def run_prediction_pipeline(db_manager: DatabaseManager):
    """
    执行单次预测的管道。这是您原有的核心预测逻辑。
    """
    print("\n" + "=" * 60)
    print("🚀  步骤4: 启动 [预测] 管道...")
    print("=" * 60)

    try:
        # 1. 数据获取
        performance_logger = PerformanceLogger(db_manager=db_manager)
        recent_draws = db_manager.get_latest_lottery_history(100)
        next_issue = db_manager.get_next_period_number()
        print(f"  - 目标期号: {next_issue}")

        # 2. 学习最新权重
        latest_weights = performance_logger.dao.get_average_scores_last_n_issues(n_issues=5)
        if not latest_weights:
            print("  - ⚠️ 警告: 尚未学习到任何权重，使用默认值。")
        else:
            print(f"  - ✅ 已加载学习到的动态权重。")

        # 3. 算法引擎执行
        base_algorithms = [
            FrequencyAnalysisAlgorithm(), HotColdNumberAlgorithm(), OmissionValueAlgorithm(),
            BayesianNumberPredictor(), MarkovTransitionModel(), NumberGraphAnalyzer(),
        ]
        chief_strategy_officer = DynamicEnsembleOptimizer(base_algorithms)
        if latest_weights:
            chief_strategy_officer.current_weights = latest_weights
        engine = RecommendationEngine()
        engine.set_meta_algorithm(chief_strategy_officer)
        final_report = engine.generate_final_recommendation(recent_draws)

        # 4. LLM最终裁决
        prompt_text, _ = build_lotto_pro_prompt_v14_omega(
            recent_draws=recent_draws,
            model_outputs=final_report,
            performance_log=chief_strategy_officer.current_weights,
            next_issue_hint=next_issue,
            last_performance_report="Weights auto-learned from history."
        )
        llm_client = get_llm_client("qwen3-max")
        response_str = llm_client.generate(
            system_prompt=prompt_text,
            user_prompt="Execute your final analysis and generate the complete JSON investment portfolio."
        )

        # 5. 存储结果
        response_data = json.loads(response_str)
        final_summary = response_data.get('final_summary', {})
        recommendations_from_llm = response_data['cognitive_cycle_outputs']['phase4_portfolio_construction'][
            'recommendations']

        root_id = db_manager.insert_algorithm_recommendation_root(
            period_number=next_issue,
            algorithm_version=f"qwen3-max (V14.5-Pr)",
            confidence_score=final_summary.get('confidence_level', 0.8),
            risk_level=final_summary.get('risk_assessment', 'medium'),
            analysis_basis=json.dumps(final_report, ensure_ascii=False)
        )
        if not root_id:
            raise Exception("插入推荐主记录失败。")

        print(f"  - ✅ 成功为期号 {next_issue} 存储了预测主记录 (ID: {root_id})。")

        # 插入详情
        details_to_insert = []
        for rec in recommendations_from_llm:
            details_to_insert.append({
                "recommend_type": rec.get('type', 'Unknown'),
                "strategy_logic": rec.get('role_in_portfolio', ''),
                "front_numbers": ','.join(map(str, rec.get('front_numbers', []))),
                "back_numbers": ','.join(map(str, rec.get('back_numbers', []))),
                "win_probability": rec.get('confidence_score', 0.0)
            })
        db_manager.insert_recommendation_details_batch(root_id, details_to_insert)
        print(f"  - ✅ 成功存储了 {len(details_to_insert)} 条推荐详情。")

    except Exception as e:
        print(f"\n❌ 预测管道执行期间发生意外错误: {e}")
        traceback.print_exc()


def main():
    """
    全自动智能管家主程序。
    """
    print("\n" + "#" * 70)
    print("###       欢迎使用 Lotto-Pro 全自动智能管家 V7.0       ###")
    print("#" * 70)

    db_manager = DatabaseManager(**DB_CONFIG)
    try:
        if not db_manager.connect():
            raise ConnectionError("数据库连接失败，程序终止。")

        orchestrator = SystemOrchestrator(db_manager)

        # --- 步骤1: 检查系统是否需要“冷启动” ---
        print("\n" + "=" * 60)
        print("🔍 步骤1: 检查系统是否需要初始化...")
        stats_count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM number_statistics")
        stats_count = stats_count_result[0]['count'] if stats_count_result else 0
        if stats_count == 0:
            print("  - 检测到系统首次运行，将执行初始化...")
            orchestrator.check_and_initialize_data()
        else:
            print("  - ✅ 系统已初始化，跳过。")

        # --- 步骤2: 检查并回填缺失的历史分析数据 ---
        print("\n" + "=" * 60)
        print("🔍 步骤2: 检查是否有需要回填的历史分析...")
        missing_basis_result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM algorithm_recommendation WHERE analysis_basis IS NULL OR analysis_basis = ''")
        missing_basis_count = missing_basis_result[0]['count'] if missing_basis_result else 0
        if missing_basis_count > 0:
            print(f"  - 检测到 {missing_basis_count} 条记录缺少分析数据，开始回填...")
            orchestrator.backfill_analysis_basis()
        else:
            print("  - ✅ 所有历史记录的分析数据完整，跳过。")

        # --- 步骤3: 检查并运行历史学习流程 ---
        print("\n" + "=" * 60)
        print("🔍 步骤3: 检查是否有需要学习的新历史...")
        unlearned_query = """
                    SELECT COUNT(DISTINCT period_number) as count
                    FROM algorithm_recommendation
                    WHERE (analysis_basis IS NOT NULL AND analysis_basis != '')
                    AND period_number NOT IN (SELECT DISTINCT period_number FROM algorithm_performance)
                """
        unlearned_result = db_manager.execute_query(unlearned_query)
        unlearned_count = unlearned_result[0]['count'] if unlearned_result else 0
        if unlearned_count > 0:
            print(f"  - 检测到 {unlearned_count} 期已分析但未学习的历史，开始学习...")
            backtest_runner = BacktestRunner(DB_CONFIG)
            try:
                backtest_runner.connect()
                start, end = backtest_runner._get_issue_range_from_db()
                if start and end:
                    backtest_runner.run(start, end)
            finally:
                backtest_runner.disconnect()
        else:
            print("  - ✅ 所有历史均已学习，跳过。")

        # --- 步骤4: 执行今天的预测任务 ---
        run_prediction_pipeline(db_manager)

    except Exception as e:
        print(f"\n❌ 系统主流程发生严重错误: {e}")
        traceback.print_exc()
    finally:
        if db_manager and getattr(db_manager, "_connected", False):
            db_manager.disconnect()
            print("\n" + "#" * 70)
            print("###                  系统所有任务执行完毕                  ###")
            print("#" * 70)


if __name__ == "__main__":
    main()