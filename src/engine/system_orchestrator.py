# file: src/engine/system_orchestrator.py

import json
import traceback
from collections import Counter
from typing import List

from src.database.database_manager import DatabaseManager
from src.engine.recommendation_engine import RecommendationEngine
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.algorithms.statistical_algorithms import (
    FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, OmissionValueAlgorithm
)
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer
from src.model.lottery_models import LotteryHistory


class SystemOrchestrator:
    """系统协调器，负责处理核心的后台任务和生命周期管理。"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.engine = self._initialize_engine()

    def _initialize_engine(self):
        """初始化一个用于回填和分析的推荐引擎实例。"""
        base_algorithms = [
            FrequencyAnalysisAlgorithm(), HotColdNumberAlgorithm(), OmissionValueAlgorithm(),
            BayesianNumberPredictor(), MarkovTransitionModel(), NumberGraphAnalyzer(),
        ]
        chief_strategy_officer = DynamicEnsembleOptimizer(base_algorithms)
        engine = RecommendationEngine()
        engine.set_meta_algorithm(chief_strategy_officer)
        return engine

    def check_and_initialize_data(self):
        """
        检查并初始化系统的基础数据（“冷启动”核心功能）。
        """
        print("\n" + "=" * 50)
        print("🔍 检查并初始化系统基础数据...")
        print("=" * 50)
        self._populate_number_statistics()
        self._populate_algorithm_configs()

    def backfill_analysis_basis(self):
        """
        回填历史上缺失的 analysis_basis 字段。
        """
        print("\n" + "=" * 50)
        print("🛠️  开始回填历史 `analysis_basis` 数据...")
        print("=" * 50)

        query = "SELECT period_number FROM algorithm_recommendation WHERE analysis_basis IS NULL OR analysis_basis = '' ORDER BY period_number"
        records_to_fill = self.db.execute_query(query)
        issues_to_fill = [r['period_number'] for r in records_to_fill]

        if not issues_to_fill:
            print("✅ 无需回填。")
            return

        print(f"🔎 发现 {len(issues_to_fill)} 条记录需要回填。")
        all_history = self.db.get_latest_lottery_history(limit=10000)

        for i, issue_str in enumerate(issues_to_fill):
            print(f"\n--- 正在处理期号: {issue_str} ({i + 1}/{len(issues_to_fill)}) ---")
            history_for_run = [d for d in all_history if int(d.period_number) < int(issue_str)]
            if len(history_for_run) < 20: continue

            final_report = self.engine.generate_final_recommendation(history_for_run)
            analysis_basis_json = json.dumps(final_report, ensure_ascii=False)

            update_query = "UPDATE algorithm_recommendation SET analysis_basis = %s WHERE period_number = %s"
            self.db.execute_update(update_query, (analysis_basis_json, issue_str))
            print(f"  - ✅ 成功写入期号 {issue_str} 的分析数据。")

    def run_learning_from_history(self):
        """
        运行完整的历史学习流程（调用回测脚本的逻辑）。
        """
        print("\n" + "=" * 50)
        print("🧠 开始从历史中学习性能权重...")
        print("=" * 50)
        # 这里我们直接调用 run_backtest_simulation.py 的核心类
        # 为了简单，这里只打印提示信息，实际调用由 main.py 发起
        print("请运行 'python run_backtest_simulation.py --auto' 来执行此操作。")
        print("在未来的版本中，可以将 BacktestRunner 类导入并在此处直接调用。")

    def _populate_number_statistics(self):
        """填充 number_statistics 表。"""
        print("\n--- 正在填充 [number_statistics] 表 ---")
        try:
            history_dao = self.db.get_dao('LotteryHistoryDAO')
            all_history = history_dao.get_lottery_history(limit=10000)
            if not all_history:
                print("❌ `lottery_history` 为空。")
                return

            front_counts = Counter(num for draw in all_history for num in draw.front_area)
            back_counts = Counter(num for draw in all_history for num in draw.back_area)
            total_draws = len(all_history)

            self.db.execute_update("DELETE FROM number_statistics")

            stats_to_insert = []
            for num in range(1, 36): stats_to_insert.append(
                ('front', num, front_counts.get(num, 0), round(front_counts.get(num, 0) / total_draws, 6)))
            for num in range(1, 13): stats_to_insert.append(
                ('back', num, back_counts.get(num, 0), round(back_counts.get(num, 0) / total_draws, 6)))

            query = "INSERT INTO number_statistics (number_type, number_value, frequency, appearance_rate) VALUES (%s, %s, %s, %s)"
            # 假设您有一个批量插入的方法
            self.db.get_dao('NumberStatisticsDAO').execute_many(query, stats_to_insert)
            print(f"✅ 成功填充 number_statistics。")
        except Exception as e:
            print(f"❌ 填充 number_statistics 时出错: {e}")

    def _populate_algorithm_configs(self):
        """填充 algorithm_configs 表。"""
        print("\n--- 正在填充 [algorithm_configs] 表 ---")
        default_configs = [
            ('FrequencyAnalysisAlgorithm', 'statistical', '{"lookback_period": 100}', True),
            ('HotColdNumberAlgorithm', 'statistical', '{"hot_count": 5, "cold_count": 5}', True),
            # ... 其他算法 ...
            ('DynamicEnsembleOptimizer', 'meta', '{}', True)
        ]
        try:
            self.db.execute_update("DELETE FROM algorithm_configs")
            query = "INSERT INTO algorithm_configs (algorithm_name, algorithm_type, default_parameters, is_active) VALUES (%s, %s, %s, %s)"
            self.db.get_dao('AlgorithmConfigDAO').execute_many(query, default_configs)
            print(f"✅ 成功填充 algorithm_configs。")
        except Exception as e:
            print(f"❌ 填充 algorithm_configs 时出错: {e}")