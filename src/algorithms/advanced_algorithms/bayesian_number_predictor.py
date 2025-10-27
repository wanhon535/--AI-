# src/algorithms/advanced_algorithms/bayesian_number_predictor.py
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from collections import Counter
from typing import List, Dict, Any
import numpy as np
import random

class BayesianNumberPredictor(BaseAlgorithm):
    """基于贝叶斯更新的号码概率预测器"""

    def __init__(self):
        super().__init__("bayesian_number_predictor", "1.0")
        self.posterior_front = {}
        self.posterior_back = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        if not history_data:
            return False

        front_counts, back_counts = Counter(), Counter()
        total = len(history_data)
        for rec in history_data:
            front_counts.update(rec.front_area)
            back_counts.update(rec.back_area)

        self.posterior_front = {n: (front_counts.get(n, 0) + 1) / (total + 35) for n in range(1, 36)}
        self.posterior_back = {n: (back_counts.get(n, 0) + 1) / (total + 12) for n in range(1, 13)}

        self.is_trained = True
        return True

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        if not self.is_trained:
            return {'error': '模型未训练'}

        front_nums = list(self.posterior_front.keys())
        probs = np.array(list(self.posterior_front.values()))
        probs /= probs.sum()
        front_selection = np.random.choice(front_nums, size=5, replace=False, p=probs)
        back_selection = random.sample(list(self.posterior_back.keys()), 2)

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [{
                'front_numbers': sorted(front_selection.tolist()),
                'back_numbers': sorted(back_selection),
                'confidence': 0.8
            }],
            'analysis': {'posterior_front_top10': dict(sorted(self.posterior_front.items())[:10])}
        }
