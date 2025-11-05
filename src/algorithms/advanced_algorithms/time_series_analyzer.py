# src/algorithms/advanced_algorithms/time_series_analyzer.py
import pandas as pd
import numpy as np
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any
import logging


class TimeSeriesAnalyzer(BaseAlgorithm):
    """多时间尺度时序分析器 - 修复版"""
    name = "TimeSeriesAnalyzer"
    version = "2.0"

    def __init__(self):
        super().__init__()
        self.parameters = {
            'short_term_window': 20,
            'medium_term_window': 50,
            'long_term_window': 100
        }
        self.trend_data = {}
        self.periodic_patterns = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """时序模型训练 - 分析历史数据的时序模式"""
        if not history_data:
            return False

        try:
            # 准备时序数据
            ts_data = self._prepare_time_series(history_data)

            # 多时间尺度分析
            self._analyze_multi_scale_trends(ts_data)

            # 分析周期性模式
            self._analyze_periodic_patterns(history_data)

            self.is_trained = True
            logging.info(f"时序分析器训练完成，分析了 {len(history_data)} 期数据")
            return True

        except Exception as e:
            logging.error(f"时序分析器训练失败: {e}")
            return False

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于时序分析进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        try:
            # 生成基于时序的推荐
            front_recommendations = self._generate_time_based_recommendations('front')
            back_recommendations = self._generate_time_based_recommendations('back')

            # 计算总体置信度
            confidence = self._calculate_overall_confidence()

            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{
                    'front_number_scores': front_recommendations,
                    'back_number_scores': back_recommendations,
                    'confidence': confidence,
                    'trend_summary': self._get_trend_summary()
                }],
                'analysis': {
                    'trend_data': self.trend_data,
                    'periodic_patterns': self.periodic_patterns,
                    'parameters_used': self.parameters
                }
            }

        except Exception as e:
            logging.error(f"时序预测失败: {e}")
            return {'error': str(e)}

    def _prepare_time_series(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """将历史数据转换为时间序列格式"""
        front_series = {i: [] for i in range(1, 36)}
        back_series = {i: [] for i in range(1, 13)}

        # 按时间顺序处理数据（确保从早到晚）
        sorted_data = sorted(history_data, key=lambda x: x.period_number)

        for record in sorted_data:
            for num in range(1, 36):
                front_series[num].append(1 if num in record.front_area else 0)
            for num in range(1, 13):
                back_series[num].append(1 if num in record.back_area else 0)

        logging.info(f"准备了 {len(sorted_data)} 期数据的时序序列")
        return {'front': front_series, 'back': back_series}

    def _analyze_multi_scale_trends(self, ts_data: Dict[str, Any]):
        """多时间尺度趋势分析"""
        self.trend_data = {
            'short_term': self._analyze_time_scale(ts_data, self.parameters['short_term_window']),
            'medium_term': self._analyze_time_scale(ts_data, self.parameters['medium_term_window']),
            'long_term': self._analyze_time_scale(ts_data, self.parameters['long_term_window'])
        }

        logging.info("多时间尺度趋势分析完成")

    def _analyze_time_scale(self, ts_data: Dict[str, Any], window: int) -> Dict[str, Any]:
        """分析指定时间尺度的趋势"""
        front_trends = {}
        back_trends = {}

        # 分析前区号码趋势
        for num in range(1, 36):
            series = ts_data['front'][num]
            if len(series) >= window:
                recent_data = series[-window:]
                trend_info = self._calculate_trend_metrics(recent_data)
                front_trends[num] = trend_info

        # 分析后区号码趋势
        for num in range(1, 13):
            series = ts_data['back'][num]
            if len(series) >= window:
                recent_data = series[-window:]
                trend_info = self._calculate_trend_metrics(recent_data)
                back_trends[num] = trend_info

        return {'front': front_trends, 'back': back_trends}

    def _calculate_trend_metrics(self, series: List[int]) -> Dict[str, Any]:
        """计算趋势指标"""
        if not series:
            return {}

        # 基础统计
        appearance_rate = np.mean(series)
        total_appearances = sum(series)

        # 趋势分析
        trend_direction = self._calculate_trend_direction(series)
        momentum = self._calculate_momentum(series)

        # 移动平均
        window_size = min(5, len(series))
        moving_avg = pd.Series(series).rolling(window=window_size).mean().iloc[-1] if len(
            series) >= window_size else appearance_rate

        return {
            'appearance_rate': float(appearance_rate),
            'total_appearances': total_appearances,
            'trend_direction': trend_direction,  # 1:上升, -1:下降, 0:平稳
            'momentum': float(momentum),
            'moving_avg': float(moving_avg) if not np.isnan(moving_avg) else 0.0
        }

    def _calculate_trend_direction(self, series: List[int]) -> int:
        """计算趋势方向"""
        if len(series) < 2:
            return 0

        # 使用线性回归计算趋势
        x = np.arange(len(series))
        y = np.array(series)

        try:
            slope = np.polyfit(x, y, 1)[0]
            if slope > 0.02:  # 上升趋势
                return 1
            elif slope < -0.02:  # 下降趋势
                return -1
            else:  # 平稳
                return 0
        except:
            return 0

    def _calculate_momentum(self, series: List[int]) -> float:
        """计算动量指标"""
        if len(series) < 5:
            return 0.0

        # 近期表现与长期表现的对比
        recent_window = min(5, len(series) // 2)
        long_window = min(10, len(series))

        recent_avg = np.mean(series[-recent_window:])
        long_avg = np.mean(series[-long_window:])

        if long_avg > 0:
            return (recent_avg - long_avg) / long_avg
        else:
            return 0.0

    def _analyze_periodic_patterns(self, history_data: List[LotteryHistory]):
        """分析周期性模式"""
        self.periodic_patterns = {
            'front': self._analyze_number_periods(history_data, 'front'),
            'back': self._analyze_number_periods(history_data, 'back')
        }

        logging.info("周期性模式分析完成")

    def _analyze_number_periods(self, history_data: List[LotteryHistory], area_type: str) -> Dict[int, Any]:
        """分析号码出现周期"""
        periods = {}
        numbers_range = range(1, 36) if area_type == 'front' else range(1, 13)
        sorted_data = sorted(history_data, key=lambda x: x.period_number)

        for num in numbers_range:
            appearances = []
            for idx, record in enumerate(sorted_data):
                numbers = record.front_area if area_type == 'front' else record.back_area
                if num in numbers:
                    appearances.append(idx)

            if len(appearances) > 1:
                # 计算出现间隔
                intervals = [appearances[i] - appearances[i - 1] for i in range(1, len(appearances))]
                avg_interval = np.mean(intervals) if intervals else 0
                std_interval = np.std(intervals) if len(intervals) > 1 else 0

                # 当前遗漏期数
                current_omission = len(sorted_data) - appearances[-1] - 1 if appearances else len(sorted_data)

                periods[num] = {
                    'total_appearances': len(appearances),
                    'avg_interval': float(avg_interval),
                    'std_interval': float(std_interval),
                    'current_omission': current_omission,
                    'last_appearance_idx': appearances[-1] if appearances else -1
                }

        return periods

    def _generate_time_based_recommendations(self, area_type: str) -> List[Dict[str, Any]]:
        """生成基于时序的推荐"""
        recommendations = []
        numbers_range = range(1, 36) if area_type == 'front' else range(1, 13)

        for num in numbers_range:
            score = self._calculate_time_series_score(num, area_type)
            if score > 0:  # 只包括有意义的评分
                trend_info = self._get_trend_info(num, area_type)
                period_info = self.periodic_patterns[area_type].get(num, {})

                recommendations.append({
                    'number': num,
                    'score': round(score, 4),
                    'trend_direction': trend_info.get('trend_direction', 0),
                    'momentum': trend_info.get('momentum', 0),
                    'omission': period_info.get('current_omission', 0),
                    'appearance_rate': trend_info.get('appearance_rate', 0)
                })

        # 按评分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations

    def _calculate_time_series_score(self, number: int, area_type: str) -> float:
        """计算时序综合评分"""
        base_score = 0.0
        weights = {'short_term': 0.5, 'medium_term': 0.3, 'long_term': 0.2}

        # 1. 多时间尺度趋势评分 (60%)
        for scale, weight in weights.items():
            scale_data = self.trend_data[scale][area_type].get(number, {})
            if scale_data:
                trend_score = self._calculate_trend_score(scale_data)
                base_score += trend_score * weight

        # 2. 周期性模式评分 (30%)
        period_data = self.periodic_patterns[area_type].get(number, {})
        period_score = self._calculate_period_score(period_data)
        base_score += period_score * 0.3

        # 3. 动量评分 (10%)
        momentum_data = self.trend_data['short_term'][area_type].get(number, {})
        momentum = momentum_data.get('momentum', 0)
        base_score += max(0, momentum) * 0.1

        return min(max(base_score, 0), 1)  # 确保在0-1范围内

    def _calculate_trend_score(self, trend_data: Dict[str, Any]) -> float:
        """计算趋势评分"""
        score = 0.0

        # 出现率基础分
        appearance_rate = trend_data.get('appearance_rate', 0)
        score += appearance_rate * 0.4

        # 趋势方向加分
        trend_direction = trend_data.get('trend_direction', 0)
        if trend_direction == 1:  # 上升趋势
            score += 0.3
        elif trend_direction == 0:  # 平稳
            score += 0.15

        # 移动平均稳定性
        moving_avg = trend_data.get('moving_avg', 0)
        score += moving_avg * 0.3

        return score

    def _calculate_period_score(self, period_data: Dict[str, Any]) -> float:
        """计算周期性评分"""
        if not period_data:
            return 0.0

        current_omission = period_data.get('current_omission', 0)
        avg_interval = period_data.get('avg_interval', 10)

        if avg_interval > 0:
            # 遗漏期数接近平均间隔时得分最高
            omission_ratio = current_omission / avg_interval
            if 0.8 <= omission_ratio <= 1.2:
                return 0.8
            elif 0.5 <= omission_ratio <= 1.5:
                return 0.5
            else:
                return 0.2

        return 0.0

    def _get_trend_info(self, number: int, area_type: str) -> Dict[str, Any]:
        """获取号码的趋势信息"""
        # 优先使用短期趋势数据
        return self.trend_data['short_term'][area_type].get(number, {})

    def _calculate_overall_confidence(self) -> float:
        """计算总体置信度"""
        # 基于数据质量和分析深度计算置信度
        confidence = 0.7  # 基础置信度

        # 如果有足够的趋势数据，提高置信度
        if (self.trend_data.get('short_term', {}).get('front') and
                self.trend_data.get('short_term', {}).get('back')):
            confidence += 0.1

        # 如果有周期性分析，提高置信度
        if self.periodic_patterns.get('front') and self.periodic_patterns.get('back'):
            confidence += 0.1

        return min(confidence, 0.95)

    def _get_trend_summary(self) -> Dict[str, Any]:
        """获取趋势分析摘要"""
        return {
            'analysis_periods': {
                'short_term': self.parameters['short_term_window'],
                'medium_term': self.parameters['medium_term_window'],
                'long_term': self.parameters['long_term_window']
            },
            'total_numbers_analyzed': {
                'front': 35,
                'back': 12
            }
        }