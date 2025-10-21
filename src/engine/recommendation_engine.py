# engine/recommendation_engine.py
from typing import List, Dict, Any
from src.model.lottery_models import LotteryHistory, AlgorithmRecommendation
from src.algorithms.base_algorithm import BaseAlgorithm

class RecommendationEngine:
    """推荐引擎"""

    def __init__(self):
        self.algorithms: List[BaseAlgorithm] = []
        self.algorithm_weights: Dict[str, float] = {}

    def add_algorithm(self, algorithm: BaseAlgorithm, weight: float = 1.0):
        """添加算法到推荐引擎"""
        self.algorithms.append(algorithm)
        self.algorithm_weights[algorithm.name] = weight

    def train_all_algorithms(self, history_data: List[LotteryHistory]) -> Dict[str, bool]:
        """训练所有算法"""
        results = {}
        for algorithm in self.algorithms:
            results[algorithm.name] = algorithm.train(history_data)
        return results

    def generate_recommendations(self, history_data: List[LotteryHistory],
                               user_preferences: Dict[str, Any] = None) -> AlgorithmRecommendation:
        """生成推荐结果"""
        all_recommendations = []
        algorithm_weights = []

        for algorithm in self.algorithms:
            if algorithm.is_trained:
                prediction = algorithm.predict(history_data)
                if 'recommendations' in prediction:
                    all_recommendations.append(prediction['recommendations'])
                    algorithm_weights.append(self.algorithm_weights.get(algorithm.name, 1.0))

        # 集成所有算法的推荐结果
        integrated_recommendations = self._integrate_recommendations(
            all_recommendations, algorithm_weights
        )

        # 创建推荐记录
        recommendation_record = AlgorithmRecommendation(
            id=0,  # 数据库会自动生成
            period_number=self._get_next_period_number(history_data),
            recommend_time=self._get_current_time(),
            algorithm_version="ensemble_v1.0",
            recommendation_combinations=integrated_recommendations,
            algorithm_parameters={},
            model_weights={k: v for k, v in self.algorithm_weights.items() if k in [alg.name for alg in self.algorithms]},
            confidence_score=self._calculate_overall_confidence(integrated_recommendations),
            risk_level=self._assess_risk_level(integrated_recommendations),
            analysis_basis={},
            key_patterns=[],
            recommend_type="primary"
        )

        return recommendation_record

    def _integrate_recommendations(self, recommendations_list: List, weights: List[float]) -> List[Dict[str, Any]]:
        """集成多个算法的推荐结果"""
        # 实现推荐结果集成逻辑
        return recommendations_list[0] if recommendations_list else []

    def _get_next_period_number(self, history_data: List[LotteryHistory]) -> str:
        """获取下一期期号"""
        if not history_data:
            return "2024001"
        latest_period = max([h.period_number for h in history_data])
        return str(int(latest_period) + 1)

    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now()

    def _calculate_overall_confidence(self, recommendations: List[Dict[str, Any]]) -> float:
        """计算总体置信度"""
        if not recommendations:
            return 0.0
        confidences = [rec.get('confidence', 0.0) for rec in recommendations]
        return sum(confidences) / len(confidences)

    def _assess_risk_level(self, recommendations: List[Dict[str, Any]]) -> str:
        """评估风险等级"""
        avg_confidence = self._calculate_overall_confidence(recommendations)
        if avg_confidence >= 0.8:
            return "low"
        elif avg_confidence >= 0.6:
            return "medium"
        else:
            return "high"
