# 文件: src/engine/system_orchestrator.py (V2 - 具备冷启动能力)

import json
from collections import Counter, defaultdict
from typing import List, Dict

from src.database.database_manager import DatabaseManager
from src.engine.recommendation_engine import RecommendationEngine
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.algorithms import AVAILABLE_ALGORITHMS  # 使用我们创建的算法注册表


class SystemOrchestrator:
    """系统协调器，负责处理核心的后台任务和生命周期管理。"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        # self.engine = self._initialize_engine() # Engine 在需要时再初始化

    def _initialize_engine(self):
        """初始化一个用于回填和分析的推荐引擎实例。"""
        # --- 核心修改：确保导入路径正确 ---
        # 确认这个导入没有红色波浪线
        from src.engine.algorithm_factory import AlgorithmFactory
        base_algorithms = AlgorithmFactory.get_active_algorithms(self.db)
        chief_strategy_officer = DynamicEnsembleOptimizer(base_algorithms)
        engine = RecommendationEngine()
        engine.set_meta_algorithm(chief_strategy_officer)
        return engine

    def backfill_analysis_basis(self):
        """
        回填历史上缺失的 analysis_basis 字段。
        """
        print("\n" + "=" * 50)
        print("🛠️  开始回填历史 `analysis_basis` 数据...")
        print("=" * 50)

        engine = self._initialize_engine()  # 在需要时才创建引擎实例

        query = "SELECT period_number FROM algorithm_recommendation WHERE analysis_basis IS NULL OR analysis_basis = '' OR analysis_basis = '{}' ORDER BY period_number"
        records_to_fill = self.db.execute_query(query)
        issues_to_fill = [r['period_number'] for r in records_to_fill]

        if not issues_to_fill:
            print("  - ✅ 无需回填。")
            return

        print(f"  - 🔎 发现 {len(issues_to_fill)} 条记录需要回填。")
        all_history = self.db.get_latest_lottery_history(limit=10000)

        for i, issue_str in enumerate(issues_to_fill):
            print(f"\n--- 正在处理期号: {issue_str} ({i + 1}/{len(issues_to_fill)}) ---")

            # 找到当前期号在历史数据中的索引
            try:
                current_index = next(i for i, draw in enumerate(all_history) if draw.period_number == issue_str)
            except StopIteration:
                print(f"  - ⚠️ 警告: 在加载的历史数据中找不到期号 {issue_str}，跳过。")
                continue

            history_for_run = all_history[:current_index]

            if len(history_for_run) < 20:
                print(f"  - ⏸️  跳过: 期号 {issue_str} 的前置历史数据不足20期。")
                continue

            final_report = engine.generate_final_recommendation(
                history_data=history_for_run
            )
            analysis_basis_json = json.dumps(final_report, ensure_ascii=False)

            update_query = "UPDATE algorithm_recommendation SET analysis_basis = %s WHERE period_number = %s AND (analysis_basis IS NULL OR analysis_basis = '' OR analysis_basis = '{}')"
            self.db.execute_update(update_query, (analysis_basis_json, issue_str))
            print(f"  - ✅ 成功回填期号 {issue_str} 的分析数据。")

    # --- 这是您需要的完整函数 ---
    def populate_number_statistics(self):
        """
        从 lottery_history 计算并填充 number_statistics 表的完整方法。
        """
        print("  - [Orchestrator] 开始计算并填充号码统计数据（冷启动）...")
        try:
            # 1. 获取所有历史数据，按期号升序排列
            all_history_raw = self.db.execute_query("SELECT * FROM lottery_history ORDER BY period_number ASC")
            if not all_history_raw:
                print("    - ⚠️ 历史数据为空，无法进行统计填充。")
                return

            total_draws = len(all_history_raw)
            print(f"    - 发现 {total_draws} 期历史数据用于统计分析。")

            # 2. 初始化数据结构
            front_numbers_range = range(1, 36)
            back_numbers_range = range(1, 13)

            # 用于统计出现次数
            front_counts = Counter()
            back_counts = Counter()

            # 用于统计遗漏值
            front_omissions = {num: 0 for num in front_numbers_range}
            back_omissions = {num: 0 for num in back_numbers_range}
            front_max_omission = defaultdict(int)
            back_max_omission = defaultdict(int)
            front_omission_history = defaultdict(list)
            back_omission_history = defaultdict(list)

            # 3. 遍历所有历史数据进行计算
            for draw in all_history_raw:
                # 提取当期号码
                current_front = {draw[f'front_area_{i + 1}'] for i in range(5)}
                current_back = {draw[f'back_area_{i + 1}'] for i in range(2)}

                # 更新出现次数
                front_counts.update(current_front)
                back_counts.update(current_back)

                # 更新遗漏值
                for num in front_numbers_range:
                    if num in current_front:
                        front_omission_history[num].append(front_omissions[num])
                        front_omissions[num] = 0
                    else:
                        front_omissions[num] += 1
                        front_max_omission[num] = max(front_max_omission[num], front_omissions[num])

                for num in back_numbers_range:
                    if num in current_back:
                        back_omission_history[num].append(back_omissions[num])
                        back_omissions[num] = 0
                    else:
                        back_omissions[num] += 1
                        back_max_omission[num] = max(back_max_omission[num], back_omissions[num])

            # 4. 准备批量插入的数据
            stats_to_insert = []

            # 处理前区号码
            for num in front_numbers_range:
                appearances = front_counts.get(num, 0)
                omission_hist = front_omission_history.get(num, [0])
                stats_to_insert.append({
                    'number': num,
                    'number_type': 'front',
                    'total_appearances': appearances,
                    'appearance_rate': round(appearances / total_draws, 4) if total_draws > 0 else 0,
                    'current_omission': front_omissions[num],
                    'max_omission': front_max_omission[num],
                    'avg_omission': round(sum(omission_hist) / len(omission_hist), 2) if omission_hist else 0,
                })

            # 处理后区号码
            for num in back_numbers_range:
                appearances = back_counts.get(num, 0)
                omission_hist = back_omission_history.get(num, [0])
                stats_to_insert.append({
                    'number': num,
                    'number_type': 'back',
                    'total_appearances': appearances,
                    'appearance_rate': round(appearances / total_draws, 4) if total_draws > 0 else 0,
                    'current_omission': back_omissions[num],
                    'max_omission': back_max_omission[num],
                    'avg_omission': round(sum(omission_hist) / len(omission_hist), 2) if omission_hist else 0,
                })

            # 5. 执行数据库操作：先清空，再批量插入
            print("    - 正在清空旧的号码统计数据...")
            self.db.execute_update("TRUNCATE TABLE number_statistics")

            print(f"    - 正在批量插入 {len(stats_to_insert)} 条新的统计记录...")
            for stats_data in stats_to_insert:
                self.db.execute_insert('number_statistics', stats_data)

            print("  - ✅ [Orchestrator] 号码统计数据填充成功！")

        except Exception as e:
            print(f"  - ❌ [Orchestrator] 填充号码统计数据时发生严重错误: {e}")
            import traceback
            traceback.print_exc()