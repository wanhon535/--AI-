# src/algorithms/advanced_algorithms/backtesting_engine.py
from src.model.lottery_models import LotteryHistory
from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
import numpy as np

class BacktestingEngine:
    """简易回测引擎"""

    def __init__(self, algorithm: BaseAlgorithm):
        self.algorithm = algorithm

    def run(self, history_data: List[LotteryHistory], start_idx=50) -> Dict[str, Any]:
        rewards = []
        for i in range(start_idx, len(history_data) - 1):
            train_data = history_data[:i]
            test = history_data[i]
            self.algorithm.train(train_data)
            res = self.algorithm.predict(train_data)
            recs = res.get('recommendations', [])
            hit = any(set(test.front_area).intersection(r.get('front_numbers', [])) for r in recs)
            reward = 10 if hit else -1
            rewards.append(reward)
        return {
            'periods': len(rewards),
            'win_rate': sum(r > 0 for r in rewards) / len(rewards),
            'avg_return': np.mean(rewards)
        }

