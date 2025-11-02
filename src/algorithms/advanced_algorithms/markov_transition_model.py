from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from collections import Counter, defaultdict
from typing import List, Dict, Any


class MarkovTransitionModel(BaseAlgorithm):
    """基于马尔可夫转移概率的号码预测 (V2.0 - 评分器版)"""
    name = "MarkovTransitionModel"
    version = "2.0"

    def __init__(self):
        super().__init__()
        self.transition_probs = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        if len(history_data) < 2:
            return False

        # 使用 defaultdict 简化计数
        counts = defaultdict(Counter)
        for i in range(len(history_data) - 1):
            prev_numbers = history_data[i].front_area
            next_numbers = history_data[i + 1].front_area
            for p_num in prev_numbers:
                counts[p_num].update(next_numbers)

        # 计算转移概率
        self.transition_probs = defaultdict(dict)
        for prev_num, next_counts in counts.items():
            total = sum(next_counts.values()) or 1
            self.transition_probs[prev_num] = {next_num: count / total for next_num, count in next_counts.items()}

        self.is_trained = True
        return True

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """核心改造: 基于上一期的号码，计算所有号码的预期转移概率作为分数"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        last_front = history_data[-1].front_area
        scores = Counter()
        for num in last_front:
            # 累加上一期每个号码到下一期所有号码的转移概率
            scores.update(self.transition_probs.get(num, {}))

        # 归一化分数
        max_score = max(scores.values()) if scores else 1.0
        front_scores = [{'number': n, 'score': round(scores.get(n, 0) / max_score, 4)} for n in range(1, 36)]

        # (后区逻辑简化，因为马尔可夫主要针对前区序列)
        back_scores = [{'number': n, 'score': 0.5} for n in range(1, 13)]

        recommendation = {
            'front_number_scores': sorted(front_scores, key=lambda x: x['score'], reverse=True),
            'back_number_scores': sorted(back_scores, key=lambda x: x['score'], reverse=True),
            'confidence': 0.78
        }

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [recommendation],
            'analysis': {'transition_top': scores.most_common(5)}
        }