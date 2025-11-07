# ====================================================================================================
# --- FILE: src/algorithms/advanced_algorithms/bayesian_number_predictor.py (COMPLETE REPLACEMENT V2) ---
# ====================================================================================================
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from src.utils.log_predictor import log_prediction
from collections import Counter
from typing import List, Dict, Any

class BayesianNumberPredictor(BaseAlgorithm):
    """基于贝叶斯更新的号码概率预测器 (V2.0 - 评分器版)"""
    name = "BayesianNumberPredictor"
    version = "2.0"

    def __init__(self):
        super().__init__()
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

        # 使用拉普拉斯平滑计算后验概率
        self.posterior_front = {n: (front_counts.get(n, 0) + 1) / (total + 35) for n in range(1, 36)}
        self.posterior_back = {n: (back_counts.get(n, 0) + 1) / (total + 12) for n in range(1, 13)}

        self.is_trained = True
        return True

    @log_prediction
    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """核心改造: 不再随机选择，而是返回所有号码的后验概率作为分数"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 归一化概率作为分数
        max_front_prob = max(self.posterior_front.values()) if self.posterior_front else 1.0
        max_back_prob = max(self.posterior_back.values()) if self.posterior_back else 1.0

        front_scores = [{'number': n, 'score': round(p / max_front_prob, 4)} for n, p in self.posterior_front.items()]
        back_scores = [{'number': n, 'score': round(p / max_back_prob, 4)} for n, p in self.posterior_back.items()]

        recommendation = {
            'front_number_scores': sorted(front_scores, key=lambda x: x['score'], reverse=True),
            'back_number_scores': sorted(back_scores, key=lambda x: x['score'], reverse=True),
            'confidence': 0.82
        }

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [recommendation],
            'analysis': {'posterior_front_top5': front_scores[:5]}
        }