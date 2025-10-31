# file: src/database/crud/algorithm_performance_dao.py
from typing import Dict, Any, List, Optional
from src.database.AllDao import AllDAO

class AlgorithmPerformanceDAO(AllDAO):
    """算法性能数据访问层"""

    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        self.table_name = "algorithm_performance"

    def insert_algorithm_performance(self,
                                     algorithm: str,
                                     issue: str,
                                     hits: float = 0,
                                     hit_rate: float = 0,
                                     score: float = 0) -> bool:
        """插入算法性能记录 - 基于实际表结构"""
        try:
            query = """
                INSERT INTO algorithm_performance 
                (algorithm, issue, hits, hit_rate, score, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            params = (algorithm, issue, hits, hit_rate, score)

            result = self.execute_insert(query, params)
            return result is not None
        except Exception as e:
            print(f"[DatabaseManager] 插入算法性能记录失败: {e}")
            return False

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

    def update_algorithm_performance(self,
                                     algorithm: str,
                                     issue: str,
                                     hits: float = None,
                                     hit_rate: float = None,
                                     score: float = None) -> bool:
        """更新算法性能记录"""
        try:
            update_fields = []
            params = []

            if hits is not None:
                update_fields.append("hits = %s")
                params.append(hits)
            if hit_rate is not None:
                update_fields.append("hit_rate = %s")
                params.append(hit_rate)
            if score is not None:
                update_fields.append("score = %s")
                params.append(score)

            if not update_fields:
                return True

            params.extend([algorithm, issue])

            query = f"""
                UPDATE algorithm_performance 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE algorithm = %s AND issue = %s
            """

            return self.execute_update(query, params)
        except Exception as e:
            print(f"[DatabaseManager] 更新算法性能记录失败: {e}")
            return False

    def get_algorithm_performance_history(self, algorithm: str = None, limit: int = 50) -> List[Dict]:
        """获取算法性能历史数据"""
        try:
            if algorithm:
                query = """
                    SELECT * FROM algorithm_performance 
                    WHERE algorithm = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """
                params = (algorithm, limit)
            else:
                query = """
                    SELECT * FROM algorithm_performance 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """
                params = (limit,)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"[DatabaseManager] 获取算法性能历史数据失败: {e}")
            return []

    def get_average_scores_last_n_issues(self, n_issues: int = 5) -> Dict[str, float]:
        """计算最近 n 期平均得分 (修复了SQL兼容性问题)"""
        # 步骤1: 先找到最近N期的期号
        issues_query = "SELECT DISTINCT period_number FROM algorithm_performance ORDER BY period_number DESC LIMIT %s"
        issues_result = self.execute_query(issues_query, (n_issues,))

        if not issues_result:
            return {}

        issues = [row['period_number'] for row in issues_result]

        # 步骤2: 基于这些期号计算平均分
        # 使用 IN (...) 语法，这是兼容的
        format_strings = ','.join(['%s'] * len(issues))
        avg_query = f"""
            SELECT algorithm_version, AVG(confidence_score) AS avg_score
            FROM algorithm_performance
            WHERE period_number IN ({format_strings})
            GROUP BY algorithm_version
        """

        avg_scores_result = self.execute_query(avg_query, tuple(issues))
        return {r['algorithm_version']: float(r['avg_score']) for r in avg_scores_result} if avg_scores_result else {}
