# src/algorithms/advanced_algorithms/markov_transition_model.py
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from collections import Counter
from typing import List, Dict, Any

class MarkovTransitionModel(BaseAlgorithm):
    """基于马尔可夫转移概率的号码预测"""

    def __init__(self):
        super().__init__("markov_transition_model", "1.0")
        self.transition_probs = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        if not history_data:
            return False

        counts = {i: Counter() for i in range(1, 36)}
        prev = None
        for rec in history_data:
            if prev:
                for p in prev:
                    counts[p].update(rec.front_area)
            prev = rec.front_area

        self.transition_probs = {}
        for k, v in counts.items():
            total = sum(v.values()) or 1
            self.transition_probs[k] = {kk: vv / total for kk, vv in v.items()}

        self.is_trained = True
        return True

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        if not self.is_trained:
            return {'error': '模型未训练'}

        last = history_data[-1].front_area
        scores = Counter()
        for n in last:
            scores.update(self.transition_probs.get(n, {}))
        top = [n for n, _ in scores.most_common(5)]

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [{'front_numbers': sorted(top), 'back_numbers': [1, 2]}],
            'analysis': {'transition_top': scores.most_common(10)}
        }
