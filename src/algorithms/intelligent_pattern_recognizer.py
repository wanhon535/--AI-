# algorithms/intelligent_pattern_recognizer.py
from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
import numpy as np
from collections import defaultdict, deque

from src.model.lottery_models import LotteryHistory


class IntelligentPatternRecognizer(BaseAlgorithm):
    """智能模式识别 - 发现深层号码规律"""

    def __init__(self):
        super().__init__("intelligent_pattern_recognizer", "2.0")
        self.pattern_library = defaultdict(list)
        self.parameters = {
            'pattern_types': ['sequential', 'interval', 'sum_trend', 'parity_shift'],
            'confidence_threshold': 0.8,
            'min_pattern_length': 3
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练模式识别模型"""
        if len(history_data) < 50:
            return False

        # 分析多种模式类型
        self._analyze_sequential_patterns(history_data)
        self._analyze_interval_patterns(history_data)
        self._analyze_sum_trends(history_data)
        self._analyze_parity_shifts(history_data)

        self.is_trained = True
        return True

    def _analyze_sequential_patterns(self, history_data: List[LotteryHistory]):
        """分析顺序模式（递增、递减、波浪）"""
        front_sequences = [sorted(rec.front_area) for rec in history_data]

        for i in range(len(front_sequences) - 3):
            current_window = front_sequences[i:i + 3]
            next_numbers = front_sequences[i + 3]

            # 检测递增/递减模式
            if self._is_ascending_pattern(current_window):
                pattern_key = "ascending_sequence"
                self.pattern_library[pattern_key].append(next_numbers)

            # 检测波浪模式
            if self._is_wave_pattern(current_window):
                pattern_key = "wave_sequence"
                self.pattern_library[pattern_key].append(next_numbers)

    def _analyze_interval_patterns(self, history_data: List[LotteryHistory]):
        """分析间距模式"""
        for rec in history_data:
            numbers = sorted(rec.front_area)
            intervals = [numbers[i + 1] - numbers[i] for i in range(len(numbers) - 1)]

            # 检测特定间距模式
            interval_pattern = tuple(sorted(intervals))
            if len(set(intervals)) <= 2:  # 间距种类少
                self.pattern_library[f"interval_{interval_pattern}"].append(numbers)

    def _is_ascending_pattern(self, sequences: List[List[int]]) -> bool:
        """判断是否为递增模式"""
        if len(sequences) < 2:
            return False

        trends = []
        for i in range(len(sequences) - 1):
            current_avg = np.mean(sequences[i])
            next_avg = np.mean(sequences[i + 1])
            trends.append(next_avg > current_avg)

        return all(trends) or not any(trends)  # 全递增或全递减

    def _is_wave_pattern(self, sequences: List[List[int]]) -> bool:
        """判断是否为波浪模式"""
        if len(sequences) < 3:
            return False

        avgs = [np.mean(seq) for seq in sequences]
        # 检查上升-下降或下降-上升模式
        return (avgs[0] < avgs[1] > avgs[2]) or (avgs[0] > avgs[1] < avgs[2])

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于模式识别进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 匹配当前数据与历史模式
        recent_data = history_data[-10:]  # 最近10期
        matched_patterns = self._match_current_patterns(recent_data)

        if matched_patterns:
            prediction = self._generate_prediction_from_patterns(matched_patterns)
            confidence = 0.85
        else:
            prediction = self._fallback_adaptive_prediction(recent_data)
            confidence = 0.6

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [{
                'front_numbers': sorted(prediction['front']),
                'back_numbers': sorted(prediction['back']),
                'confidence': confidence,
                'pattern_matched': bool(matched_patterns)
            }],
            'analysis': {
                'matched_patterns': list(matched_patterns.keys()) if matched_patterns else [],
                'pattern_library_size': len(self.pattern_library)
            }
        }