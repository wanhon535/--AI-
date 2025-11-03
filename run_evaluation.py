import os
import sys
import json

# --- 环境设置 (保持不变) ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path: sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from src.algorithms import AVAILABLE_ALGORITHMS


def run_base_algorithm_evaluation_and_get_recommendation():
    """
    最终版: 融合了智能写入逻辑，确保高效且无重复错误。
    """
    print("\n" + "#" * 70 + "\n###      🔥 终极回测 & 今晚决策引擎 (智能写入版)      ###\n" + "#" * 70)

    db = DatabaseManager(**DB_CONFIG)
    if not db.connect():
        print("❌ 数据库连接失败，终止。")
        return

    try:
        # (步骤 1 和 2 保持不变)
        all_history_raw = db.execute_query("SELECT * FROM lottery_history ORDER BY period_number ASC")
        all_history = db._convert_rows_to_history_list(all_history_raw)
        if len(all_history) < 30:
            print(f"❌ 历史数据不足30期 (仅 {len(all_history)} 期)，无法进行有效评估。")
            return
        print(f"✅ 已加载 {len(all_history)} 期完整历史数据用于模拟评估。")

        algorithm_total_scores = {}

        print("\n" + "=" * 60)
        print("🧹 正在清空旧的算法表现记录...")
        db.execute_update("TRUNCATE TABLE algorithm_performance;")
        print("  - ✅ `algorithm_performance` 表已清空。")

        # (步骤 3 遍历算法，保持不变)
        for algo_name, AlgoClass in AVAILABLE_ALGORITHMS.items():
            if algo_name == "DynamicEnsembleOptimizer": continue

            print("\n" + "=" * 60)
            print(f"🏃‍♂️ 正在模拟评估选手: {algo_name}")

            algorithm = AlgoClass()

            # <<< 核心升级 1/2: 准备用于批量智能写入的数据 >>>
            # 我们不再准备字典列表，而是准备元组(tuple)列表，以匹配 executemany 的要求
            performance_params_list = []

            periods_to_test = len(all_history) - 30
            for i in range(30, len(all_history)):
                # (内部的回测计算逻辑完全不变)
                training_data, actual_draw = all_history[:i], all_history[i]
                algorithm.train(training_data)
                prediction = algorithm.predict(training_data)
                rec = prediction.get('recommendations', [{}])[0]
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

                # 将该期的数据作为一个元组添加到列表中
                performance_params_list.append(
                    (
                        actual_draw.period_number,
                        algo_name,
                        algorithm.version,
                        json.dumps({"front": sorted(list(predicted_front)), "back": sorted(list(predicted_back))}),
                        confidence,
                        float(hits),
                        round(hit_rate, 4),
                        round(score, 4)
                    )
                )

            # <<< 核心升级 2/2: 使用单次、高效的批量智能写入 >>>
            if performance_params_list:
                print(f"\n  - ✍️  正在为 {algo_name} 智能写入/更新 {len(performance_params_list)} 条历史战报...")

                query = """
                INSERT INTO algorithm_performance (issue, algorithm, algorithm_version, predictions, confidence_score, hits, hit_rate, score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    algorithm_version = VALUES(algorithm_version),
                    predictions = VALUES(predictions),
                    confidence_score = VALUES(confidence_score),
                    hits = VALUES(hits),
                    hit_rate = VALUES(hit_rate),
                    score = VALUES(score),
                    updated_at = NOW();
                """
                success = db.execute_batch_insert(query, performance_params_list)

                if success:
                    print(f"  - ✅ {algo_name} 的历史战报已全部智能写入。")
                    # 累加总分 (需要从元组中提取)
                    algorithm_total_scores[algo_name] = sum(
                        record[7] for record in performance_params_list)  # score是第8个元素(索引7)
                else:
                    print(f"  - ❌ {algo_name} 的历史战报批量写入失败。")

        # (步骤 5 和 6，找出冠军并生成推荐的逻辑，完全不变)
        if not algorithm_total_scores:
            print("\n❌ 未能计算出任何算法的评分，无法推荐。")
            return

        champion_algo_name = max(algorithm_total_scores, key=algorithm_total_scores.get)
        print("\n" + "#" * 70 + "\n###      🏆 算法选拔赛结束！最终排名如下：      ###\n" + "#" * 70)
        sorted_scores = sorted(algorithm_total_scores.items(), key=lambda item: item[1], reverse=True)
        for name, total_score in sorted_scores:
            print(f"  - {name:<25}: 综合总分 {total_score:.2f} {'👑' if name == champion_algo_name else ''}")

        print("\n" + "=" * 60 + f"\n👑 正在使用冠军算法 ({champion_algo_name}) 生成今晚的决策...")
        ChampionAlgoClass = AVAILABLE_ALGORITHMS[champion_algo_name]
        champion_instance = ChampionAlgoClass()
        champion_instance.train(all_history)
        final_prediction = champion_instance.predict(all_history)
        final_rec = final_prediction['recommendations'][0]
        final_front_scores = final_rec['front_number_scores']
        final_back_scores = final_rec['back_number_scores']

        print("\n" + "#" * 70 + f"\n###      🔥 今晚 ({db.get_next_period_number()}期) 决策参考      ###\n" + "#" * 70)
        print(f"基于冠军算法: {champion_algo_name} (版本: {champion_instance.version})")
        print("-" * 70)
        print(f"号码池-前区高分 (Top 10): {[item['number'] for item in final_front_scores[:10]]}")
        print(f"号码池-后区高分 (Top 5):  {[item['number'] for item in final_back_scores[:5]]}")
        print("-" * 70)
        print("【建议组合 (仅供参考)】")
        print(
            f"  - 稳健组合 (5+2): 前区 {[item['number'] for item in final_front_scores[:5]]} | 后区 {[item['number'] for item in final_back_scores[:2]]}")
        print(
            f"  - 激进组合 (7+3): 前区 {[item['number'] for item in final_front_scores[:7]]} | 后区 {[item['number'] for item in final_back_scores[:3]]}")
        print("#" * 70)
        print("⚠️  警告：过去的表现不预示未来的结果。请理性投注，控制风险。")

    finally:
        if db and db.is_connected():
            db.disconnect()


if __name__ == "__main__":
    run_base_algorithm_evaluation_and_get_recommendation()