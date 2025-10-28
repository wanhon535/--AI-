# main.py (Final Architecture V4.3 - With Chinese Logging)

import json
import os
import sys
import traceback
from datetime import datetime

# --- 1. 项目环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
print(f"项目根目录已添加到路径: {project_root}")

# --- 2. 导入所有需要的模块 ---
from src.database.database_manager import DatabaseManager
from src.prompt_templates import build_lotto_pro_prompt_v14_omega
from src.llm.clients import get_llm_client
from src.engine.recommendation_engine import RecommendationEngine
from src.engine.performance_logger import PerformanceLogger

# --- 导入所有算法 ---
from src.algorithms.statistical_algorithms import FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, \
    OmissionValueAlgorithm
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer


def main():

    """主函数，负责编排完整的“评估-学习-决策”闭环"""
    print("\n" + "=" * 60)
    print("🔥  启动 LOTTO-PRO 自学习预测管道 V4.3")
    print("=" * 60)


    db_manager = None  # 确保在finally块中可用
    try:
        # --- 初始化核心组件 ---
        db_manager = DatabaseManager(
            host='localhost', user='root', password='123456789',
            database='lottery_analysis_system', port=3309
        )
        if not db_manager.connect():
            raise ConnectionError("数据库连接失败。")

        performance_logger = PerformanceLogger(db_manager=db_manager, smoothing_alpha=0.6, hist_window=5)

        # ======================================================================
        # 阶段一：学习 (从历史表现中学习)
        # ======================================================================
        print("\n[管道步骤 1/4] 从历史表现中学习...")
        # (在真实场景中，此步骤会在开奖后独立运行以评估和更新权重)
        print("  - [开发模式] 本次运行跳过实时评估环节，将直接使用数据库中的历史平均分。")

        # ======================================================================
        # 阶段二：预测 (运行完整的算法矩阵)
        # ======================================================================
        print("\n[管道步骤 2/4] 为下一期生成预测...")

        # 1. 获取最新数据
        recent_draws = db_manager.get_latest_lottery_history(100)
        next_issue = db_manager.get_next_period_number()
        print(f"  - 数据获取成功。目标期号: {next_issue}")

        # 2. 从数据库动态加载学习到的最新权重 (闭环的关键！)
        latest_weights = performance_logger.dao.get_average_scores_last_n_issues(n_issues=5)
        if not latest_weights:
            print("  - ⚠️ 警告: 未找到历史表现数据。优化器将使用默认等权重。")
        else:
            print(f"  - ✅ 已从数据库加载自适应权重: {json.dumps(latest_weights, indent=2)}")

        # 3. 组建基础算法团队
        base_algorithms = [
            FrequencyAnalysisAlgorithm(), HotColdNumberAlgorithm(), OmissionValueAlgorithm(),
            BayesianNumberPredictor(), MarkovTransitionModel(), NumberGraphAnalyzer(),
        ]

        # 4. 任命“首席策略官”(DynamicEnsembleOptimizer)，并注入最新的动态权重！
        chief_strategy_officer = DynamicEnsembleOptimizer(base_algorithms)
        if latest_weights:
            chief_strategy_officer.current_weights = latest_weights
            print("  - 已将学习到的权重注入优化器。")

        # 5. 启动专业引擎，执行最高决策
        engine = RecommendationEngine()
        engine.set_meta_algorithm(chief_strategy_officer)
        final_report = engine.generate_final_recommendation(recent_draws)

        # ======================================================================
        # 阶段三：LLM最终裁决 (FINAL JUDGEMENT)
        # ======================================================================
        print("\n[管道步骤 3/4] 提交综合报告给大语言模型进行最终裁决...")

        # 1. 构建Prompt
        prompt_text, _ = build_lotto_pro_prompt_v14_omega(
            recent_draws=recent_draws,
            model_outputs=final_report,
            performance_log=chief_strategy_officer.current_weights,
            last_performance_report="[系统日志] 权重已根据数据库中最近的表现分数自动调整。",
            next_issue_hint=next_issue,
        )
        print("  - Prompt 构建成功，准备提交给 CEO (LLM)。")

        # 2. 调用LLM
        MODEL_TO_USE = "qwen3-max"
        llm_client = get_llm_client(MODEL_TO_USE)
        response_str = llm_client.generate(
            system_prompt=prompt_text,
            user_prompt="请根据这份高度整合的战略建议书，进行最终的投资组合构建，并返回完整的JSON对象。"
        )
        print(f"  - ✅ 已收到来自 {MODEL_TO_USE} 的决策。")

        # ======================================================================
        # 阶段四：执行 (解析并存储到数据库)
        # ======================================================================
        print("\n[PIPELINE] STEP 4/4: Parsing and saving results to database...")
        try:
            response_data = json.loads(response_str)
            recommendations_from_llm = response_data['cognitive_cycle_outputs']['phase4_portfolio_construction'][
                'recommendations']
            print(f"  - ✅ Decision parsed successfully. Found {len(recommendations_from_llm)} portfolio items.")

            # --- vvvvvvvvvvv  恢复并强化的数据库写入逻辑 vvvvvvvvvvv ---

            # 1. 插入推荐主记录 (algorithm_recommendation)
            final_summary = response_data.get('final_summary', {})
            root_id = db_manager.insert_algorithm_recommendation_root(
                period_number=next_issue,
                model_name=f"{MODEL_TO_USE} ({response_data.get('request_meta', {}).get('engine_version', 'Prometheus')})",
                confidence_score=final_summary.get('confidence_level', 0.8),
                risk_level=final_summary.get('risk_assessment', 'medium')
            )

            if not root_id:
                print("  - ❌ CRITICAL: Failed to insert recommendation root record. Aborting save.")
                return

            print(f"  - ✅ Recommendation root record inserted. ID: {root_id}")

            # 2. 准备推荐详情数据
            details_to_insert = []
            for rec in recommendations_from_llm:
                front_str = ','.join(map(str, rec.get('front_numbers', [])))
                back_str = ','.join(map(str, rec.get('back_numbers', [])))

                details_to_insert.append({
                    "recommend_type": rec.get('type', 'Unknown'),
                    "strategy_logic": rec.get('role_in_portfolio', ''),
                    "front_numbers": front_str,
                    "back_numbers": back_str,
                    "win_probability": rec.get('confidence_score', 0.0)
                })

            # 3. 批量插入推荐详情 (recommendation_details)
            success = db_manager.insert_recommendation_details_batch(
                recommendation_id=root_id,
                details=details_to_insert
            )

            if success:
                print("  - ✅ All recommendation details have been successfully saved to the database.")
            else:
                print("  - ❌ FAILED: Could not insert recommendation details into the database.")

            # --- ^^^^^^^^^^^ 数据库写入逻辑结束 ^^^^^^^^^^^ ---

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  - ❌ CRITICAL: Failed to parse or save LLM's decision. Error: {e}")
            with open("error_response.log", "w", encoding="utf-8") as f:
                f.write(response_str)
            print("  - Raw response saved to error_response.log for debugging.")

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