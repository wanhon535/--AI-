# src/database/curd/algorithm_performance_dao.py
from typing import List, Optional
import json
from ..AllDao import AllDAO
from src.model.lottery_models import AlgorithmPerformance


class AlgorithmPerformanceDAO(AllDAO):
    """算法性能数据访问对象"""

    def get_algorithm_performance(self, algorithm_version: str = None) -> List[AlgorithmPerformance]:
        """获取算法性能数据"""
        query = "SELECT * FROM algorithm_performance"
        params = ()
        if algorithm_version:
            query += " WHERE algorithm_version = %s"
            params = (algorithm_version,)

        results = self.execute_query(query, params)
        performance_list = []
        for row in results:
            performance = AlgorithmPerformance(
                id=row['id'],
                algorithm_version=row['algorithm_version'],
                total_recommendations=row['total_recommendations'],
                total_periods_analyzed=row['total_periods_analyzed'],
                avg_front_hit_rate=float(row['avg_front_hit_rate']),
                avg_back_hit_rate=float(row['avg_back_hit_rate']),
                hit_distribution=json.loads(row['hit_distribution']) if row['hit_distribution'] else None,
                confidence_accuracy=float(row['confidence_accuracy']),
                risk_adjusted_return=float(row['risk_adjusted_return']),
                stability_score=float(row['stability_score']),
                consistency_rate=float(row['consistency_rate']),
                current_weight=float(row['current_weight']),
                weight_history=json.loads(row['weight_history']) if row['weight_history'] else None,
                performance_trend=row['performance_trend']
            )
            performance_list.append(performance)
        return performance_list

    def update_algorithm_performance(self, performance: AlgorithmPerformance) -> bool:
        """更新算法性能数据"""
        query = """
        INSERT INTO algorithm_performance (
            algorithm_version, total_recommendations, total_periods_analyzed,
            avg_front_hit_rate, avg_back_hit_rate, hit_distribution,
            confidence_accuracy, risk_adjusted_return, stability_score,
            consistency_rate, current_weight, weight_history, performance_trend
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_recommendations = VALUES(total_recommendations),
            total_periods_analyzed = VALUES(total_periods_analyzed),
            avg_front_hit_rate = VALUES(avg_front_hit_rate),
            avg_back_hit_rate = VALUES(avg_back_hit_rate),
            hit_distribution = VALUES(hit_distribution),
            confidence_accuracy = VALUES(confidence_accuracy),
            risk_adjusted_return = VALUES(risk_adjusted_return),
            stability_score = VALUES(stability_score),
            consistency_rate = VALUES(consistency_rate),
            current_weight = VALUES(current_weight),
            weight_history = VALUES(weight_history),
            performance_trend = VALUES(performance_trend)
        """
        params = (
            performance.algorithm_version,
            performance.total_recommendations,
            performance.total_periods_analyzed,
            performance.avg_front_hit_rate,
            performance.avg_back_hit_rate,
            json.dumps(performance.hit_distribution) if performance.hit_distribution else None,
            performance.confidence_accuracy,
            performance.risk_adjusted_return,
            performance.stability_score,
            performance.consistency_rate,
            performance.current_weight,
            json.dumps(performance.weight_history) if performance.weight_history else None,
            performance.performance_trend
        )
        return self.execute_update(query, params)