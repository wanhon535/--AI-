# algorithms/statistical_algorithms.py
from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
from src.model.lottery_models import LotteryHistory
from collections import Counter
import random

class FrequencyAnalysisAlgorithm(BaseAlgorithm):
    """频率分析算法"""

    def __init__(self):
        super().__init__("frequency_analysis", "1.0")
        self.frequency_data = {}
        self.parameters = {
            'front_area_range': (1, 35),
            'back_area_range': (1, 12),
            'top_n': 10
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练频率分析模型"""
        if not history_data:
            return False

        # 统计前区和后区号码频率
        front_numbers = []
        back_numbers = []

        for record in history_data:
            front_numbers.extend(record.front_area)
            back_numbers.extend(record.back_area)

        self.frequency_data = {
            'front_frequency': Counter(front_numbers),
            'back_frequency': Counter(back_numbers)
        }

        self.is_trained = True
        return True

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于频率进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 获取高频号码
        front_freq = self.frequency_data['front_frequency']
        back_freq = self.frequency_data['back_frequency']

        # 选择前N个高频号码
        top_n = self.parameters.get('top_n', 10)
        front_candidates = [num for num, _ in front_freq.most_common(top_n)]
        back_candidates = [num for num, _ in back_freq.most_common(min(top_n, 6))]

        # 生成推荐组合
        recommendations = []
        for _ in range(5):  # 生成5组推荐
            front_selection = random.sample(front_candidates, min(5, len(front_candidates)))
            back_selection = random.sample(back_candidates, min(2, len(back_candidates)))
            recommendations.append({
                'front_numbers': sorted(front_selection),
                'back_numbers': sorted(back_selection),
                'confidence': 0.75  # 基于频率分析的置信度
            })

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': recommendations,
            'analysis': {
                'front_frequency_top': dict(front_freq.most_common(10)),
                'back_frequency_top': dict(back_freq.most_common(6))
            }
        }

class HotColdNumberAlgorithm(BaseAlgorithm):
    """热冷号识别算法"""

    def __init__(self):
        super().__init__("hot_cold_number", "1.0")
        self.hot_numbers = {}
        self.cold_numbers = {}
        self.parameters = {
            'hot_threshold': 10,  # 热号阈值（最近N期出现次数）
            'cold_threshold': 20  # 冷号阈值（连续未出现期数）
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练热冷号识别模型"""
        if not history_data:
            return False

        # 分析热号（最近出现频率高的号码）
        recent_periods = min(20, len(history_data))  # 分析最近20期
        recent_data = history_data[-recent_periods:]

        front_numbers = []
        back_numbers = []
        for record in recent_data:
            front_numbers.extend(record.front_area)
            back_numbers.extend(record.back_area)

        front_counter = Counter(front_numbers)
        back_counter = Counter(back_numbers)

        hot_threshold = self.parameters.get('hot_threshold', 10)
        self.hot_numbers = {
            'front': [num for num, count in front_counter.items() if count >= hot_threshold],
            'back': [num for num, count in back_counter.items() if count >= hot_threshold//2]
        }

        # 分析冷号（长时间未出现的号码）
        all_front_numbers = set(range(1, 36))
        all_back_numbers = set(range(1, 13))

        # 找出最近出现过的号码
        appeared_front = set(front_numbers)
        appeared_back = set(back_numbers)

        # 冷号为未在近期出现的号码
        self.cold_numbers = {
            'front': list(all_front_numbers - appeared_front),
            'back': list(all_back_numbers - appeared_back)
        }

        self.is_trained = True
        return True

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于热冷号进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        recommendations = []
        for _ in range(5):
            # 组合热号和冷号
            front_hot = random.sample(self.hot_numbers['front'], min(3, len(self.hot_numbers['front'])))
            front_cold = random.sample(self.cold_numbers['front'], min(2, len(self.cold_numbers['front'])))
            front_selection = sorted(front_hot + front_cold)

            back_hot = random.sample(self.hot_numbers['back'], min(1, len(self.hot_numbers['back'])))
            back_cold = random.sample(self.cold_numbers['back'], min(1, len(self.cold_numbers['back'])))
            back_selection = sorted(back_hot + back_cold)

            recommendations.append({
                'front_numbers': front_selection,
                'back_numbers': back_selection,
                'confidence': 0.70
            })

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': recommendations,
            'analysis': {
                'hot_numbers': self.hot_numbers,
                'cold_numbers': self.cold_numbers
            }
        }

class OmissionValueAlgorithm(BaseAlgorithm):
    """遗漏值计算算法"""

    def __init__(self):
        super().__init__("omission_value", "1.0")
        self.omission_data = {}
        self.parameters = {
            'high_omission_threshold': 15  # 高遗漏阈值
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练遗漏值计算模型"""
        if not history_data:
            return False

        # 计算每个号码的遗漏值
        front_omission = {i: 0 for i in range(1, 36)}
        back_omission = {i: 0 for i in range(1, 13)}

        # 从最新一期开始计算遗漏
        for record in reversed(history_data):
            # 出现的号码遗漏值重置为0
            for num in record.front_area:
                front_omission[num] = 0
            for num in record.back_area:
                back_omission[num] = 0

            # 未出现的号码遗漏值+1
            for num in front_omission:
                if num not in record.front_area:
                    front_omission[num] += 1
            for num in back_omission:
                if num not in record.back_area:
                    back_omission[num] += 1

        self.omission_data = {
            'front_omission': front_omission,
            'back_omission': back_omission
        }

        self.is_trained = True
        return True

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于遗漏值进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        high_threshold = self.parameters.get('high_omission_threshold', 15)

        # 选择高遗漏号码（可能即将出现）
        front_high_omission = [num for num, omission in self.omission_data['front_omission'].items()
                              if omission >= high_threshold]
        back_high_omission = [num for num, omission in self.omission_data['back_omission'].items()
                             if omission >= high_threshold//2]

        recommendations = []
        for _ in range(5):
            front_selection = random.sample(front_high_omission, min(5, len(front_high_omission)))
            back_selection = random.sample(back_high_omission, min(2, len(back_high_omission)))
            recommendations.append({
                'front_numbers': sorted(front_selection),
                'back_numbers': sorted(back_selection),
                'confidence': 0.65
            })

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': recommendations,
            'analysis': {
                'front_omission': self.omission_data['front_omission'],
                'back_omission': self.omission_data['back_omission']
            }
        }
