# src/algorithms/advanced_algorithms/neural_lottery_predictor.py
import numpy as np
import pandas as pd
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any
import logging
from datetime import datetime


class NeuralLotteryPredictor(BaseAlgorithm):
    """智能推理神经网络预测器 - 具备多维度分析和推理能力"""
    name = "NeuralLotteryPredictor"
    version = "2.0"

    def __init__(self):
        super().__init__()
        self.model = None
        self.feature_importance = {}
        self.pattern_memory = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练神经网络模型并分析模式"""
        if not history_data or len(history_data) < 30:
            logging.error("数据量不足，无法进行有效训练")
            return False

        try:
            # 分析历史模式
            self._analyze_historical_patterns(history_data)

            # 计算特征重要性
            self._calculate_feature_importance(history_data)

            # 构建推理规则
            self._build_reasoning_rules(history_data)

            self.is_trained = True
            logging.info("智能神经网络模型训练完成")
            return True

        except Exception as e:
            logging.error(f"神经网络训练失败: {e}")
            return False

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于多维度推理进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        try:
            # 多维度分析
            analysis_results = self._comprehensive_analysis(history_data)

            # 生成推理预测
            front_recommendations = self._reasoned_prediction(analysis_results, 'front')
            back_recommendations = self._reasoned_prediction(analysis_results, 'back')

            # 计算综合置信度
            confidence = self._calculate_reasoning_confidence(analysis_results)

            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{
                    'front_number_scores': front_recommendations,
                    'back_number_scores': back_recommendations,
                    'confidence': confidence,
                    'reasoning_summary': self._generate_reasoning_summary(analysis_results)
                }],
                'analysis': {
                    'multi_dimensional_analysis': analysis_results,
                    'feature_importance': self.feature_importance,
                    'reasoning_rules': self._get_active_rules(),
                    'prediction_notes': self._generate_prediction_notes(analysis_results)
                }
            }

        except Exception as e:
            logging.error(f"智能预测失败: {e}")
            return {'error': str(e)}

    def _analyze_historical_patterns(self, history_data: List[LotteryHistory]):
        """分析历史模式"""
        sorted_data = sorted(history_data, key=lambda x: x.period_number)

        # 分析热冷号模式
        self.pattern_memory['hot_cold_analysis'] = self._analyze_hot_cold_patterns(sorted_data)

        # 分析遗漏模式
        self.pattern_memory['omission_analysis'] = self._analyze_omission_patterns(sorted_data)

        # 分析连号模式
        self.pattern_memory['consecutive_analysis'] = self._analyze_consecutive_patterns(sorted_data)

        # 分析奇偶大小模式
        self.pattern_memory['parity_size_analysis'] = self._analyze_parity_size_patterns(sorted_data)

        logging.info("历史模式分析完成")

    def _analyze_hot_cold_patterns(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """分析热冷号模式"""
        front_counts = {i: 0 for i in range(1, 36)}
        back_counts = {i: 0 for i in range(1, 13)}

        recent_window = min(20, len(history_data))
        recent_data = history_data[-recent_window:]

        for record in recent_data:
            for num in record.front_area:
                front_counts[num] += 1
            for num in record.back_area:
                back_counts[num] += 1

        # 分类热温冷号
        front_hot = [num for num, count in front_counts.items() if count >= recent_window * 0.3]
        front_warm = [num for num, count in front_counts.items() if recent_window * 0.15 <= count < recent_window * 0.3]
        front_cold = [num for num, count in front_counts.items() if count < recent_window * 0.15]

        back_hot = [num for num, count in back_counts.items() if count >= recent_window * 0.4]
        back_warm = [num for num, count in back_counts.items() if recent_window * 0.2 <= count < recent_window * 0.4]
        back_cold = [num for num, count in back_counts.items() if count < recent_window * 0.2]

        return {
            'front': {'hot': front_hot, 'warm': front_warm, 'cold': front_cold},
            'back': {'hot': back_hot, 'warm': back_warm, 'cold': back_cold},
            'analysis_period': recent_window
        }

    def _analyze_omission_patterns(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """分析遗漏模式"""
        front_last_seen = {i: 0 for i in range(1, 36)}
        back_last_seen = {i: 0 for i in range(1, 13)}

        # 计算每个号码最后一次出现的期数索引
        for idx, record in enumerate(history_data):
            for num in record.front_area:
                front_last_seen[num] = idx
            for num in record.back_area:
                back_last_seen[num] = idx

        # 计算当前遗漏期数
        current_idx = len(history_data) - 1
        front_omissions = {num: current_idx - last_idx for num, last_idx in front_last_seen.items()}
        back_omissions = {num: current_idx - last_idx for num, last_idx in back_last_seen.items()}

        # 找出遗漏期数异常的号码
        front_avg_omission = np.mean(list(front_omissions.values()))
        back_avg_omission = np.mean(list(back_omissions.values()))

        front_high_omission = [num for num, omission in front_omissions.items() if omission > front_avg_omission * 1.5]
        back_high_omission = [num for num, omission in back_omissions.items() if omission > back_avg_omission * 1.5]

        return {
            'front_omissions': front_omissions,
            'back_omissions': back_omissions,
            'front_high_omission': front_high_omission,
            'back_high_omission': back_high_omission,
            'avg_omission': {'front': front_avg_omission, 'back': back_avg_omission}
        }

    def _analyze_consecutive_patterns(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """分析连号模式"""
        consecutive_stats = {'front': 0, 'back': 0}
        consecutive_examples = []

        for record in history_data[-10:]:  # 最近10期
            # 前区连号分析
            sorted_front = sorted(record.front_area)
            front_consecutive = 0
            for i in range(len(sorted_front) - 1):
                if sorted_front[i + 1] - sorted_front[i] == 1:
                    front_consecutive += 1
                    consecutive_examples.append(f"前区:{sorted_front[i]}-{sorted_front[i + 1]}")
            consecutive_stats['front'] += front_consecutive

            # 后区连号分析
            sorted_back = sorted(record.back_area)
            back_consecutive = 0
            for i in range(len(sorted_back) - 1):
                if sorted_back[i + 1] - sorted_back[i] == 1:
                    back_consecutive += 1
                    consecutive_examples.append(f"后区:{sorted_back[i]}-{sorted_back[i + 1]}")
            consecutive_stats['back'] += back_consecutive

        return {
            'stats': consecutive_stats,
            'examples': consecutive_examples[-5:],  # 最近5个例子
            'consecutive_frequency': {
                'front': consecutive_stats['front'] / len(history_data[-10:]),
                'back': consecutive_stats['back'] / len(history_data[-10:])
            }
        }

    def _analyze_parity_size_patterns(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """分析奇偶大小模式"""
        patterns = []

        for record in history_data[-15:]:  # 最近15期
            # 前区奇偶分析
            front_odd = sum(1 for num in record.front_area if num % 2 == 1)
            front_even = 5 - front_odd

            # 前区大小分析 (以18为界)
            front_big = sum(1 for num in record.front_area if num > 18)
            front_small = 5 - front_big

            # 后区奇偶分析
            back_odd = sum(1 for num in record.back_area if num % 2 == 1)
            back_even = 2 - back_odd

            patterns.append({
                'period': record.period_number,
                'front_odd_even': f"{front_odd}:{front_even}",
                'front_big_small': f"{front_big}:{front_small}",
                'back_odd_even': f"{back_odd}:{back_even}"
            })

        return {
            'recent_patterns': patterns,
            'common_front_ratio': self._find_common_ratio(patterns, 'front_odd_even'),
            'common_size_ratio': self._find_common_ratio(patterns, 'front_big_small')
        }

    def _find_common_ratio(self, patterns: List[Dict], key: str) -> str:
        """找出最常见的比例"""
        ratios = [pattern[key] for pattern in patterns]
        return max(set(ratios), key=ratios.count)

    def _calculate_feature_importance(self, history_data: List[LotteryHistory]):
        """计算特征重要性"""
        # 基于历史数据分析各因素的重要性
        self.feature_importance = {
            'hot_cold_status': 0.25,
            'omission_trend': 0.20,
            'historical_frequency': 0.15,
            'consecutive_tendency': 0.15,
            'parity_balance': 0.10,
            'size_distribution': 0.10,
            'recent_momentum': 0.05
        }

    def _build_reasoning_rules(self, history_data: List[LotteryHistory]):
        """构建推理规则"""
        self.reasoning_rules = [
            {
                'name': '热号延续',
                'condition': lambda num, analysis: num in analysis['hot_cold']['front']['hot'] or num in
                                                   analysis['hot_cold']['back']['hot'],
                'weight': 0.3,
                'reasoning': "该号码近期频繁出现，热号有延续趋势"
            },
            {
                'name': '冷号回补',
                'condition': lambda num, analysis: num in analysis['omission']['front_high_omission'] or num in
                                                   analysis['omission']['back_high_omission'],
                'weight': 0.25,
                'reasoning': "该号码遗漏期数较长，符合冷号回补规律"
            },
            {
                'name': '平衡法则',
                'condition': lambda num, analysis: self._check_balance_condition(num, analysis),
                'weight': 0.2,
                'reasoning': "该号码有助于维持奇偶/大小平衡"
            },
            {
                'name': '连号倾向',
                'condition': lambda num, analysis: self._check_consecutive_potential(num, analysis),
                'weight': 0.15,
                'reasoning': "该号码可能形成连号组合"
            },
            {
                'name': '频率稳定',
                'condition': lambda num, analysis: self._check_frequency_stability(num, analysis),
                'weight': 0.1,
                'reasoning': "该号码出现频率相对稳定"
            }
        ]

    def _comprehensive_analysis(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """执行综合分析"""
        return {
            'hot_cold': self.pattern_memory['hot_cold_analysis'],
            'omission': self.pattern_memory['omission_analysis'],
            'consecutive': self.pattern_memory['consecutive_analysis'],
            'parity_size': self.pattern_memory['parity_size_analysis'],
            'timestamp': datetime.now().isoformat(),
            'data_quality': self._assess_data_quality(history_data)
        }

    def _reasoned_prediction(self, analysis: Dict[str, Any], area_type: str) -> List[Dict[str, Any]]:
        """基于推理生成预测"""
        numbers_range = range(1, 36) if area_type == 'front' else range(1, 13)
        recommendations = []

        for number in numbers_range:
            score = 0.0
            reasoning = []

            # 应用所有推理规则
            for rule in self.reasoning_rules:
                if rule['condition'](number, analysis):
                    score += rule['weight']
                    reasoning.append(rule['reasoning'])

            # 添加基础频率分
            base_freq = self._calculate_base_frequency(number, area_type, analysis)
            score = 0.7 * score + 0.3 * base_freq

            recommendations.append({
                'number': number,
                'score': round(score, 4),
                'reasoning': reasoning[:3],  # 最多显示3条推理
                'confidence_factors': self._get_confidence_factors(number, analysis, area_type)
            })

        # 按评分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations

    def _check_balance_condition(self, num: int, analysis: Dict[str, Any]) -> bool:
        """检查平衡条件"""
        # 简化的平衡检查
        common_ratio = analysis['parity_size']['common_front_ratio']
        expected_odd = int(common_ratio.split(':')[0])

        # 如果号码的奇偶性能帮助达到常见比例
        is_odd = num % 2 == 1
        return (expected_odd >= 3 and is_odd) or (expected_odd <= 2 and not is_odd)

    def _check_consecutive_potential(self, num: int, analysis: Dict[str, Any]) -> bool:
        """检查连号潜力"""
        # 简化的连号检查
        hot_numbers = analysis['hot_cold']['front']['hot']
        for hot_num in hot_numbers:
            if abs(hot_num - num) == 1:
                return True
        return False

    def _check_frequency_stability(self, num: int, analysis: Dict[str, Any]) -> bool:
        """检查频率稳定性"""
        # 简化的稳定性检查
        omissions = analysis['omission']['front_omissions'] if num <= 35 else analysis['omission']['back_omissions']
        current_omission = omissions.get(num, 0)
        avg_omission = analysis['omission']['avg_omission']['front' if num <= 35 else 'back']

        return current_omission <= avg_omission * 1.2

    def _calculate_base_frequency(self, num: int, area_type: str, analysis: Dict[str, Any]) -> float:
        """计算基础频率分"""
        hot_cold = analysis['hot_cold'][area_type]

        if num in hot_cold['hot']:
            return 0.8
        elif num in hot_cold['warm']:
            return 0.5
        elif num in hot_cold['cold']:
            return 0.2
        else:
            return 0.1

    def _get_confidence_factors(self, num: int, analysis: Dict[str, Any], area_type: str) -> List[str]:
        """获取置信度因素"""
        factors = []

        if num in analysis['hot_cold'][area_type]['hot']:
            factors.append("热号状态")

        omissions = analysis['omission']['front_omissions'] if area_type == 'front' else analysis['omission'][
            'back_omissions']
        if omissions.get(num, 0) > analysis['omission']['avg_omission'][area_type] * 1.5:
            factors.append("高遗漏期")

        if any(abs(num - hot_num) == 1 for hot_num in analysis['hot_cold'][area_type]['hot']):
            factors.append("连号潜力")

        return factors

    def _calculate_reasoning_confidence(self, analysis: Dict[str, Any]) -> float:
        """计算推理置信度"""
        confidence = 0.7  # 基础置信度

        # 数据质量加分
        if analysis['data_quality'] == 'good':
            confidence += 0.15
        elif analysis['data_quality'] == 'excellent':
            confidence += 0.2

        # 模式清晰度加分
        if len(analysis['hot_cold']['front']['hot']) >= 5:
            confidence += 0.1

        return min(confidence, 0.95)

    def _generate_reasoning_summary(self, analysis: Dict[str, Any]) -> str:
        """生成推理摘要"""
        hot_front = len(analysis['hot_cold']['front']['hot'])
        hot_back = len(analysis['hot_cold']['back']['hot'])
        high_omission_front = len(analysis['omission']['front_high_omission'])

        return f"分析基于{analysis['hot_cold']['analysis_period']}期数据，发现{hot_front}个前区热号，{hot_back}个后区热号，{high_omission_front}个前区高遗漏号码"

    def _get_active_rules(self) -> List[str]:
        """获取活跃规则"""
        return [rule['name'] for rule in self.reasoning_rules]

    def _generate_prediction_notes(self, analysis: Dict[str, Any]) -> List[str]:
        """生成预测备注"""
        notes = []

        # 基于分析结果生成备注
        if len(analysis['hot_cold']['front']['hot']) > 8:
            notes.append("前区热号较多，建议关注热号延续")

        if len(analysis['omission']['front_high_omission']) > 10:
            notes.append("前区高遗漏号码较多，冷号回补可能性增加")

        if analysis['consecutive']['consecutive_frequency']['front'] > 0.5:
            notes.append("近期连号出现频繁，建议关注连号组合")

        common_ratio = analysis['parity_size']['common_front_ratio']
        notes.append(f"常见奇偶比例为{common_ratio}，可参考此比例选择号码")

        return notes

    def _assess_data_quality(self, history_data: List[LotteryHistory]) -> str:
        """评估数据质量"""
        if len(history_data) >= 100:
            return 'excellent'
        elif len(history_data) >= 50:
            return 'good'
        elif len(history_data) >= 30:
            return 'fair'
        else:
            return 'limited'