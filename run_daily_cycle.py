# 文件: run_daily_cycle.py (已修复缩进错误)

import os
import sys
import json
import argparse
from typing import Set

# --- 环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path: sys.path.insert(0, project_root)

# --- 核心组件导入 ---
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from src.algorithms import AVAILABLE_ALGORITHMS
from src.model.lottery_models import LotteryHistory
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.engine.recommendation_engine import RecommendationEngine
from src.engine.imperial_senate import ImperialSenate
from src.prompt_templates import build_final_mandate_prompt
from src.llm.clients import get_llm_client

# --- 全局配置 ---
MODELS_TO_SIMULATE = ["qwen3-max",
                      "gpt-4o",  # 将来要用时取消注释
                      "gemini-2.5-flash",
                      "deepseek-chat"]
NUM_PERIODS_TO_SIMULATE = 9999


class DailyCycleRunner:
    """ “帝国一日”总调度器 (稳定版) """

    def __init__(self, db_config: dict, force_rerun: bool = False):
        self.db = DatabaseManager(**db_config)
        self.force_rerun = force_rerun
        if not self.db.connect(): raise ConnectionError("数据库连接失败")

    def run_all(self):
        print("\n" + "#" * 70 + "\n###      ☀️  “帝国一日”自动化流程启动      ###\n" + "#" * 70)
        if self.force_rerun: self._cleanup_for_rerun()
        self._run_base_algorithm_evaluation()
        self._run_full_historical_simulation()
        self._run_llm_backtesting()
        print("\n" + "#" * 70 + "\n###      🌙  “帝国一日”自动化流程全部执行完毕      ###\n" + "#" * 70)
        self.db.disconnect()

    def _cleanup_for_rerun(self):
        print("\n⚠️  --force 模式，正在清理所有模拟与评估数据...")
        # 严格按顺序
        self.db.execute_update("TRUNCATE TABLE backtest_results;")
        self.db.execute_update("TRUNCATE TABLE reward_penalty_records;")
        self.db.execute_update("TRUNCATE TABLE prediction_outputs;")
        self.db.execute_update("TRUNCATE TABLE recommendation_details;")
        self.db.execute_update("TRUNCATE TABLE algorithm_recommendation;")
        self.db.execute_update("TRUNCATE TABLE algorithm_performance;")
        print("  - ✅ 清理完毕。")

    def _run_base_algorithm_evaluation(self):
        print("\n" + "=" * 70 + "\n=== 步骤 1/3: 基础算法历史表现评估 (智能写入) ===")
        print("=" * 70)
        all_history_raw = self.db.execute_query("SELECT * FROM lottery_history ORDER BY period_number ASC")
        all_history = self.db._convert_rows_to_history_list(all_history_raw)
        if len(all_history) < 30: return

        for algo_name, AlgoClass in AVAILABLE_ALGORITHMS.items():
            if algo_name == "DynamicEnsembleOptimizer": continue

            print(f"\n🏃‍♂️ 正在评估选手: {algo_name}")
            algorithm = AlgoClass()
            performance_params_list = []
            for i in range(30, len(all_history)):
                training_data, actual_draw = all_history[:i], all_history[i]
                algorithm.train(training_data)
                prediction = algorithm.predict(training_data)
                rec = prediction['recommendations'][0]
                front_scores, back_scores = rec.get('front_number_scores', []), rec.get('back_number_scores', [])
                if not front_scores or not back_scores: continue
                predicted_front, predicted_back = {item['number'] for item in front_scores[:5]}, {item['number'] for
                                                                                                  item in
                                                                                                  back_scores[:2]}
                hits = len(predicted_front & set(actual_draw.front_area)) + len(
                    predicted_back & set(actual_draw.back_area))
                confidence = rec.get('confidence', 0.5)
                hit_rate = hits / 7.0
                score = hit_rate * confidence
                performance_params_list.append(
                    (actual_draw.period_number, algo_name, algorithm.version, float(hits), round(hit_rate, 4),
                     round(score, 4))
                )

            if performance_params_list:
                print(f"  - ✍️  正在为 {algo_name} 智能写入/更新 {len(performance_params_list)} 条历史战报...")
                query = """
                        INSERT INTO algorithm_performance (issue, algorithm, algorithm_version, hits, hit_rate, score)
                        VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                        UPDATE
                            algorithm_version = \
                        VALUES (algorithm_version), hits = \
                        VALUES (hits), hit_rate = \
                        VALUES (hit_rate), score = \
                        VALUES (score), updated_at = NOW();
                        """
                success = self.db.execute_batch_insert(query, performance_params_list)
                if success:
                    print(f"  - ✅ {algo_name} 的历史战报已全部智能写入。")
                else:
                    print(f"  - ❌ {algo_name} 的历史战报写入失败。")

    # <<< 这里是关键修复：将下面的函数定义取消缩进，使其成为类的正确方法 >>>
    def _run_full_historical_simulation(self):
        print("\n" + "=" * 70 + "\n=== 步骤 2/3: LLM 全流程历史决策模拟 (动态引擎版) ===")
        print("=" * 70)
        all_history_in_mem_raw = self.db.execute_query("SELECT * FROM lottery_history ORDER BY period_number ASC")
        all_history_in_mem = self.db._convert_rows_to_history_list(all_history_in_mem_raw)

        for llm_model_name in MODELS_TO_SIMULATE:
            print(f"\n--- 开始对模型: [{llm_model_name}] 进行模拟 ---")
            periods_to_simulate = all_history_in_mem[30:]

            for i, target_draw in enumerate(periods_to_simulate, 1):
                target_period = target_draw.period_number
                print(
                    f"\n--- 模拟进度 [{llm_model_name}]: {i}/{len(periods_to_simulate)} (期号: {target_period}) ---")

                try:
                    training_data = all_history_in_mem[:30 + i - 1]

                    base_scorers = [AlgoClass() for name, AlgoClass in AVAILABLE_ALGORITHMS.items() if
                                    name != "DynamicEnsembleOptimizer"]

                    # 假设 DynamicEnsembleOptimizer 构造函数已更新以接受 db_manager
                    fusion_algorithm = DynamicEnsembleOptimizer(base_algorithms=base_scorers, db_manager=self.db)

                    engine = RecommendationEngine(base_scorers=base_scorers, fusion_algorithm=fusion_algorithm)
                    print("  - [诊断] 正在调用核心推荐引擎生成所有模型输出...")
                    model_outputs = engine.generate_all_recommendations(training_data)
                    print("  - [诊断] 引擎运行完毕。")

                    senate = ImperialSenate(self.db, {}, model_outputs)
                    edict, quant_prop, ml_brief = senate.generate_all_briefings(training_data, "上期ROI-2%")

                    prompt_text, _ = build_final_mandate_prompt(
                        recent_draws=training_data,
                        model_outputs=model_outputs,
                        performance_log={},
                        next_issue_hint=target_period,
                        last_performance_report="上期ROI-2%",
                        senate_edict=edict,
                        quant_proposal=quant_prop,
                        ml_briefing=ml_brief
                    )

                    print("  - [诊断] 正在调用 LLM...")
                    llm_client = get_llm_client(llm_model_name)
                    response_str = llm_client.generate(system_prompt=prompt_text,
                                                       user_prompt="Your Majesty, your final decree.",
                                                       json_mode=True)
                    response_data = json.loads(response_str.strip().replace('```json', '').replace('```', ''))
                    print("  - [诊断] LLM 返回并解析成功。")

                    recommend_time = self.db.get_current_time()
                    meta_data = {'period_number': target_period, 'recommend_time': recommend_time,
                                 'algorithm_version': f"TheFinalMandate_{llm_model_name}_V1.2_DynamicSim",
                                 'confidence_score': 0.9 if response_data.get('self_check', {}).get('e_hits_ok',
                                                                                                    False) else 0.7,
                                 'risk_level': '中性',
                                 'analysis_basis': json.dumps(model_outputs, ensure_ascii=False, default=str),
                                 # 添加 default=str 以防序列化问题
                                 'llm_cognitive_details': json.dumps(
                                     {'senate_edict': edict, 'quant_proposal': json.loads(quant_prop),
                                      'ml_briefing': json.loads(ml_brief),
                                      'final_memo': response_data.get('edict', {}).get('final_memo')},
                                     ensure_ascii=False), 'models': llm_model_name}

                    recommendation_id = self.db.execute_insert('algorithm_recommendation', meta_data)
                    if not recommendation_id: recommendation_id = self.db.get_last_insert_id()
                    if not recommendation_id: raise Exception("插入元数据后未能获取 ID。")

                    final_edict = response_data.get('edict', {})
                    portfolio = final_edict.get('final_imperial_portfolio', {})
                    recommendations = portfolio.get('recommendations', [])

                    if recommendations:
                        details_to_insert = [(recommendation_id, r.get('type'), r.get('role'),
                                              ','.join(map(str, r.get('front_numbers', []))),
                                              ','.join(map(str, r.get('back_numbers', []))), r.get('sharpe')) for r
                                             in recommendations]
                        self.db.execute_batch_insert(
                            "INSERT INTO recommendation_details (recommendation_metadata_id, recommend_type, strategy_logic, front_numbers, back_numbers, win_probability) VALUES (%s, %s, %s, %s, %s, %s)",
                            details_to_insert)

                    output_data = {"recommendation_id": recommendation_id, "issue": target_period,
                                   "model_name": llm_model_name,
                                   "portfolio": json.dumps(portfolio, ensure_ascii=False),
                                   "memo": final_edict.get('final_memo'),
                                   "expected_hits_range": str(portfolio.get('overall_e_hits_range', 'N/A')),
                                   "predicted_roi": portfolio.get('allocation_summary', '')[:250],
                                   "self_check_details": json.dumps(response_data.get('self_check', {}),
                                                                    ensure_ascii=False)}
                    self.db.execute_insert('prediction_outputs', output_data)
                    print(f"  - ✅ 已为期号 {target_period} 成功存入双轨制数据。")

                except Exception as e:
                    print(f"\n  - ❌❌❌ 在处理期号 {target_period} 时发生致命错误！ ❌❌❌")
                    import traceback
                    traceback.print_exc()
                    continue

    # <<< 这里是关键修复：将下面的函数定义取消缩进，使其成为类的正确方法 >>>
    def _run_llm_backtesting(self):
        print("\n" + "=" * 70 + "\n=== 步骤 3/3: LLM 决策功绩评估 (奖罚分明) ===")
        print("=" * 70)
        untested_predictions = self.db.execute_query(
            "SELECT po.id, po.recommendation_id, po.issue, po.model_name, po.portfolio FROM prediction_outputs po LEFT JOIN reward_penalty_records rpr ON po.recommendation_id = rpr.recommendation_id WHERE rpr.id IS NULL")
        if not untested_predictions: print("✅ 所有历史决策均已评估并记录奖罚。"); return
        print(f"🔎 发现 {len(untested_predictions)} 条尚未进行奖罚评估的历史决策。")
        issues_to_check = {p['issue'] for p in untested_predictions}
        placeholders = ','.join(['%s'] * len(issues_to_check))
        history_rows = self.db.execute_query(
            f"SELECT period_number, front_area_1, front_area_2, front_area_3, front_area_4, front_area_5, back_area_1, back_area_2 FROM lottery_history WHERE period_number IN ({placeholders})",
            tuple(issues_to_check))
        actual_draws = {row['period_number']: {"front": {row[f'front_area_{i + 1}'] for i in range(5)},
                                               "back": {row[f'back_area_{i + 1}'] for i in range(2)}} for row in
                        history_rows}
        for prediction in untested_predictions:
            issue = prediction['issue']
            if issue not in actual_draws: continue
            try:
                portfolio = json.loads(prediction['portfolio'])
                recommendations = portfolio.get('recommendations', [])
                actual = actual_draws[issue]
                best_front_hits, best_back_hits = 0, 0  # 初始化为0
                for rec in recommendations:
                    pred_front, pred_back = set(map(int, rec.get('front_numbers', []))), set(
                        map(int, rec.get('back_numbers', [])))
                    front_hits, back_hits = len(pred_front & actual['front']), len(pred_back & actual['back'])
                    if front_hits + back_hits > best_front_hits + best_back_hits:
                        best_front_hits, best_back_hits = front_hits, back_hits
                hit_score = (best_front_hits * 10) + (best_back_hits * 25)
                reward_info = {"hit_score": hit_score, "reward_points": hit_score * 1.5,
                               "penalty_points": 0 if hit_score > 5 else 50,
                               "net_points": (hit_score * 1.5) - (0 if hit_score > 5 else 50)}
                reward_record_data = {"period_number": issue,
                                      "algorithm_version": f"TheFinalMandate_{prediction['model_name']}_V1.1_Simulated",
                                      "recommendation_id": prediction['recommendation_id'],
                                      "front_hit_count": best_front_hits, "back_hit_count": best_back_hits,
                                      **reward_info}
                self.db.execute_insert('reward_penalty_records', reward_record_data)
                print(
                    f"  - ✅ 已评估期号 {issue} (模型: {prediction['model_name']})，净得分: {reward_info['net_points']}。")
            except Exception as e:
                print(f"  - ❌ 评估期号 {issue} 失败: {e}")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="“帝国一日”总调度器：一键完成清理、模拟与评估。")
    parser.add_argument('--force', action='store_true', help='强制重新运行，会先清空所有历史模拟与评估数据。')
    args = parser.parse_args()

    runner = DailyCycleRunner(DB_CONFIG, force_rerun=args.force)
    runner.run_all()