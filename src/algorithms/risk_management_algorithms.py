# algorithms/risk_management_algorithms.py
from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
from src.model.lottery_models import LotteryHistory
import random
import math

class RiskAssessmentAlgorithm(BaseAlgorithm):
    """风险评估算法"""

    def __init__(self):
        super().__init__("risk_assessment", "1.0")
        self.risk_metrics = {}
        self.parameters = {
            'max_stake_ratio': 0.05,  # 最大投注资金比例
            'risk_tolerance': 0.7,    # 风险容忍度
            'diversification_factor': 3  # 分散投资因子
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练风险评估模型"""
        if not history_data:
            return False

        # 计算历史数据的基本统计信息
        total_periods = len(history_data)
        
        # 计算号码分布的稳定性
        front_number_stability = self._calculate_number_stability(
            [record.front_area for record in history_data], 35)
        back_number_stability = self._calculate_number_stability(
            [record.back_area for record in history_data], 12)
        
        # 计算历史中奖概率分布
        hit_probability_distribution = self._analyze_hit_distribution(history_data)
        
        self.risk_metrics = {
            'total_periods': total_periods,
            'front_stability': front_number_stability,
            'back_stability': back_number_stability,
            'hit_probability_distribution': hit_probability_distribution
        }

        self.is_trained = True
        return True

    def _calculate_number_stability(self, number_series: List[List[int]], max_number: int) -> float:
        """计算号码稳定性"""
        if not number_series:
            return 0.0
            
        # 统计每个号码的出现频率
        number_frequency = {i: 0 for i in range(1, max_number + 1)}
        total_appearances = 0
        
        for numbers in number_series:
            for number in numbers:
                number_frequency[number] += 1
                total_appearances += 1
        
        # 计算频率的标准差（越小表示越稳定）
        if total_appearances == 0:
            return 0.0
            
        expected_frequency = total_appearances / max_number
        variance = sum((freq - expected_frequency) ** 2 for freq in number_frequency.values()) / max_number
        std_deviation = math.sqrt(variance)
        
        # 稳定性与标准差成反比
        stability = 1.0 / (1.0 + std_deviation)
        return stability

    def _analyze_hit_distribution(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """分析历史中奖分布"""
        # 简化实现，实际应用中可以更复杂
        return {
            'front_hit_average': 5,  # 前区命中平均数
            'back_hit_average': 2,   # 后区命中平均数
            'max_front_hit': 5,      # 前区最大命中数
            'max_back_hit': 2        # 后区最大命中数
        }

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """风险评估预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 基于历史数据和参数计算风险指标
        risk_score = self._calculate_risk_score()
        recommended_stake = self._calculate_recommended_stake()
        diversification_strategy = self._generate_diversification_strategy()
        
        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [{
                'risk_score': risk_score,
                'recommended_stake_ratio': recommended_stake,
                'diversification_strategy': diversification_strategy,
                'confidence': 0.85
            }],
            'analysis': self.risk_metrics
        }

    def _calculate_risk_score(self) -> float:
        """计算风险评分"""
        # 基于号码稳定性和其他因素计算综合风险评分
        stability_factor = (self.risk_metrics['front_stability'] + self.risk_metrics['back_stability']) / 2
        # 风险评分，值越小风险越低
        risk_score = 1.0 - stability_factor
        return max(0.0, min(1.0, risk_score))

    def _calculate_recommended_stake(self) -> float:
        """计算推荐的投注资金比例"""
        risk_score = self._calculate_risk_score()
        # 根据风险评分调整投注比例，风险越高比例越低
        base_ratio = self.parameters['max_stake_ratio']
        adjusted_ratio = base_ratio * (1.0 - risk_score)
        return max(0.01, adjusted_ratio)  # 至少保证1%

    def _generate_diversification_strategy(self) -> Dict[str, Any]:
        """生成分散投资策略"""
        risk_score = self._calculate_risk_score()
        diversification_factor = self.parameters['diversification_factor']
        
        # 根据风险评分调整分散投资的数量
        if risk_score < 0.3:
            num_combinations = diversification_factor
        elif risk_score < 0.6:
            num_combinations = diversification_factor + 1
        else:
            num_combinations = diversification_factor + 2
            
        return {
            'recommended_combinations': num_combinations,
            'selection_strategy': 'mixed' if risk_score < 0.5 else 'conservative'
        }


class PortfolioOptimizationAlgorithm(BaseAlgorithm):
    """投资组合优化算法"""

    def __init__(self):
        super().__init__("portfolio_optimization", "1.0")
        self.optimization_results = {}
        self.parameters = {
            'target_return': 0.1,      # 目标回报率
            'max_volatility': 0.15,    # 最大波动率
            'risk_free_rate': 0.02     # 无风险利率
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练投资组合优化模型"""
        if not history_data:
            return False

        # 分析历史回报和风险
        returns_history = self._calculate_historical_returns(history_data)
        volatility = self._calculate_volatility(returns_history)
        
        self.optimization_results = {
            'historical_returns': returns_history,
            'historical_volatility': volatility,
            'sharpe_ratio': self._calculate_sharpe_ratio(returns_history, volatility) if volatility > 0 else 0
        }

        self.is_trained = True
        return True

    def _calculate_historical_returns(self, history_data: List[LotteryHistory]) -> List[float]:
        """计算历史回报率"""
        # 简化实现，实际中可以基于模拟投注结果计算
        returns = []
        for i in range(1, min(21, len(history_data))):  # 最近20期
            # 模拟固定回报率
            returns.append(random.uniform(-0.05, 0.2))
        return returns

    def _calculate_volatility(self, returns: List[float]) -> float:
        """计算波动率"""
        if len(returns) < 2:
            return 0.0
            
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        return math.sqrt(variance)

    def _calculate_sharpe_ratio(self, returns: List[float], volatility: float) -> float:
        """计算夏普比率"""
        if volatility <= 0:
            return 0.0
            
        mean_return = sum(returns) / len(returns)
        excess_return = mean_return - self.parameters['risk_free_rate']
        return excess_return / volatility

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """投资组合优化预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 生成优化的投资组合建议
        optimal_allocation = self._optimize_allocation()
        risk_adjusted_strategy = self._generate_risk_adjusted_strategy()
        
        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [{
                'optimal_allocation': optimal_allocation,
                'risk_adjusted_strategy': risk_adjusted_strategy,
                'expected_return': self.parameters['target_return'],
                'risk_metrics': self.optimization_results,
                'confidence': 0.8
            }],
            'analysis': self.optimization_results
        }

    def _optimize_allocation(self) -> Dict[str, Any]:
        """优化资金分配"""
        # 简化实现，实际中可以使用现代投资组合理论等方法
        sharpe_ratio = self.optimization_results.get('sharpe_ratio', 0)
        
        if sharpe_ratio > 1.0:
            conservative_ratio = 0.3
            moderate_ratio = 0.5
            aggressive_ratio = 0.2
        elif sharpe_ratio > 0.5:
            conservative_ratio = 0.4
            moderate_ratio = 0.4
            aggressive_ratio = 0.2
        else:
            conservative_ratio = 0.6
            moderate_ratio = 0.3
            aggressive_ratio = 0.1
            
        return {
            'conservative': conservative_ratio,
            'moderate': moderate_ratio,
            'aggressive': aggressive_ratio
        }

    def _generate_risk_adjusted_strategy(self) -> Dict[str, Any]:
        """生成风险调整策略"""
        volatility = self.optimization_results.get('historical_volatility', 0)
        
        if volatility < 0.05:
            strategy = 'aggressive'
            max_stake = 0.1
        elif volatility < 0.1:
            strategy = 'moderate'
            max_stake = 0.07
        else:
            strategy = 'conservative'
            max_stake = 0.05
            
        return {
            'strategy_type': strategy,
            'max_stake_per_bet': max_stake,
            'recommended_diversification': max(3, int(10 * (1 - volatility)))
        }


class StopLossAlgorithm(BaseAlgorithm):
    """止损算法"""

    def __init__(self):
        super().__init__("stop_loss", "1.0")
        self.stop_loss_rules = {}
        self.parameters = {
            'max_loss_ratio': 0.2,     # 最大损失比例
            'trailing_stop': 0.1,      # 追踪止损比例
            'recovery_period': 5       # 恢复期（期数）
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练止损模型"""
        if not history_data:
            return False

        # 分析历史最大连续亏损
        max_consecutive_losses = self._analyze_consecutive_losses(history_data)
        
        self.stop_loss_rules = {
            'max_consecutive_losses': max_consecutive_losses,
            'suggested_stop_loss_ratio': min(
                self.parameters['max_loss_ratio'],
                max_consecutive_losses * 0.02
            )
        }

        self.is_trained = True
        return True

    def _analyze_consecutive_losses(self, history_data: List[LotteryHistory]) -> int:
        """分析历史最大连续亏损期数"""
        # 简化实现，实际中可以基于模拟投注结果计算
        max_consecutive = 0
        current_consecutive = 0
        
        for i in range(min(50, len(history_data))):  # 分析最近50期
            # 模拟随机输赢结果
            is_loss = random.random() > 0.3  # 假设70%的胜率
            
            if is_loss:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
                
        return max(1, max_consecutive)

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """止损策略预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 生成止损策略建议
        stop_loss_strategy = self._generate_stop_loss_strategy()
        recovery_plan = self._generate_recovery_plan()
        
        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [{
                'stop_loss_strategy': stop_loss_strategy,
                'recovery_plan': recovery_plan,
                'max_loss_threshold': self.parameters['max_loss_ratio'],
                'confidence': 0.9
            }],
            'analysis': self.stop_loss_rules
        }

    def _generate_stop_loss_strategy(self) -> Dict[str, Any]:
        """生成止损策略"""
        return {
            'fixed_stop_loss': self.stop_loss_rules['suggested_stop_loss_ratio'],
            'trailing_stop': self.parameters['trailing_stop'],
            'conditional_stops': {
                'consecutive_losses_3': 0.1,
                'consecutive_losses_5': 0.05,
                'daily_loss_limit': 0.15
            }
        }

    def _generate_recovery_plan(self) -> Dict[str, Any]:
        """生成恢复计划"""
        return {
            'cool_down_periods': self.parameters['recovery_period'],
            'reduced_stake_ratio': 0.5,
            'strategy_review_required': True
        }