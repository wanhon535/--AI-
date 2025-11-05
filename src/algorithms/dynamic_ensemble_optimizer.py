from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
from collections import defaultdict
import numpy as np
from src.model.lottery_models import LotteryHistory


class DynamicEnsembleOptimizer(BaseAlgorithm):
    """动态权重集成优化器 (V3.1 - 对齐Base V2)"""
    name = "DynamicEnsembleOptimizer"
    version = "3.1"

    def __init__(self, base_algorithms: List[BaseAlgorithm] = None):
        super().__init__()  # 对齐新的BaseAlgorithm
        self.base_algorithms = base_algorithms if base_algorithms else []
        self.current_weights = {}
        self.parameters = {
            'evaluation_window': 30,
            'weight_decay_factor': 0.98,
            'min_weight': 0.05
        }

    def calculate_dynamic_weights(self, algorithm_performance):
        """基于算法性能动态计算权重"""
        weights = {}
        total_performance = sum(algorithm_performance.values())

        for algo_name, performance in algorithm_performance.items():
            # 基础权重 + 性能加成
            base_weight = 1.0 / len(algorithm_performance)
            performance_bonus = performance / total_performance
            weights[algo_name] = base_weight * 0.3 + performance_bonus * 0.7

        return weights

    # ... train 和 predict 方法保持不变 ...
    def train(self, history_data: List[LotteryHistory]) -> bool:
        if not self.base_algorithms or len(history_data) < 50:
            print("  - [Optimizer] 警告: 无法训练权重，将使用默认等权重。")
            if self.base_algorithms: self.current_weights = {algo.name: 1.0 / len(self.base_algorithms) for algo in
                                                             self.base_algorithms}
            self.is_trained = True
            return True
        print(f"  - [Optimizer] 开始训练权重，评估 {len(self.base_algorithms)} 个算法...")
        self.current_weights = {algorithm.name: 1.0 / len(self.base_algorithms) for algorithm in self.base_algorithms}
        print(f"  - [Optimizer] 权重训练完成（当前为等权重）: {self.current_weights}")
        self.is_trained = True
        return True

    def predict(self, individual_predictions: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_trained:
            algo_names = list(individual_predictions.keys())
            if not algo_names: return {'error': '没有收到任何基础算法的预测结果'}
            self.current_weights = {name: 1.0 / len(algo_names) for name in algo_names}
            print(f"  - [Optimizer] 警告: 模型未训练，使用临时等权重: {self.current_weights}")

        front_master_scores = defaultdict(float)
        back_master_scores = defaultdict(float)
        algorithms_used = []
        for algo_name, result in individual_predictions.items():
            if not result or 'recommendations' not in result or not result['recommendations']: continue
            weight = self.current_weights.get(algo_name, 0.01)
            rec = result['recommendations'][0]
            if 'front_number_scores' not in rec or 'back_number_scores' not in rec: continue
            algorithms_used.append(algo_name)
            for item in rec['front_number_scores']: front_master_scores[item['number']] += item['score'] * weight
            for item in rec['back_number_scores']: back_master_scores[item['number']] += item['score'] * weight

        max_front_score = max(front_master_scores.values()) if front_master_scores else 1.0
        max_back_score = max(back_master_scores.values()) if back_master_scores else 1.0
        fused_front_scores = sorted(
            [{'number': num, 'score': round(score / max_front_score, 4)} for num, score in front_master_scores.items()],
            key=lambda x: x['score'], reverse=True)
        fused_back_scores = sorted(
            [{'number': num, 'score': round(score / max_back_score, 4)} for num, score in back_master_scores.items()],
            key=lambda x: x['score'], reverse=True)

        fused_recommendation = {"fused_front_scores": fused_front_scores, "fused_back_scores": fused_back_scores,
                                "confidence": np.mean([res['recommendations'][0].get('confidence', 0.7) for res in
                                                       individual_predictions.values() if
                                                       res and res['recommendations']])}
        return {'algorithm': self.name, 'version': self.version, 'recommendations': [fused_recommendation],
                'analysis': {'weights_used': self.current_weights, 'algorithms_fused': algorithms_used,
                             'ensemble_method': 'weighted_score_fusion'}}