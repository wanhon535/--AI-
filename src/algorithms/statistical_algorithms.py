from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
from src.model.lottery_models import LotteryHistory
from collections import Counter
import numpy as np

class FrequencyAnalysisAlgorithm(BaseAlgorithm):
    """频率分析算法 (V2.1 - 对齐Base V2)"""
    name = "FrequencyAnalysisScorer"
    version = "2.1"

    def __init__(self):
        super().__init__() # 对齐新的BaseAlgorithm
        self.frequency_data = {}
        self.parameters = {
            'front_area_range': (1, 35),
            'back_area_range': (1, 12),
        }

    # ... train 和 predict 方法保持不变 ...
    def train(self, history_data: List[LotteryHistory]) -> bool:
        if not history_data: return False
        front_numbers = [num for record in history_data for num in record.front_area]
        back_numbers = [num for record in history_data for num in record.back_area]
        self.frequency_data = {'front_frequency': Counter(front_numbers), 'back_frequency': Counter(back_numbers)}
        self.is_trained = True
        return True

    def _normalize_scores(self, counter: Counter, number_range: tuple) -> List[Dict[str, Any]]:
        if not counter: return [{'number': n, 'score': 0.0} for n in range(number_range[0], number_range[1] + 1)]
        max_count = max(counter.values()) if counter else 1.0
        scores = [{'number': number, 'score': round(counter.get(number, 0) / max_count, 4)} for number in range(number_range[0], number_range[1] + 1)]
        return sorted(scores, key=lambda x: x['score'], reverse=True)

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        if not self.is_trained: return {'error': '模型未训练'}
        front_scores = self._normalize_scores(self.frequency_data['front_frequency'], self.parameters['front_area_range'])
        back_scores = self._normalize_scores(self.frequency_data['back_frequency'], self.parameters['back_area_range'])
        recommendation = {'front_number_scores': front_scores, 'back_number_scores': back_scores, 'confidence': 0.85}
        return {'algorithm': self.name, 'version': self.version, 'recommendations': [recommendation], 'analysis': {'front_top_5': front_scores[:5], 'back_top_3': back_scores[:3]}}


class HotColdNumberAlgorithm(BaseAlgorithm):
    """热冷号识别算法 (V2.1 - 对齐Base V2)"""
    name = "HotColdScorer"
    version = "2.1"

    def __init__(self):
        super().__init__() # 对齐新的BaseAlgorithm
        self.analysis_data = {}
        self.parameters = {'recent_periods': 20, 'hot_weight': 0.6, 'cold_weight': 0.4}

    # ... train 和 predict 方法保持不变 ...
    def train(self, history_data: List[LotteryHistory]) -> bool:
        if not history_data: return False
        recent_data = history_data[-self.parameters['recent_periods']:]
        front_recent_counts = Counter(num for rec in recent_data for num in rec.front_area)
        back_recent_counts = Counter(num for rec in recent_data for num in rec.back_area)
        front_omission = {i: 0 for i in range(1, 36)}
        back_omission = {i: 0 for i in range(1, 13)}
        for i, record in enumerate(reversed(history_data)):
            for num in range(1, 36):
                if num not in record.front_area and front_omission[num] == i: front_omission[num] += 1
            for num in range(1, 13):
                if num not in record.back_area and back_omission[num] == i: back_omission[num] += 1
        self.analysis_data = {'front_hot': front_recent_counts, 'back_hot': back_recent_counts, 'front_cold': front_omission, 'back_cold': back_omission}
        self.is_trained = True
        return True

    def _calculate_combined_scores(self, hot_counts: Counter, cold_omissions: Dict, number_range: tuple) -> List[Dict[str, Any]]:
        if not hot_counts and not cold_omissions: return [{'number': n, 'score': 0.0} for n in range(number_range[0], number_range[1] + 1)]
        max_hot = max(hot_counts.values()) if hot_counts else 1
        hot_scores = {n: hot_counts.get(n, 0) / max_hot for n in range(number_range[0], number_range[1] + 1)}
        max_cold = max(cold_omissions.values()) if cold_omissions else 1
        cold_scores = {n: cold_omissions.get(n, 0) / max_cold for n in range(number_range[0], number_range[1] + 1)}
        combined_scores = []
        for num in range(number_range[0], number_range[1] + 1):
            final_score = (self.parameters['hot_weight'] * hot_scores[num] + self.parameters['cold_weight'] * cold_scores[num])
            combined_scores.append({'number': num, 'score': round(final_score, 4)})
        return sorted(combined_scores, key=lambda x: x['score'], reverse=True)

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        if not self.is_trained: return {'error': '模型未训练'}
        front_scores = self._calculate_combined_scores(self.analysis_data['front_hot'], self.analysis_data['front_cold'], (1, 35))
        back_scores = self._calculate_combined_scores(self.analysis_data['back_hot'], self.analysis_data['back_cold'], (1, 12))
        recommendation = {'front_number_scores': front_scores, 'back_number_scores': back_scores, 'confidence': 0.80}
        return {'algorithm': self.name, 'version': self.version, 'recommendations': [recommendation], 'analysis': {'front_top_5': front_scores[:5], 'back_top_3': back_scores[:3]}}


class OmissionValueAlgorithm(BaseAlgorithm):
    """遗漏值分析算法 (V2.1 - 对齐Base V2)"""
    name = "OmissionValueScorer"
    version = "2.1"

    def __init__(self):
        super().__init__() # 对齐新的BaseAlgorithm
        self.omission_data = {}
        self.parameters = {}

    # ... train 和 predict 方法保持不变 ...
    def train(self, history_data: List[LotteryHistory]) -> bool:
        if not history_data: return False
        front_omission = {i: 0 for i in range(1, 36)}
        back_omission = {i: 0 for i in range(1, 13)}
        last_seen_front, last_seen_back, total_periods = {}, {}, len(history_data)
        for i, record in enumerate(history_data):
            for num in record.front_area: last_seen_front[num] = i
            for num in record.back_area: last_seen_back[num] = i
        for num in range(1, 36): front_omission[num] = total_periods - 1 - last_seen_front.get(num, -1)
        for num in range(1, 13): back_omission[num] = total_periods - 1 - last_seen_back.get(num, -1)
        self.omission_data = {'front_omission': front_omission, 'back_omission': back_omission}
        self.is_trained = True
        return True

    def _normalize_omission(self, omission_dict: Dict) -> List[Dict[str, Any]]:
        if not omission_dict: return []
        max_omission = max(omission_dict.values()) if omission_dict else 1.0
        scores = [{'number': number, 'score': round(omission / max_omission, 4)} for number, omission in omission_dict.items()]
        return sorted(scores, key=lambda x: x['score'], reverse=True)

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        if not self.is_trained: return {'error': '模型未训练'}
        front_scores = self._normalize_omission(self.omission_data['front_omission'])
        back_scores = self._normalize_omission(self.omission_data['back_omission'])
        recommendation = {'front_number_scores': front_scores, 'back_number_scores': back_scores, 'confidence': 0.70}
        return {'algorithm': self.name, 'version': self.version, 'recommendations': [recommendation], 'analysis': {'front_top_5': front_scores[:5], 'back_top_3': back_scores[:3]}}