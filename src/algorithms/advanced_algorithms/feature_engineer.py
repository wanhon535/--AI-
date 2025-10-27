# src/algorithms/advanced_algorithms/feature_engineer.py
from typing import List, Tuple
import numpy as np
import pandas as pd
from collections import Counter
from src.model.lottery_models import LotteryHistory

class FeatureEngineer:
    """
    将历史开奖转换为机器学习/深度学习可用的特征。
    特征示例：和值、奇偶比、跨度、号码频率、连号次数等。
    """

    @staticmethod
    def build_features(history_data: List[LotteryHistory], lookback: int = 20) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if len(history_data) < lookback + 1:
            return pd.DataFrame(), pd.DataFrame()

        rows, targets = [], []
        history_sorted = sorted(history_data, key=lambda r: r.date)

        for i in range(lookback, len(history_sorted) - 1):
            window = history_sorted[i - lookback:i]
            next_rec = history_sorted[i + 1]

            front_counts = Counter()
            back_counts = Counter()
            sums, odd_ratios = [], []

            for w in window:
                front_counts.update(w.front_area)
                back_counts.update(w.back_area)
                total = sum(w.front_area + w.back_area)
                sums.append(total)
                odd = sum(1 for n in w.front_area + w.back_area if n % 2 == 1)
                even = len(w.front_area) + len(w.back_area) - odd
                odd_ratios.append(odd / (even + 1e-6))

            features = {
                'mean_sum': np.mean(sums),
                'std_sum': np.std(sums),
                'mean_odd_ratio': np.mean(odd_ratios),
                'front_unique': len(front_counts),
                'back_unique': len(back_counts)
            }

            for num in range(1, 36):
                features[f'front_freq_{num}'] = front_counts.get(num, 0)
            for num in range(1, 13):
                features[f'back_freq_{num}'] = back_counts.get(num, 0)

            target_sum = sum(next_rec.front_area) + sum(next_rec.back_area)
            rows.append(features)
            targets.append({'target_sum': target_sum})

        return pd.DataFrame(rows), pd.DataFrame(targets)
