# test_learning_loop.py

import os
import sys
import random

# --- 1. 项目环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# --- 2. 导入所有需要的模块 ---
from src.model.lottery_models import LotteryHistory
from src.engine.performance_logger import PerformanceLogger
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.database.database_manager import DatabaseManager
from src.engine.adaptive_weight_updater import AdaptiveWeightUpdater
from src.database.crud.algorithm_performance_dao import AlgorithmPerformanceDAO
# 导入基础算法用于测试
from src.algorithms.statistical_algorithms import FrequencyAnalysisAlgorithm
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor


# --- 3. 模拟一个数据库 (关键！)**
# 我们创建一个假的 DAO 类，它把数据存在内存里，而不是真实数据库里
class MockAlgorithmPerformanceDAO:
    def __init__(self, db_manager: DatabaseManager = None, dao=None, smoothing_alpha: float = 0.6,
                 hist_window: int = 5):
        """
        :param db_manager: 传入一个已经配置好的 DatabaseManager 实例 (for production).
        :param dao: 可选。传入一个DAO实例 (for testing).
        :param smoothing_alpha: 平滑系数。
        :param hist_window: 历史窗口大小。
        """
        if dao:
            # Test mode: use the provided mock dao
            self.dao = dao
            print("[PerformanceLogger] Initialized in TEST mode with a mock DAO.")
        elif db_manager:
            # Production mode: create a real DAO using the db_manager
            self.dao = AlgorithmPerformanceDAO(db_manager)
            print("[PerformanceLogger] Initialized in PRODUCTION mode with a real DAO.")
        else:
            raise ValueError("PerformanceLogger requires either a 'db_manager' or a 'dao' instance.")

        self.updater = AdaptiveWeightUpdater(alpha=smoothing_alpha)
        self.hist_window = hist_window

    def get_average_scores_last_n_issues(self, n_issues: int = 3) -> dict:
        # 从内存中计算平均分
        latest_issues = sorted(list(set(d['issue'] for d in self.db)), reverse=True)[:n_issues]
        if not latest_issues:
            print(" MOCK_DB: No historical scores found.")
            return {}

        scores = {}
        for issue in latest_issues:
            for record in self.db:
                if record['issue'] == issue:
                    scores.setdefault(record['algorithm'], []).append(record['score'])

        avg_scores = {algo: sum(s_list) / len(s_list) for algo, s_list in scores.items()}
        print(f" MOCK_DB: Calculated average scores from last {len(latest_issues)} issues: {avg_scores}")
        return avg_scores


def run_unit_test():
    print("\n" + "=" * 60)
    print("🚀  STARTING UNIT TEST FOR THE SELF-LEARNING LOOP")
    print("=" * 60)

    # --- 1. 准备模拟环境 ---
    # 使用假的数据库DAO
    mock_dao = MockAlgorithmPerformanceDAO()

    # vvvvvvvvvvv  这是关键的修正！ vvvvvvvvvvv
    # 在创建PerformanceLogger时，直接把假的dao“注入”进去！
    # 这样它就不会再去创建真实的、需要连接数据库的DAO了。
    performance_logger = PerformanceLogger(dao=mock_dao)
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # ... (测试脚本的其余部分完全保持不变) ...

    # 准备一点历史数据
    history_data = [
        LotteryHistory(period_number=str(2025001 + i),
                       front_area=random.sample(range(1, 36), 5),
                       back_area=random.sample(range(1, 13), 2))
        for i in range(50)
    ]
    base_algorithms = [FrequencyAnalysisAlgorithm(), BayesianNumberPredictor()]

    # ==========================================================
    # --- 2. 模拟第一次预测 (冷启动) ---
    print("\n--- LOOP 1: Cold Start Prediction ---")
    weights_loop1 = mock_dao.get_average_scores_last_n_issues()
    optimizer_loop1 = DynamicEnsembleOptimizer(base_algorithms)
    optimizer_loop1.current_weights = weights_loop1
    optimizer_loop1.train(history_data)
    report_loop1 = optimizer_loop1.predict(history_data)
    print(f"\n[LOOP 1] Optimizer used weights: {optimizer_loop1.current_weights}")
    print(f"[LOOP 1] Final recommendation generated (front): {report_loop1['recommendations'][0]['front_numbers']}")

    # ==========================================================
    # --- 3. 模拟开奖，并进行学习 ---
    print("\n--- POST-LOOP 1: Learning from Results ---")
    actual_draw_loop1 = LotteryHistory(period_number="2025051", front_area=[1, 2, 3, 4, 5], back_area=[1, 2])
    mock_model_outputs_loop1 = {
        'frequency_analysis': {'recommendations': [{'front_numbers': [3, 4, 5, 6, 7]}]},
        'bayesian_number_predictor': {'recommendations': [{'front_numbers': [10, 11, 12, 13, 14]}]}
    }
    performance_logger.evaluate_and_update(
        issue="2025051",
        model_outputs=mock_model_outputs_loop1,
        actual_draw=actual_draw_loop1
    )

    # ==========================================================
    # --- 4. 模拟第二次预测 (热启动) ---
    print("\n--- LOOP 2: Hot Start Prediction (with learned weights) ---")
    weights_loop2 = mock_dao.get_average_scores_last_n_issues()
    optimizer_loop2 = DynamicEnsembleOptimizer(base_algorithms)
    optimizer_loop2.current_weights = weights_loop2
    optimizer_loop2.train(history_data)
    report_loop2 = optimizer_loop2.predict(history_data)
    print(f"\n[LOOP 2] Optimizer started with LEARNED weights: {weights_loop2}")
    print(f"[LOOP 2] Final recommendation generated (front): {report_loop2['recommendations'][0]['front_numbers']}")

    print("\n" + "=" * 60)
    print("🏁  UNIT TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_unit_test()