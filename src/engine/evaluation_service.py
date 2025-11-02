# 文件: src/engine/evaluation_service.py (V6 - 最终修复版)

import json
import re  # 确保导入 re
from src.database.database_manager import DatabaseManager
from src.engine.evaluation_system import EvaluationSystem


def calculate_hits_from_list(predicted_numbers: list, actual_numbers: set) -> int:
    # 确保 predicted_numbers 是一个集合，以处理可能的重复
    return len(set(predicted_numbers) & actual_numbers)


def run_evaluation_for_period(db_manager: DatabaseManager, period_to_evaluate: str):
    """
    对指定期号的所有最终推荐方案执行“奖罚分明”评估。
    这个服务现在只专注于评估最终推荐，不再处理基础算法的日志。
    """
    print(f"\n🔍 开始对第 {period_to_evaluate} 期进行最终推荐评估...")

    # 1. 获取当期开奖结果
    actual_draw_raw = db_manager.execute_query(
        "SELECT * FROM lottery_history WHERE period_number = %s", (period_to_evaluate,)
    )
    if not actual_draw_raw:
        print(f"  - ⚠️ 警告: 在lottery_history表中找不到期号 {period_to_evaluate} 的开奖数据，跳过评估。")
        return
    actual_draw = actual_draw_raw[0]

    # 2. 获取当期所有通过LLM生成的推荐元数据
    recommendations_raw = db_manager.execute_query(
        "SELECT * FROM algorithm_recommendation WHERE period_number = %s", (period_to_evaluate,)
    )
    if not recommendations_raw:
        print(f"  - ✅ 在algorithm_recommendation表中未找到期号 {period_to_evaluate} 的推荐记录，无需评估。")
        return

    print(f"\n  [评估] 发现 {len(recommendations_raw)} 套为第 {period_to_evaluate} 期生成的最终推荐方案。")
    eval_system = EvaluationSystem()

    # 3. 遍历每一套推荐方案
    for rec_main in recommendations_raw:
        rec_id = rec_main['id']
        model_name = rec_main['algorithm_version']

        # 检查是否已评估过，避免重复计算
        existing_reward = db_manager.execute_query(
            "SELECT id FROM reward_penalty_records WHERE recommendation_id = %s", (rec_id,)
        )
        if existing_reward:
            print(f"    - ✅ 模型 '{model_name}' 的推荐(ID:{rec_id}) 已评估过，跳过。")
            continue

        print(f"    --- 正在评估模型 '{model_name}' 的推荐 (ID: {rec_id}) ---")

        # 获取该方案下的所有具体组合
        details_raw = db_manager.execute_query(
            "SELECT * FROM recommendation_details WHERE recommendation_metadata_id = %s", (rec_id,)
        )
        if not details_raw:
            print(f"      - ⚠️ 警告: 找不到推荐ID {rec_id} 的详情记录。")
            continue

        best_hit_score = -1
        best_reward_data = None

        # 4. 在一套方案的所有组合中，找出表现最好的那个进行记录
        for detail in details_raw:
            try:
                # 调用评估系统的核心方法计算奖罚
                reward_data = eval_system.calculate_reward_record(rec_main, detail, actual_draw)

                # 我们只记录这一套方案里，中奖效果最好的那个组合
                if reward_data['hit_score'] > best_hit_score:
                    best_hit_score = reward_data['hit_score']
                    best_reward_data = reward_data
            except Exception as e:
                print(f"      - ❌ 计算组合 {detail.get('id')} 表现时出错: {e}")
                continue

        # 5. 将最佳表现的奖罚记录存入数据库
        if best_reward_data:
            try:
                self.db.execute_insert('reward_penalty_records', best_reward_data)
                print(f"      - ✅ 评估完成！最高得分: {best_hit_score}。奖罚记录已存入数据库。")
            except Exception as e:
                print(f"      - ❌ 存储奖罚记录 (推荐ID: {rec_id}) 到数据库时失败: {e}")
        else:
            print("      - ℹ️ 该推荐方案中的所有组合均未命中。")

# 文件: src/engine/evaluation_service.py

def _evaluate_base_algorithms_logs(db_manager, period, actual_front, actual_back):
    """
    辅助函数: 评估基础算法并更新 algorithm_performance。
    (V4 - 修复了 Decimal 与 float 的类型冲突，并增强了健壮性)
    """
    prediction_logs = db_manager.execute_query(
        "SELECT * FROM algorithm_prediction_logs WHERE period_number = %s", (period,)
    )
    if not prediction_logs:
        return

    print(f"\n  [评估1/2] 正在评估 {len(prediction_logs)} 个基础算法的长期性能...")
    for log in prediction_logs:
        algo_version = log['algorithm_version']
        try:
            if not log['predictions']:
                continue
            predictions = json.loads(log['predictions'])
            primary_rec = predictions.get('recommendations', [{}])[0]

            front_hits = calculate_hits_from_list(primary_rec.get('front_numbers', []), actual_front)
            back_hits = calculate_hits_from_list(primary_rec.get('back_numbers', []), actual_back)

            # --- 核心修复：在这里进行类型转换和计算 ---

            # 1. 读取旧的统计数据
            current_stats_raw = db_manager.execute_query(
                "SELECT total_periods_analyzed, avg_front_hit_rate, avg_back_hit_rate FROM algorithm_performance WHERE algorithm_version = %s",
                (algo_version,)
            )

            # 2. 计算本期表现 (使用 float 类型)
            current_front_hit_rate = float(front_hits / 5.0)
            current_back_hit_rate = float(back_hits / 2.0)

            if not current_stats_raw:
                # 如果没有旧记录，直接插入一条全新的性能记录
                print(f"    - ⚠️ 警告: 未找到 {algo_version} 的性能记录，正在为其创建初始记录...")
                # 注意：这里的 INSERT 语句需要与您的 algorithm_performance 表结构完全匹配
                # 这是一个基于您之前提供的“超级表”结构的示例
                insert_sql = """
                             INSERT INTO algorithm_performance
                             (algorithm_version, issue, algorithm, period_number, total_periods_analyzed, \
                              total_recommendations,
                              avg_front_hit_rate, avg_back_hit_rate, hits, hit_rate, score)
                             VALUES (%s, %s, %s, %s, 1, 1, %s, %s, %s, %s, %s) \
                             """
                # 从版本号中分离出算法名
                algorithm_name = algo_version.split('_')[0]

                # 计算 hits, hit_rate, score
                total_hits = front_hits + back_hits
                hit_rate = total_hits / 7.0
                confidence_score = float(log.get('confidence_score', 0.5))
                score = hit_rate * confidence_score

                db_manager.execute_update(
                    insert_sql,
                    (algo_version, period, algorithm_name, period, current_front_hit_rate, current_back_hit_rate,
                     total_hits, hit_rate, score)
                )
                continue

            # 3. (关键) 将从数据库读出的 Decimal/None 安全地转换为 float
            current_stats = current_stats_raw[0]
            total_periods = int(current_stats.get('total_periods_analyzed') or 0)
            old_front_rate = float(current_stats.get('avg_front_hit_rate') or 0.0)
            old_back_rate = float(current_stats.get('avg_back_hit_rate') or 0.0)

            # 4. 现在，所有变量都是 Python 的原生数字类型，可以安全计算
            new_total_periods = total_periods + 1
            new_front_rate = ((old_front_rate * total_periods) + current_front_hit_rate) / new_total_periods
            new_back_rate = ((old_back_rate * total_periods) + current_back_hit_rate) / new_total_periods

            # 5. 更新数据库中的长期统计数据
            update_sql = """
                         UPDATE algorithm_performance
                         SET total_periods_analyzed = %s,
                             total_recommendations  = total_recommendations + 1,
                             avg_front_hit_rate     = %s,
                             avg_back_hit_rate      = %s,
                             last_updated           = NOW()
                         WHERE algorithm_version = %s \
                         """
            params = (new_total_periods, new_front_rate, new_back_rate, algo_version)
            if db_manager.execute_update(update_sql, params):
                print(f"  - 算法: {algo_version} -> 命中: {front_hits}+{back_hits}。长期性能已更新。")

        except Exception as e:
            print(f"  - ❌ 评估基础算法 {algo_version} 时出错: {e}")


def _evaluate_final_recommendations(db_manager, period, actual_draw):
    """
    辅助函数: 评估最终推荐并生成奖罚记录。(V3 - 修复导入路径)
    """
    # --- 核心修复：从正确的 evaluation_system 导入 ---
    # Python 3.8+ 推荐使用相对导入
    from ..engine.evaluation_system import EvaluationSystem
    # 如果上面的导入报错，请尝试绝对导入：
    # from src.engine.evaluation_system import EvaluationSystem
    eval_system = EvaluationSystem()

    recommendations_raw = db_manager.execute_query("SELECT * FROM algorithm_recommendation WHERE period_number = %s",
                                                   (period,))
    if not recommendations_raw: return

    print(f"\n  [评估2/2] 正在为 {len(recommendations_raw)} 套最终推荐方案生成“奖罚记录”...")
    for rec in recommendations_raw:
        rec_id = rec['id']
        model_name = rec['algorithm_version']

        existing_reward = db_manager.execute_query("SELECT id FROM reward_penalty_records WHERE recommendation_id = %s",
                                                   (rec_id,))
        if existing_reward:
            print(f"    - ✅ 模型 '{model_name}' 的这条推荐(ID:{rec_id}) 已评估过，跳过。")
            continue

        print(f"    --- 正在评估模型 '{model_name}' 的推荐 (ID: {rec_id}) ---")

        details_raw = db_manager.execute_query(
            "SELECT * FROM recommendation_details WHERE recommendation_metadata_id = %s", (rec_id,))
        if not details_raw:
            print(f"      - ⚠️ 警告: 找不到推荐ID {rec_id} 的详情记录。")
            continue

        best_hit_score = -1
        best_reward_data = None

        for detail in details_raw:
            try:
                reward_data = eval_system.calculate_reward_record(rec, detail, actual_draw)
                if reward_data['hit_score'] > best_hit_score:
                    best_hit_score = reward_data['hit_score']
                    best_reward_data = reward_data
            except Exception as e:
                print(f"      - ❌ 计算组合 {detail.get('id')} 表现时出错: {e}")
                continue

        if best_reward_data:
            db_manager.execute_insert('reward_penalty_records', best_reward_data)
            print(f"      - ✅ 评估完成！最高得分: {best_hit_score}。奖罚记录已存入。")