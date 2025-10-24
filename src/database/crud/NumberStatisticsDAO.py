from typing import List, Optional
import json
from ..AllDao import AllDAO
from src.model.lottery_models import NumberStatistics


class NumberStatisticsDAO(AllDAO):
    """号码统计数据访问对象"""

    def get_number_statistics(self, number: int = None, number_type: str = None) -> List[NumberStatistics]:
        """获取号码统计数据"""
        query = "SELECT * FROM number_statistics"
        conditions = []
        params = []

        if number is not None:
            conditions.append("number = %s")
            params.append(number)

        if number_type:
            conditions.append("number_type = %s")
            params.append(number_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        results = self.execute_query(query, tuple(params))
        stats_list = []
        for row in results:
            stats = NumberStatistics(
                number=row['number'],
                number_type=row['number_type'],
                total_appearances=row['total_appearances'],
                appearance_rate=float(row['appearance_rate']),
                recent_10_appearances=row['recent_10_appearances'],
                recent_20_appearances=row['recent_20_appearances'],
                recent_50_appearances=row['recent_50_appearances'],
                current_omission=row['current_omission'],
                max_omission=row['max_omission'],
                avg_omission=float(row['avg_omission']),
                heat_status=row['heat_status'],
                heat_score=float(row['heat_score']),
                strong_followers=json.loads(row['strong_followers']) if row['strong_followers'] else None,
                strong_precursors=json.loads(row['strong_precursors']) if row['strong_precursors'] else None,
                position_preference=json.loads(row['position_preference']) if row['position_preference'] else None
            )
            stats_list.append(stats)
        return stats_list

    def update_number_statistics(self, stats: NumberStatistics) -> bool:
        """更新号码统计数据"""
        query = """
        INSERT INTO number_statistics (
            number, number_type, total_appearances, appearance_rate,
            recent_10_appearances, recent_20_appearances, recent_50_appearances,
            current_omission, max_omission, avg_omission, heat_status,
            heat_score, strong_followers, strong_precursors, position_preference
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_appearances = VALUES(total_appearances),
            appearance_rate = VALUES(appearance_rate),
            recent_10_appearances = VALUES(recent_10_appearances),
            recent_20_appearances = VALUES(recent_20_appearances),
            recent_50_appearances = VALUES(recent_50_appearances),
            current_omission = VALUES(current_omission),
            max_omission = VALUES(max_omission),
            avg_omission = VALUES(avg_omission),
            heat_status = VALUES(heat_status),
            heat_score = VALUES(heat_score),
            strong_followers = VALUES(strong_followers),
            strong_precursors = VALUES(strong_precursors),
            position_preference = VALUES(position_preference)
        """
        params = (
            stats.number, stats.number_type, stats.total_appearances, stats.appearance_rate,
            stats.recent_10_appearances, stats.recent_20_appearances, stats.recent_50_appearances,
            stats.current_omission, stats.max_omission, stats.avg_omission, stats.heat_status,
            stats.heat_score,
            json.dumps(stats.strong_followers) if stats.strong_followers else None,
            json.dumps(stats.strong_precursors) if stats.strong_precursors else None,
            json.dumps(stats.position_preference) if stats.position_preference else None
        )
        return self.execute_update(query, params)