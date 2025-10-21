# engine/evaluation_system.py
from typing import List, Dict, Any
from src.model.lottery_models import (
    LotteryHistory, RewardPenaltyRecord,
    AlgorithmPerformance, AlgorithmRecommendation
)

class EvaluationSystem:
    """评估反馈系统"""

    def __init__(self):
        self.performance_metrics = {}

    def evaluate_recommendation(self, recommendation: AlgorithmRecommendation,
                              actual_result: LotteryHistory) -> RewardPenaltyRecord:
        """评估推荐结果"""
        # 计算命中数量
        front_hit_count = len(set(recommendation.recommendation_combinations[0]['front_numbers']) &
                             set(actual_result.front_area))
        back_hit_count = len(set(recommendation.recommendation_combinations[0]['back_numbers']) &
                            set(actual_result.back_area))

        # 计算命中得分
        hit_score = front_hit_count * 2 + back_hit_count * 3

        # 计算奖励积分和惩罚积分
        reward_points = hit_score * 10
        penalty_points = 0 if hit_score > 0 else 5

        # 创建评估记录
        evaluation_record = RewardPenaltyRecord(
            id=0,
            period_number=actual_result.period_number,
            algorithm_version=recommendation.algorithm_version,
            recommendation_id=recommendation.id,
            front_hit_count=front_hit_count,
            back_hit_count=back_hit_count,
            hit_score=hit_score,
            reward_points=reward_points,
            penalty_points=penalty_points,
            net_points=reward_points - penalty_points,
            hit_details={
                'front_hit': list(set(recommendation.recommendation_combinations[0]['front_numbers']) &
                                set(actual_result.front_area)),
                'back_hit': list(set(recommendation.recommendation_combinations[0]['back_numbers']) &
                               set(actual_result.back_area))
            },
            missed_numbers={
                'front_missed': list(set(actual_result.front_area) -
                                   set(recommendation.recommendation_combinations[0]['front_numbers'])),
                'back_missed': list(set(actual_result.back_area) -
                                  set(recommendation.recommendation_combinations[0]['back_numbers']))
            }
        )

        return evaluation_record

    def update_algorithm_performance(self, evaluation_record: RewardPenaltyRecord) -> AlgorithmPerformance:
        """更新算法性能数据"""
        # 实现性能更新逻辑
        performance = AlgorithmPerformance(
            id=0,
            algorithm_version=evaluation_record.algorithm_version
        )

        return performance

    def calculate_performance_metrics(self, evaluation_records: List[RewardPenaltyRecord]) -> Dict[str, Any]:
        """计算性能指标"""
        if not evaluation_records:
            return {}

        total_recommendations = len(evaluation_records)
        total_front_hits = sum([rec.front_hit_count for rec in evaluation_records])
        total_back_hits = sum([rec.back_hit_count for rec in evaluation_records])

        metrics = {
            'total_recommendations': total_recommendations,
            'avg_front_hit_rate': total_front_hits / (total_recommendations * 5),  # 假设每组5个前区号码
            'avg_back_hit_rate': total_back_hits / (total_recommendations * 2),   # 假设每组2个后区号码
            'total_reward_points': sum([rec.reward_points for rec in evaluation_records]),
            'total_penalty_points': sum([rec.penalty_points for rec in evaluation_records]),
            'net_points': sum([rec.net_points for rec in evaluation_records])
        }

        return metrics
