# src/engine/recommendation_engine.py (Final Architecture Version)

from typing import List, Dict, Any
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory


class RecommendationEngine:
    """
    推荐引擎 V3.0 (元算法调度器)
    职责：只管理和运行最高层级的元算法（如动态集成器）。
    """

    def __init__(self):
        """初始化引擎。"""
        self._meta_algorithm: BaseAlgorithm = None
        print("✅ Recommendation Engine V3.0 (Meta-Scheduler) initialized.")

    def set_meta_algorithm(self, meta_algorithm: BaseAlgorithm):
        """
        设置当前要执行的核心元算法。
        整个引擎一次只相信一个最高决策者。
        """
        self._meta_algorithm = meta_algorithm
        print(f"  - Meta-algorithm '{meta_algorithm.name}' has been set as the primary executor.")

    def generate_final_recommendation(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """
        【核心方法】执行元算法，并返回其最终的、唯一的输出报告。

        :param history_data: 用于训练和预测的历史数据。
        :return: 元算法的预测结果。
        """
        if not self._meta_algorithm:
            raise RuntimeError("No meta-algorithm has been set in the Recommendation Engine.")

        print(f"\n[ENGINE] Executing meta-algorithm: {self._meta_algorithm.name}...")

        try:
            # 训练并预测元算法（元算法内部会管理所有基础算法）
            self._meta_algorithm.train(history_data)
            prediction = self._meta_algorithm.predict(history_data)
            print(f"[ENGINE] ✅ Final report from '{self._meta_algorithm.name}' generated successfully.")
            # 我们将结果包装在以算法名为键的字典中，以保持与LLM Prompt的兼容性
            return {self._meta_algorithm.name: prediction}

        except Exception as e:
            print(f"[ENGINE] ❌ CRITICAL ERROR during meta-algorithm execution: {e}")
            return {self._meta_algorithm.name: {"error": str(e)}}