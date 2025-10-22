# src/model/lottery_models.py
from datetime import datetime
from typing import List, Dict, Any, Optional

class LotteryHistory:
    """历史开奖数据实体类"""

    def __init__(self, id: int = None, period_number: str = None, draw_date: str = None,
                 draw_time: datetime = None, front_area: List[int] = None,
                 back_area: List[int] = None, sum_value: int = None,
                 span_value: int = None, ac_value: int = None,
                 odd_even_ratio: str = None, size_ratio: str = None,
                 prime_composite_ratio: str = None,
                 consecutive_numbers: List[List[int]] = None,
                 consecutive_count: int = None, tail_numbers: List[int] = None,
                 data_source: str = None, data_quality: int = None):
        self.id = id
        self.period_number = period_number
        self.draw_date = draw_date
        self.draw_time = draw_time
        self.front_area = front_area if front_area else []
        self.back_area = back_area if back_area else []
        self.sum_value = sum_value
        self.span_value = span_value
        self.ac_value = ac_value
        self.odd_even_ratio = odd_even_ratio
        self.size_ratio = size_ratio
        self.prime_composite_ratio = prime_composite_ratio
        self.consecutive_numbers = consecutive_numbers
        self.consecutive_count = consecutive_count
        self.tail_numbers = tail_numbers
        self.data_source = data_source
        self.data_quality = data_quality

class NumberStatistics:
    """号码统计实体类"""

    def __init__(self, number: int = None, number_type: str = None,
                 total_appearances: int = None, appearance_rate: float = None,
                 recent_10_appearances: int = None, recent_20_appearances: int = None,
                 recent_50_appearances: int = None, current_omission: int = None,
                 max_omission: int = None, avg_omission: float = None,
                 heat_status: str = None, heat_score: float = None,
                 strong_followers: List[int] = None,
                 strong_precursors: List[int] = None,
                 position_preference: Dict[str, Any] = None):
        self.number = number
        self.number_type = number_type
        self.total_appearances = total_appearances
        self.appearance_rate = appearance_rate
        self.recent_10_appearances = recent_10_appearances
        self.recent_20_appearances = recent_20_appearances
        self.recent_50_appearances = recent_50_appearances
        self.current_omission = current_omission
        self.max_omission = max_omission
        self.avg_omission = avg_omission
        self.heat_status = heat_status
        self.heat_score = heat_score
        self.strong_followers = strong_followers if strong_followers else []
        self.strong_precursors = strong_precursors if strong_precursors else []
        self.position_preference = position_preference

class AlgorithmConfig:
    """算法配置实体类"""

    def __init__(self, id: int = None, algorithm_name: str = None,
                 algorithm_type: str = None, parameters: Dict[str, Any] = None,
                 description: str = None, version: str = None,
                 is_active: bool = None, is_default: bool = None,
                 min_data_required: int = None, expected_accuracy: float = None,
                 computation_complexity: str = None, memory_requirements: str = None):
        self.id = id
        self.algorithm_name = algorithm_name
        self.algorithm_type = algorithm_type
        self.parameters = parameters if parameters else {}
        self.description = description
        self.version = version
        self.is_active = is_active
        self.is_default = is_default
        self.min_data_required = min_data_required
        self.expected_accuracy = expected_accuracy
        self.computation_complexity = computation_complexity
        self.memory_requirements = memory_requirements

class AlgorithmPerformance:
    """算法性能实体类"""

    def __init__(self, id: int = None, algorithm_version: str = None,
                 total_recommendations: int = None, total_periods_analyzed: int = None,
                 avg_front_hit_rate: float = None, avg_back_hit_rate: float = None,
                 hit_distribution: Dict[str, Any] = None, confidence_accuracy: float = None,
                 risk_adjusted_return: float = None, stability_score: float = None,
                 consistency_rate: float = None, current_weight: float = None,
                 weight_history: List[Dict[str, Any]] = None,
                 performance_trend: str = None):
        self.id = id
        self.algorithm_version = algorithm_version
        self.total_recommendations = total_recommendations
        self.total_periods_analyzed = total_periods_analyzed
        self.avg_front_hit_rate = avg_front_hit_rate
        self.avg_back_hit_rate = avg_back_hit_rate
        self.hit_distribution = hit_distribution
        self.confidence_accuracy = confidence_accuracy
        self.risk_adjusted_return = risk_adjusted_return
        self.stability_score = stability_score
        self.consistency_rate = consistency_rate
        self.current_weight = current_weight
        self.weight_history = weight_history if weight_history else []
        self.performance_trend = performance_trend

class AlgorithmRecommendation:
    """算法推荐记录实体类"""

    def __init__(self, id: int = None, period_number: str = None,
                 recommend_time: datetime = None, algorithm_version: str = None,
                 recommendation_combinations: List[Dict[str, Any]] = None,
                 algorithm_parameters: Dict[str, Any] = None,
                 model_weights: Dict[str, Any] = None,
                 confidence_score: float = None, risk_level: str = None,
                 analysis_basis: Dict[str, Any] = None,
                 key_patterns: List[Dict[str, Any]] = None,
                 recommend_type: str = None):
        self.id = id
        self.period_number = period_number
        self.recommend_time = recommend_time
        self.algorithm_version = algorithm_version
        self.recommendation_combinations = recommendation_combinations if recommendation_combinations else []
        self.algorithm_parameters = algorithm_parameters if algorithm_parameters else {}
        self.model_weights = model_weights if model_weights else {}
        self.confidence_score = confidence_score
        self.risk_level = risk_level
        self.analysis_basis = analysis_basis if analysis_basis else {}
        self.key_patterns = key_patterns if key_patterns else []
        self.recommend_type = recommend_type

class RecommendationDetail:
    """推荐详情实体类"""

    def __init__(self, id: int = None, recommendation_metadata_id: int = None,
                 recommend_type: str = None, strategy_logic: str = None,
                 front_numbers: str = None, back_numbers: str = None,
                 win_probability: float = None, created_at: datetime = None):
        self.id = id
        self.recommendation_metadata_id = recommendation_metadata_id
        self.recommend_type = recommend_type
        self.strategy_logic = strategy_logic
        self.front_numbers = front_numbers
        self.back_numbers = back_numbers
        self.win_probability = win_probability
        self.created_at = created_at

class UserPurchaseRecord:
    """用户购买记录实体类"""

    def __init__(self, id: int = None, period_metadata_id: int = None,
                 user_id: str = None, purchase_type: str = None,
                 front_numbers_purchased: str = None, back_numbers_purchased: str = None,
                 cost: float = None, is_hit: bool = None,
                 front_hit_count: int = None, back_hit_count: int = None,
                 winnings_amount: float = None, purchase_time: datetime = None,
                 created_at: datetime = None):
        self.id = id
        self.period_metadata_id = period_metadata_id
        self.user_id = user_id
        self.purchase_type = purchase_type
        self.front_numbers_purchased = front_numbers_purchased
        self.back_numbers_purchased = back_numbers_purchased
        self.cost = cost
        self.is_hit = is_hit
        self.front_hit_count = front_hit_count
        self.back_hit_count = back_hit_count
        self.winnings_amount = winnings_amount
        self.purchase_time = purchase_time
        self.created_at = created_at

class PersonalBetting:
    """个人投注记录实体类"""

    def __init__(self, id: int = None, user_id: str = None, period_number: str = None,
                 bet_time: datetime = None, bet_type: str = None,
                 front_numbers: List[int] = None, front_count: int = None,
                 back_numbers: List[int] = None, back_count: int = None,
                 bet_amount: float = None, multiple: int = None,
                 is_winning: bool = None, winning_level: str = None,
                 winning_amount: float = None, strategy_type: str = None,
                 confidence_level: int = None, analysis_notes: str = None):
        self.id = id
        self.user_id = user_id
        self.period_number = period_number
        self.bet_time = bet_time
        self.bet_type = bet_type
        self.front_numbers = front_numbers if front_numbers else []
        self.front_count = front_count
        self.back_numbers = back_numbers if back_numbers else []
        self.back_count = back_count
        self.bet_amount = bet_amount
        self.multiple = multiple
        self.is_winning = is_winning
        self.winning_level = winning_level
        self.winning_amount = winning_amount
        self.strategy_type = strategy_type
        self.confidence_level = confidence_level
        self.analysis_notes = analysis_notes

class RewardPenaltyRecord:
    """奖罚记录实体类"""

    def __init__(self, id: int = None, period_number: str = None,
                 algorithm_version: str = None, recommendation_id: int = None,
                 front_hit_count: int = None, back_hit_count: int = None,
                 hit_score: float = None, reward_points: float = None,
                 penalty_points: float = None, net_points: float = None,
                 hit_details: Dict[str, Any] = None,
                 missed_numbers: List[int] = None,
                 performance_rating: int = None, accuracy_deviation: float = None,
                 improvement_suggestions: str = None, evaluation_time: datetime = None):
        self.id = id
        self.period_number = period_number
        self.algorithm_version = algorithm_version
        self.recommendation_id = recommendation_id
        self.front_hit_count = front_hit_count
        self.back_hit_count = back_hit_count
        self.hit_score = hit_score
        self.reward_points = reward_points
        self.penalty_points = penalty_points
        self.net_points = net_points
        self.hit_details = hit_details if hit_details else {}
        self.missed_numbers = missed_numbers if missed_numbers else []
        self.performance_rating = performance_rating
        self.accuracy_deviation = accuracy_deviation
        self.improvement_suggestions = improvement_suggestions
        self.evaluation_time = evaluation_time

class ABTestConfig:
    """A/B测试配置实体类"""

    def __init__(self, id: int = None, test_name: str = None,
                 test_description: str = None, algorithm_a: str = None,
                 algorithm_b: str = None, split_ratio: float = None,
                 test_parameters: Dict[str, Any] = None,
                 success_metrics: Dict[str, Any] = None, test_status: str = None,
                 start_date: str = None, end_date: str = None,
                 min_sample_size: int = None, current_sample_size: int = None,
                 algorithm_a_performance: Dict[str, Any] = None,
                 algorithm_b_performance: Dict[str, Any] = None,
                 statistical_significance: float = None, created_by: str = None):
        self.id = id
        self.test_name = test_name
        self.test_description = test_description
        self.algorithm_a = algorithm_a
        self.algorithm_b = algorithm_b
        self.split_ratio = split_ratio
        self.test_parameters = test_parameters if test_parameters else {}
        self.success_metrics = success_metrics if success_metrics else {}
        self.test_status = test_status
        self.start_date = start_date
        self.end_date = end_date
        self.min_sample_size = min_sample_size
        self.current_sample_size = current_sample_size
        self.algorithm_a_performance = algorithm_a_performance if algorithm_a_performance else {}
        self.algorithm_b_performance = algorithm_b_performance if algorithm_b_performance else {}
        self.statistical_significance = statistical_significance
        self.created_by = created_by
