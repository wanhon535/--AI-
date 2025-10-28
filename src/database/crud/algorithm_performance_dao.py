# file: src/database/crud/algorithm_performance_dao.py
from typing import Dict, Any, List, Optional
from src.database.AllDao import AllDAO

class AlgorithmPerformanceDAO(AllDAO):
    """算法性能数据访问层"""

    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        self.table_name = "algorithm_performance"

    def insert_or_update(self, issue: str, algorithm: str, hits: float, hit_rate: float, score: float):
        """插入或更新算法性能数据"""
        query = f"""
        INSERT INTO {self.table_name} (issue, algorithm, hits, hit_rate, score, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            hits=VALUES(hits), hit_rate=VALUES(hit_rate),
            score=VALUES(score), updated_at=NOW();
        """
        self.execute_update(query, (issue, algorithm, hits, hit_rate, score))

    def get_algorithm_performance(self, algorithm_version: str = None) -> List[Dict[str, Any]]:
        """查询算法性能"""
        if algorithm_version:
            query = f"SELECT * FROM {self.table_name} WHERE algorithm=%s ORDER BY issue DESC LIMIT 50"
            return self.execute_query(query, (algorithm_version,))
        else:
            query = f"SELECT * FROM {self.table_name} ORDER BY issue DESC LIMIT 50"
            return self.execute_query(query)

    def update_algorithm_performance(self, perf_obj):
        """更新算法性能对象（对象方式）"""
        query = f"""
        UPDATE {self.table_name}
        SET score=%s, hit_rate=%s, hits=%s, updated_at=NOW()
        WHERE algorithm=%s
        """
        self.execute_update(query, (perf_obj.confidence_accuracy, perf_obj.avg_front_hit_rate,
                                    perf_obj.total_recommendations, perf_obj.algorithm_version))

    def get_average_scores_last_n_issues(self, n_issues: int = 5) -> Dict[str, float]:
        """计算最近 n 期平均得分"""
        sql_issues = "SELECT DISTINCT issue FROM algorithm_performance ORDER BY issue DESC LIMIT %s"
        issues_result = self.execute_query(sql_issues, (n_issues,))
        if not issues_result:
            return {}

        issues = [row['issue'] for row in issues_result]
        format_issues = ",".join(["%s"] * len(issues))
        sql_avg = f"""
            SELECT algorithm, AVG(score) AS avg_score
            FROM algorithm_performance
            WHERE issue IN ({format_issues})
            GROUP BY algorithm
        """
        avg_scores_result = self.execute_query(sql_avg, tuple(issues))
        return {r['algorithm']: float(r['avg_score']) for r in avg_scores_result} if avg_scores_result else {}

