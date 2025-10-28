# src/database/crud/algorithm_performance_dao.py (Refactored Professional Version)

import pymysql
from datetime import datetime
from typing import Dict, Any, List, Optional

# 我们现在导入 DatabaseManager，让它来处理所有连接
from src.database.database_manager import DatabaseManager


class AlgorithmPerformanceDAO:
    """DAO for algorithm_performance table, using a central DatabaseManager."""

    def __init__(self, db_manager: DatabaseManager):
        """
        初始化DAO，并注入一个已经连接好的DatabaseManager实例。
        """
        self.db = db_manager
        # 在初始化时，我们仍然确保表存在
        self._ensure_table()

    def _ensure_table(self):
        """Ensures the performance table exists."""
        sql = """
        CREATE TABLE IF NOT EXISTS algorithm_performance (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            issue VARCHAR(32) NOT NULL,
            algorithm VARCHAR(128) NOT NULL,
            hits FLOAT DEFAULT 0,
            hit_rate FLOAT DEFAULT 0,
            score FLOAT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_issue_algo (issue, algorithm)
        ) CHARACTER SET utf8mb4;
        """
        # 使用注入的db_manager来执行SQL
        self.db.execute_update(sql)

    def insert_or_update(self, issue: str, algorithm: str, hits: float, hit_rate: float, score: float):
        """Inserts or updates an algorithm's performance for a specific issue."""
        sql = """
        INSERT INTO algorithm_performance (issue, algorithm, hits, hit_rate, score)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE hits=%s, hit_rate=%s, score=%s
        """
        params = (issue, algorithm, hits, hit_rate, score, hits, hit_rate, score)
        self.db.execute_update(sql, params)

    def get_average_scores_last_n_issues(self, n_issues: int = 5) -> Dict[str, float]:
        """
        Calculates the average score for each algorithm over the last N distinct issues.
        """
        # 1. Get the last N distinct issues
        sql_issues = "SELECT DISTINCT issue FROM algorithm_performance ORDER BY issue DESC LIMIT %s"
        issues_result = self.db.execute_query(sql_issues, (n_issues,))

        if not issues_result:
            return {}

        issues = [row['issue'] for row in issues_result]

        # 2. Calculate the average score for these issues
        format_issues = ",".join(["%s"] * len(issues))
        sql_avg = f"""
        SELECT algorithm, AVG(score) as avg_score FROM algorithm_performance
        WHERE issue IN ({format_issues})
        GROUP BY algorithm
        """
        avg_scores_result = self.db.execute_query(sql_avg, tuple(issues))

        return {row['algorithm']: float(row['avg_score']) for row in avg_scores_result} if avg_scores_result else {}