# src/engine/recommendation_engine.py (Final Architecture Version)
import json
from datetime import datetime
from typing import List, Dict, Any
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory


class RecommendationEngine:
    """
    推荐引擎 V3.0 (元算法调度器)
    职责：只管理和运行最高层级的元算法（如动态集成器）。
    """

    def store_algorithm_predictions(self, algorithm_name: str, predictions: Dict, period_number: str):
        """存储单个算法的预测结果到数据库"""
        try:
            # 获取数据库连接
            db_manager = self.db_manager  # 需要在 __init__ 中初始化 db_manager

            # 构建算法预测记录
            algorithm_data = {
                'algorithm_name': algorithm_name,
                'period_number': period_number,
                'predictions': json.dumps(predictions, ensure_ascii=False),
                'confidence_score': predictions.get('confidence', 0.5),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 插入到算法预测表（需要先在数据库中创建这个表）
            db_manager.insert_algorithm_predictions(algorithm_data)

        except Exception as e:
            print(f"存储算法 {algorithm_name} 预测结果失败: {e}")


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

    def generate_final_recommendation(self, history_data: List[LotteryHistory],
                                      individual_predictions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        【核心方法】执行元算法，并返回其最终的、唯一的输出报告。
        (V3.1 - 增加了对预计算结果的支持)

        :param history_data: 用于训练和预测的历史数据。
        :param individual_predictions: (可选) 已经计算好的基础算法预测结果。
        :return: 元算法的预测结果。
        """
        if not self._meta_algorithm:
            raise RuntimeError("No meta-algorithm has been set in the Recommendation Engine.")

        print(f"\n[ENGINE] Executing meta-algorithm: {self._meta_algorithm.name}...")

        try:
            # 如果没有提供预计算的结果，元算法会自己去跑
            # 如果提供了，我们需要一种方式把它传递给元算法
            # 这里我们假设元算法（DynamicEnsembleOptimizer）有一个方法可以接收它们

            self._meta_algorithm.train(history_data)

            # --- 核心修改 ---
            # 检查元算法是否可以直接使用预计算的结果
            if individual_predictions and hasattr(self._meta_algorithm, 'predict_with_individuals'):
                prediction = self._meta_algorithm.predict_with_individuals(history_data, individual_predictions)
            else:
                # 否则，执行标准的预测流程
                prediction = self._meta_algorithm.predict(history_data)
            # -----------------

            print(f"[ENGINE] ✅ Final report from '{self._meta_algorithm.name}' generated successfully.")
            return {self._meta_algorithm.name: prediction}

        except Exception as e:
            print(f"[ENGINE] ❌ CRITICAL ERROR during meta-algorithm execution: {e}")
            import traceback
            traceback.print_exc()  # 打印详细的错误堆栈
            return {self._meta_algorithm.name: {"error": str(e)}}