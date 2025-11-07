# src/database/crud/reward_penalty_records_dao.py
from typing import List, Dict, Any, Optional
from src.database.connection_manager import DatabaseConnectionManager
import json
from datetime import datetime


class RewardPenaltyRecordsDAO:
    """奖罚记录数据访问对象"""

    def __init__(self):
        self.connection_manager = DatabaseConnectionManager()

    def create(self, record_data: Dict[str, Any]) -> int:
        """创建奖罚记录"""
        query = """
        INSERT INTO reward_penalty_records 
        (period_number, algorithm_version, recommendation_id, front_hit_count, 
         back_hit_count, hit_score, reward_points, penalty_points, net_points,
         performance_rating, hit_details, evaluation_time) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            record_data['period_number'],
            record_data['algorithm_version'],
            record_data.get('recommendation_id'),
            record_data['front_hit_count'],
            record_data['back_hit_count'],
            record_data['hit_score'],
            record_data['reward_points'],
            record_data['penalty_points'],
            record_data['net_points'],
            record_data['performance_rating'],
            record_data.get('hit_details'),
            record_data.get('evaluation_time', datetime.now())
        )

        return self.connection_manager.execute_insert(query, params)

    def get_by_period_and_recommendation(self, period_number: str, recommendation_id: int) -> Optional[Dict[str, Any]]:
        """根据期号和推荐ID获取奖罚记录"""
        query = """
        SELECT * FROM reward_penalty_records 
        WHERE period_number = %s AND recommendation_id = %s
        """

        results = self.connection_manager.execute_query(query, (period_number, recommendation_id))
        return results[0] if results else None

    def get_by_period(self, period_number: str) -> List[Dict[str, Any]]:
        """根据期号获取奖罚记录"""
        query = "SELECT * FROM reward_penalty_records WHERE period_number = %s"
        return self.connection_manager.execute_query(query, (period_number,))

    def get_by_algorithm_version(self, algorithm_version: str, limit: int = 100) -> List[Dict[str, Any]]:
        """根据算法版本获取奖罚记录"""
        query = "SELECT * FROM reward_penalty_records WHERE algorithm_version = %s ORDER BY evaluation_time DESC LIMIT %s"
        return self.connection_manager.execute_query(query, (algorithm_version, limit))

    def get_performance_stats(self, algorithm_version: str = None) -> Dict[str, Any]:
        """获取性能统计"""
        if algorithm_version:
            query = """
            SELECT 
                COUNT(*) as total_records,
                AVG(hit_score) as avg_hit_score,
                AVG(net_points) as avg_net_points,
                SUM(CASE WHEN hit_score > 0 THEN 1 ELSE 0 END) as winning_records,
                AVG(front_hit_count) as avg_front_hits,
                AVG(back_hit_count) as avg_back_hits
            FROM reward_penalty_records 
            WHERE algorithm_version = %s
            """
            results = self.connection_manager.execute_query(query, (algorithm_version,))
        else:
            query = """
            SELECT 
                COUNT(*) as total_records,
                AVG(hit_score) as avg_hit_score,
                AVG(net_points) as avg_net_points,
                SUM(CASE WHEN hit_score > 0 THEN 1 ELSE 0 END) as winning_records,
                AVG(front_hit_count) as avg_front_hits,
                AVG(back_hit_count) as avg_back_hits
            FROM reward_penalty_records
            """
            results = self.connection_manager.execute_query(query)

        return results[0] if results else {}

    def get_recent_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近的奖罚记录"""
        query = "SELECT * FROM reward_penalty_records ORDER BY evaluation_time DESC LIMIT %s"
        return self.connection_manager.execute_query(query, (limit,))

    def delete_by_period(self, period_number: str) -> int:
        """删除指定期号的记录"""
        query = "DELETE FROM reward_penalty_records WHERE period_number = %s"
        return self.connection_manager.execute_update(query, (period_number,))