# algorithms/real_time_feedback_learner.py
from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta

from src.model.lottery_models import LotteryHistory


class RealTimeFeedbackLearner(BaseAlgorithm):
    """实时反馈学习器 - 根据最新结果立即调整策略"""

    def __init__(self):
        super().__init__("real_time_feedback_learner", "2.0")
        self.learning_state = {
            'recent_success_patterns': [],
            'failed_strategies': [],
            'adaptation_factors': {},
            'performance_trend': 'stable'
        }
        self.parameters = {
            'learning_rate': 0.2,
            'adaptation_speed': 0.1,
            'pattern_memory_size': 50
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练实时学习器"""
        if len(history_data) < 20:
            return False

        # 分析历史成功模式
        self._analyze_historical_success(history_data)

        # 初始化适应因子
        self._initialize_adaptation_factors()

        self.is_trained = True
        return True

    def _analyze_historical_success(self, history_data: List[LotteryHistory]):
        """分析历史成功模式"""
        success_patterns = []

        for i in range(len(history_data) - 5):
            window = history_data[i:i + 5]
            # 分析这个时间窗口内的成功特征
            pattern_features = self._extract_pattern_features(window)
            success_rate = self._calculate_window_success_rate(window, history_data[i + 5:i + 10])

            if success_rate > 0.6:  # 成功阈值
                success_patterns.append({
                    'features': pattern_features,
                    'success_rate': success_rate,
                    'timestamp': window[-1].date if hasattr(window[-1], 'date') else datetime.now()
                })

        # 保留最佳模式
        success_patterns.sort(key=lambda x: x['success_rate'], reverse=True)
        self.learning_state['recent_success_patterns'] = success_patterns[:self.parameters['pattern_memory_size']]

    def process_feedback(self, prediction: Dict, actual_result: LotteryHistory):
        """处理预测反馈并立即学习"""
        if not self.is_trained:
            return

        # 计算预测准确度
        accuracy = self._calculate_prediction_accuracy(prediction, actual_result)

        # 更新学习状态
        self._update_learning_state(accuracy, prediction, actual_result)

        # 调整适应因子
        self._adapt_strategy_based_on_feedback(accuracy)

    def _calculate_prediction_accuracy(self, prediction: Dict, actual: LotteryHistory) -> float:
        """计算预测准确度"""
        if 'recommendations' not in prediction:
            return 0.0

        best_rec = prediction['recommendations'][0]
        front_hits = len(set(best_rec.get('front_numbers', [])) & set(actual.front_area))
        back_hits = len(set(best_rec.get('back_numbers', [])) & set(actual.back_area))

        # 加权评分
        return (front_hits * 0.7 + back_hits * 0.3) / (5 * 0.7 + 2 * 0.3)

    def _update_learning_state(self, accuracy: float, prediction: Dict, actual: LotteryHistory):
        """更新学习状态"""
        if accuracy > 0.6:
            # 记录成功模式
            success_pattern = {
                'prediction_features': self._extract_prediction_features(prediction),
                'actual_result': actual,
                'accuracy': accuracy,
                'timestamp': datetime.now()
            }
            self.learning_state['recent_success_patterns'].append(success_pattern)

            # 限制记忆大小
            if len(self.learning_state['recent_success_patterns']) > self.parameters['pattern_memory_size']:
                self.learning_state['recent_success_patterns'].pop(0)

        else:
            # 记录失败策略
            failed_strategy = {
                'prediction': prediction,
                'actual': actual,
                'accuracy': accuracy
            }
            self.learning_state['failed_strategies'].append(failed_strategy)

    def _adapt_strategy_based_on_feedback(self, accuracy: float):
        """基于反馈调整策略"""
        # 根据准确度趋势调整学习率
        if accuracy < 0.4:
            # 表现差，增加探索性
            self.parameters['learning_rate'] = min(0.3, self.parameters['learning_rate'] + 0.05)
            self.learning_state['performance_trend'] = 'declining'
        elif accuracy > 0.7:
            # 表现好，减少探索性
            self.parameters['learning_rate'] = max(0.1, self.parameters['learning_rate'] - 0.02)
            self.learning_state['performance_trend'] = 'improving'

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于实时学习的预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 应用学习到的策略
        adapted_prediction = self._apply_learned_strategies(history_data)

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [adapted_prediction],
            'analysis': {
                'learning_state': self.learning_state['performance_trend'],
                'success_patterns_count': len(self.learning_state['recent_success_patterns']),
                'current_learning_rate': self.parameters['learning_rate']
            }
        }

    def _apply_learned_strategies(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """应用学习到的策略"""
        recent_data = history_data[-10:]

        # 匹配最近的成功模式
        best_matching_pattern = self._find_best_matching_pattern(recent_data)

        if best_matching_pattern:
            # 使用成功模式进行预测
            prediction = self._generate_from_success_pattern(best_matching_pattern, recent_data)
            confidence = 0.8
        else:
            # 使用自适应策略
            prediction = self._adaptive_fallback_strategy(recent_data)
            confidence = 0.65

        return {
            'front_numbers': sorted(prediction['front']),
            'back_numbers': sorted(prediction['back']),
            'confidence': confidence,
            'strategy_source': 'learned_pattern' if best_matching_pattern else 'adaptive_fallback'
        }

    def _initialize_adaptation_factors(self):
        """初始化适应因子"""
        self.learning_state['adaptation_factors'] = {
            'trend_following': 1.0,
            'reversion_strategy': 1.0,
            'pattern_matching': 1.0
        }

    def _extract_pattern_features(self, window):
        """提取模式特征"""
        return {}

    def _calculate_window_success_rate(self, window, next_window):
        """计算窗口成功率"""
        return 0.5

    def _extract_prediction_features(self, prediction):
        """提取预测特征"""
        return {}