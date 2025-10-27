# main.py
from src.config.database_config import DatabaseConfig

from src.config.system_config import SystemConfig
from src.database.database_manager import DatabaseManager
from src.engine.recommendation_engine import RecommendationEngine
from src.engine.evaluation_system import EvaluationSystem
from src.algorithms.statistical_algorithms import (
    FrequencyAnalysisAlgorithm,
    HotColdNumberAlgorithm,
    OmissionValueAlgorithm
)
import logging

def main():
    """主函数"""
    # 初始化日志
    # main.py (位于项目根目录)

    import json
    import os
    import sys

    # --- 1. 项目环境设置 (Setup Project Environment) ---
    # 将项目根目录添加到Python的模块搜索路径，确保可以正确导入src下的所有模块
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, project_root)
    print(f"Project root added to path: {project_root}")

    # --- 2. 导入项目核心模块 (Import Core Modules) ---
    from src.database.database_manager import DatabaseManager
    from src.prompt_templates import build_lotto_pro_prompt_v14_omega
    from src.llm.clients import get_llm_client

    # --- 3. 主执行函数 (Main Execution Function) ---
    def run_prediction_pipeline():
        """
        执行一次完整的端到端预测流程：
        连接数据库 -> 获取数据 -> 构建Prompt -> 调用AI -> 解析结果 -> 存入数据库
        """
        print("\n" + "=" * 60)
        print("🔥  STARTING LOTTO-PRO PREDICTION PIPELINE (Prometheus-Ω Engine)")
        print("=" * 60)

        # --- 初始化并连接数据库 ---
        db_manager = DatabaseManager(
            host='localhost', user='root', password='123456789',
            database='lottery_analysis_system', port=3309
        )
        if not db_manager.connect():
            print("❌ CRITICAL: Database connection failed. Aborting pipeline.")
            return

        try:
            # --- 步骤一：从数据库获取实时数据 ---
            print("\n[PHASE 1/5] Fetching data from database...")

            # !! 注意：以下是我根据您的项目结构推断的方法名 !!
            # !! 如果您的 DatabaseManager 中方法名不同，请在此处修改 !!
            recent_draws = db_manager.get_latest_lottery_history(50)
            # 假设您有方法获取算法的历史表现和上一期复盘报告
            # 如果没有，我们将使用None或空字典作为占位符
            performance_log = db_manager.get_performance_log() if hasattr(db_manager, 'get_performance_log') else {}
            last_performance_report = db_manager.get_last_performance_report() if hasattr(db_manager,
                                                                                          'get_last_performance_report') else None
            next_issue = db_manager.get_next_period_number()

            print(f"✅ Data fetched successfully for next issue: {next_issue}")
            print(f"  - Loaded {len(recent_draws)} recent draws.")
            print(f"  - Loaded {len(performance_log)} performance records.")

            # --- 步骤二：构建 Prometheus-Ω Prompt ---
            print("\n[PHASE 2/5] Building Prometheus-Ω prompt...")

            # 假设您的 model_outputs 来自于一个算法引擎
            # 在本次测试中，我们先用一个模拟的 placeholder
            mock_model_outputs = {
                'bayesian': {'status': 'ok'}, 'markov': {'status': 'ok'}, 'graph': {'status': 'ok'},
                'neural': {'status': 'ok'}, 'hit_optimizer': {'status': 'ok'}, 'ensemble': {'status': 'ok'}
            }

            prompt_text, _ = build_lotto_pro_prompt_v14_omega(
                recent_draws=recent_draws,
                model_outputs=mock_model_outputs,
                performance_log=performance_log,
                last_performance_report=last_performance_report,
                next_issue_hint=next_issue,
                risk_preference="平衡"  # 可根据需要调整
            )
            print("✅ Prompt built successfully.")

            # --- 步骤三：调用通义千问模型 ---
            print("\n[PHASE 3/5] Calling Tongyi LLM (qwen3-max)...")

            # 这是您可以轻松切换模型的地方
            MODEL_TO_USE = "qwen3-max"

            llm_client = get_llm_client(MODEL_TO_USE)
            response_str = llm_client.generate(
                system_prompt=prompt_text,
                user_prompt="请根据以上指令，执行你的分析并返回完整的JSON对象。"
            )
            print("✅ LLM response received.")

            # --- 步骤四：解析AI返回的JSON结果 ---
            print("\n[PHASE 4/5] Parsing AI response...")
            try:
                response_data = json.loads(response_str)
                # 提取核心的推荐列表
                recommendations = response_data['cognitive_cycle_outputs']['phase4_portfolio_construction'][
                    'recommendations']
                print(f"✅ AI response parsed successfully. Found {len(recommendations)} recommendations.")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ CRITICAL: Failed to parse AI response. Error: {e}")
                print("--- RAW AI RESPONSE ---")
                print(response_str)
                print("-----------------------")
                # 写入错误日志文件以便分析
                with open("error_response.log", "w", encoding="utf-8") as f:
                    f.write(response_str)
                print("Raw response saved to error_response.log. Aborting pipeline.")
                return

            # --- 步骤五：将结果存入数据库 ---
            print("\n[PHASE 5/5] Saving recommendations to database...")

            # 1. 插入推荐主记录
            root_id = db_manager.insert_algorithm_recommendation_root(
                period_number=next_issue,
                model_name=MODEL_TO_USE,
                confidence_score=response_data.get('final_summary', {}).get('confidence_level', 0.85),
                risk_level=response_data.get('final_summary', {}).get('risk_assessment', 'medium')
            )

            if not root_id:
                print("❌ CRITICAL: Failed to insert recommendation root record. Aborting save.")
                return

            print(f"✅ Recommendation root record inserted. ID: {root_id}")

            # 2. 转换数据格式以匹配DAO的批量插入方法
            details_to_insert = []
            for rec in recommendations:
                # 将列表转换为逗号分隔的字符串
                front_str = ','.join(map(str, rec.get('front_numbers', [])))
                back_str = ','.join(map(str, rec.get('back_numbers', [])))

                details_to_insert.append({
                    "recommend_type": rec.get('type', '未知'),
                    "strategy_logic": rec.get('role_in_portfolio', ''),
                    "front_numbers": front_str,
                    "back_numbers": back_str,
                    "win_probability": rec.get('confidence_score', 0.0)  # 复用字段
                })

            # 3. 批量插入推荐详情
            success = db_manager.insert_recommendation_details_batch(
                recommendation_id=root_id,
                details=details_to_insert
            )

            if success:
                print("✅ Recommendation details inserted successfully.")
            else:
                print("❌ FAILED: Could not insert recommendation details.")

        except Exception as e:
            print(f"\n❌ An unexpected error occurred in the pipeline: {e}")
        finally:
            # --- 断开数据库连接 ---
            db_manager.disconnect()
            print("\n" + "=" * 60)
            print("🏁  PIPELINE FINISHED. Database connection closed.")
            print("=" * 60)

    # --- 启动管道 ---
    if __name__ == "__main__":
        run_prediction_pipeline()

if __name__ == "__main__":
    main()
