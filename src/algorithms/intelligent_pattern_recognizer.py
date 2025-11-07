# src/algorithms/advanced_algorithms/intelligent_pattern_recognizer.py
import numpy as np
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any
import logging
from collections import Counter
import pandas as pd

from src.utils.log_predictor import log_prediction


class IntelligentPatternRecognizer(BaseAlgorithm):
    """智能模式识别器 - 识别历史数据中的复杂模式"""
    name = "IntelligentPatternRecognizer"
    version = "1.0"

    def __init__(self):
        super().__init__()
        self.patterns = {}
        self.pattern_confidence = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练模式识别模型"""
        if not history_data or len(history_data) < 30:
            logging.error("数据量不足，无法进行模式识别")
            return False

        try:
            # 识别多种模式
            self._identify_frequency_patterns(history_data)
            self._identify_sequential_patterns(history_data)
            self._identify_structural_patterns(history_data)
            self._identify_temporal_patterns(history_data)

            # 计算模式置信度
            self._calculate_pattern_confidence(history_data)

            self.is_trained = True
            logging.info("智能模式识别器训练完成")
            return True

        except Exception as e:
            logging.error(f"模式识别器训练失败: {e}")
            return False

    @log_prediction
    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于模式识别进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        try:
            # 基于多种模式生成预测
            front_recommendations = self._pattern_based_prediction('front')
            back_recommendations = self._pattern_based_prediction('back')

            # 计算综合置信度
            confidence = self._calculate_overall_confidence()

            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{
                    'front_number_scores': front_recommendations,
                    'back_number_scores': back_recommendations,
                    'confidence': confidence,
                    'active_patterns': list(self.patterns.keys())
                }],
                'analysis': {
                    'pattern_analysis': self._get_pattern_analysis(),
                    'pattern_confidence': self.pattern_confidence,
                    'pattern_details': self._get_pattern_details()
                }
            }

        except Exception as e:
            logging.error(f"模式识别预测失败: {e}")
            return {'error': str(e)}

    def _identify_frequency_patterns(self, history_data: List[LotteryHistory]):
        """识别频率相关模式"""
        # 热冷号模式
        front_freq = Counter()
        back_freq = Counter()

        for record in history_data:
            for num in record.front_area:
                front_freq[num] += 1
            for num in record.back_area:
                back_freq[num] += 1

        # 热号、温号、冷号分类
        total_periods = len(history_data)
        front_hot = [num for num, count in front_freq.items() if count / total_periods > 0.25]
        front_cold = [num for num, count in front_freq.items() if count / total_periods < 0.1]

        back_hot = [num for num, count in back_freq.items() if count / total_periods > 0.3]
        back_cold = [num for num, count in back_freq.items() if count / total_periods < 0.15]

        self.patterns['frequency_hot_cold'] = {
            'front_hot': front_hot,
            'front_cold': front_cold,
            'back_hot': back_hot,
            'back_cold': back_cold,
            'description': f"热冷号模式: 前区{len(front_hot)}热/{len(front_cold)}冷, 后区{len(back_hot)}热/{len(back_cold)}冷"
        }

    def _identify_sequential_patterns(self, history_data: List[LotteryHistory]):
        """识别序列模式"""
        sorted_data = sorted(history_data, key=lambda x: x.period_number)

        # 遗漏模式
        front_last_seen = {i: 0 for i in range(1, 36)}
        back_last_seen = {i: 0 for i in range(1, 13)}

        omission_patterns = []
        for idx, record in enumerate(sorted_data):
            # 更新遗漏信息
            current_omissions = {}
            for num in range(1, 36):
                current_omissions[num] = idx - front_last_seen[num]
            for num in record.front_area:
                front_last_seen[num] = idx

            omission_patterns.append(current_omissions)

        # 分析遗漏趋势
        high_omission_numbers = []
        avg_omission = np.mean([omission for pattern in omission_patterns[-10:] for omission in pattern.values()])

        for num in range(1, 36):
            recent_omissions = [pattern[num] for pattern in omission_patterns[-5:]]
            if np.mean(recent_omissions) > avg_omission * 1.5:
                high_omission_numbers.append(num)

        self.patterns['sequential_omission'] = {
            'high_omission_numbers': high_omission_numbers,
            'avg_omission': avg_omission,
            'description': f"高遗漏号码模式: {len(high_omission_numbers)}个号码遗漏期数超过平均1.5倍"
        }

    def _identify_structural_patterns(self, history_data: List[LotteryHistory]):
        """识别结构模式"""
        # 奇偶模式
        parity_patterns = []
        size_patterns = []  # 大小模式 (以18为界)
        sum_patterns = []

        for record in history_data:
            # 奇偶比例
            odd_count = sum(1 for num in record.front_area if num % 2 == 1)
            parity_patterns.append(f"{odd_count}:{5 - odd_count}")

            # 大小比例
            big_count = sum(1 for num in record.front_area if num > 18)
            size_patterns.append(f"{big_count}:{5 - big_count}")

            # 和值
            sum_patterns.append(sum(record.front_area))

        # 最常见模式
        common_parity = Counter(parity_patterns).most_common(1)[0][0]
        common_size = Counter(size_patterns).most_common(1)[0][0]
        avg_sum = np.mean(sum_patterns)

        self.patterns['structural_balance'] = {
            'common_parity': common_parity,
            'common_size': common_size,
            'avg_sum': avg_sum,
            'description': f"结构平衡模式: 奇偶{common_parity}, 大小{common_size}, 平均和值{avg_sum:.1f}"
        }

    def _identify_temporal_patterns(self, history_data: List[LotteryHistory]):
        """识别时间模式"""
        sorted_data = sorted(history_data, key=lambda x: x.period_number)

        # 周期性分析
        period_intervals = {}
        for area in ['front', 'back']:
            numbers_range = range(1, 36) if area == 'front' else range(1, 13)
            for num in numbers_range:
                appearances = []
                for idx, record in enumerate(sorted_data):
                    numbers = record.front_area if area == 'front' else record.back_area
                    if num in numbers:
                        appearances.append(idx)

                if len(appearances) > 1:
                    intervals = [appearances[i] - appearances[i - 1] for i in range(1, len(appearances))]
                    avg_interval = np.mean(intervals)
                    period_intervals[f"{area}_{num}"] = avg_interval

        # 找出周期性强的号码
        periodic_numbers = []
        avg_interval = np.mean(list(period_intervals.values())) if period_intervals else 10

        for key, interval in period_intervals.items():
            if abs(interval - avg_interval) / avg_interval < 0.3:  # 间隔接近平均值
                area, num = key.split('_')
                periodic_numbers.append((area, int(num)))

        self.patterns['temporal_periodic'] = {
            'periodic_numbers': periodic_numbers,
            'avg_interval': avg_interval,
            'description': f"时间周期模式: {len(periodic_numbers)}个号码出现周期稳定"
        }

    def _calculate_pattern_confidence(self, history_data: List[LotteryHistory]):
        """计算模式置信度"""
        # 基于模式清晰度和数据量计算置信度
        total_periods = len(history_data)

        # 频率模式置信度
        freq_pattern = self.patterns['frequency_hot_cold']
        hot_ratio = len(freq_pattern['front_hot']) / 35
        self.pattern_confidence['frequency'] = min(0.8, hot_ratio * 2)

        # 序列模式置信度
        seq_pattern = self.patterns['sequential_omission']
        if len(seq_pattern['high_omission_numbers']) > 0:
            self.pattern_confidence['sequential'] = 0.7
        else:
            self.pattern_confidence['sequential'] = 0.5

        # 结构模式置信度
        struct_pattern = self.patterns['structural_balance']
        parity_counter = Counter()
        for record in history_data:
            odd_count = sum(1 for num in record.front_area if num % 2 == 1)
            parity_counter[f"{odd_count}:{5 - odd_count}"] += 1

        most_common_ratio = parity_counter.most_common(1)[0][1] / total_periods
        self.pattern_confidence['structural'] = most_common_ratio

        # 时间模式置信度
        temp_pattern = self.patterns['temporal_periodic']
        if len(temp_pattern['periodic_numbers']) > 5:
            self.pattern_confidence['temporal'] = 0.7
        else:
            self.pattern_confidence['temporal'] = 0.4

    def _pattern_based_prediction(self, area_type: str) -> List[Dict[str, Any]]:
        """基于多种模式生成预测"""
        numbers_range = range(1, 36) if area_type == 'front' else range(1, 13)
        recommendations = []

        for number in numbers_range:
            score = 0.0
            pattern_matches = []

            # 频率模式匹配
            freq_pattern = self.patterns['frequency_hot_cold']
            if area_type == 'front':
                if number in freq_pattern['front_hot']:
                    score += 0.3 * self.pattern_confidence['frequency']
                    pattern_matches.append("热号模式")
                elif number in freq_pattern['front_cold']:
                    score += 0.1 * self.pattern_confidence['frequency']
                    pattern_matches.append("冷号模式")
            else:
                if number in freq_pattern['back_hot']:
                    score += 0.3 * self.pattern_confidence['frequency']
                    pattern_matches.append("热号模式")
                elif number in freq_pattern['back_cold']:
                    score += 0.1 * self.pattern_confidence['frequency']
                    pattern_matches.append("冷号模式")

            # 序列模式匹配
            seq_pattern = self.patterns['sequential_omission']
            if number in seq_pattern['high_omission_numbers']:
                score += 0.25 * self.pattern_confidence['sequential']
                pattern_matches.append("高遗漏模式")

            # 结构模式匹配
            struct_pattern = self.patterns['structural_balance']
            common_parity = struct_pattern['common_parity']
            expected_odd = int(common_parity.split(':')[0])

            is_odd = number % 2 == 1
            if (expected_odd >= 3 and is_odd) or (expected_odd <= 2 and not is_odd):
                score += 0.2 * self.pattern_confidence['structural']
                pattern_matches.append("奇偶平衡模式")

            # 时间模式匹配
            temp_pattern = self.patterns['temporal_periodic']
            for area, num in temp_pattern['periodic_numbers']:
                if area == area_type and num == number:
                    score += 0.25 * self.pattern_confidence['temporal']
                    pattern_matches.append("周期稳定模式")
                    break

            # 基础分
            score += 0.1

            recommendations.append({
                'number': number,
                'score': round(min(score, 1.0), 4),
                'pattern_matches': pattern_matches
            })

        # 按评分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations

    def _calculate_overall_confidence(self) -> float:
        """计算综合置信度"""
        if not self.pattern_confidence:
            return 0.5

        # 加权平均
        weights = {
            'frequency': 0.3,
            'sequential': 0.25,
            'structural': 0.25,
            'temporal': 0.2
        }

        total_confidence = 0.0
        for pattern, weight in weights.items():
            if pattern in self.pattern_confidence:
                total_confidence += self.pattern_confidence[pattern] * weight

        return round(total_confidence, 4)

    def _get_pattern_analysis(self) -> Dict[str, Any]:
        """获取模式分析信息"""
        return {
            'pattern_count': len(self.patterns),
            'strongest_pattern_confidence': max(self.pattern_confidence.values()) if self.pattern_confidence else 0,
            'identified_patterns': [
                {'name': name, 'description': pattern['description']}
                for name, pattern in self.patterns.items()
            ]
        }

    def _get_pattern_details(self) -> Dict[str, Any]:
        """获取模式详情"""
        details = {}
        for name, pattern in self.patterns.items():
            details[name] = {
                'description': pattern['description'],
                'confidence': self.pattern_confidence.get(name.replace('_pattern', ''), 0)
            }
        return details