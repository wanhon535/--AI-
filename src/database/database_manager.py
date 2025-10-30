# src/database/database_manager.py
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from .connection_manager import DatabaseConnectionManager
from src.database.crud.lottery_history_dao import LotteryHistoryDAO
from src.database.crud.algorithm_recommendation_dao import AlgorithmRecommendationDAO
from src.database.crud.recommendation_details_dao import RecommendationDetailsDAO
from src.database.crud.user_purchase_dao import UserPurchaseDAO
from src.database.crud.personal_betting_dao import PersonalBettingDAO
from src.database.crud.AlgorithmConfigDAO import AlgorithmConfigDAO
from src.database.crud.AlgorithmPerformanceDAO import AlgorithmPerformanceDAO
from src.database.crud.NumberStatisticsDAO import NumberStatisticsDAO
from src.model.lottery_models import (
    LotteryHistory, NumberStatistics, AlgorithmConfig,
    AlgorithmPerformance, AlgorithmRecommendation,
    PersonalBetting, RecommendationDetail, UserPurchaseRecord
)


class DatabaseManager:
    """统一数据库管理器（兼容原有接口）"""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3309):
        self.connection_manager = DatabaseConnectionManager(host, user, password, database, port)
        self._connected = False

    def get_dao(self, dao_class):
        """兼容接口：直接从 connection_manager 获取 DAO"""
        return self.connection_manager.get_dao(dao_class)


    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            # 通过获取一个DAO来触发连接
            dao = self.connection_manager.get_dao(LotteryHistoryDAO)
            self._connected = dao.connection and dao.connection.is_connected()
            return self._connected
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute(self, query, params=None, commit=True):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        if commit:
            self.connection.commit()
        cursor.close()

    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        cursor.close()
        return result

    def disconnect(self):
        """关闭数据库连接"""
        self.connection_manager.disconnect_all()
        self._connected = False

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询语句（兼容原有接口）"""
        # 使用LotteryHistoryDAO来执行通用查询
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.execute_query(query, params)

    def get_last_insert_id(self) -> int:
        """
        返回上一次 INSERT 操作生成的自增 ID。
        """
        return self.last_insert_id

    def get_config(self):
        return self.connection_manager.connection_config

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """执行更新语句（兼容原有接口）"""
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.execute_update(query, params)

    # LotteryHistory 相关方法
    def get_latest_lottery_history(self, limit: int = 50) -> List[LotteryHistory]:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_latest_lottery_history(limit)

    def get_lottery_history(self, limit: int = 100, offset: int = 0) -> List[LotteryHistory]:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_lottery_history(limit, offset)

    def insert_lottery_history(self, history: LotteryHistory) -> bool:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.insert_lottery_history(history)

    def get_next_period_number(self) -> str:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_next_period_number()

    # AlgorithmRecommendation 相关方法 - 修复返回ID
    def insert_algorithm_recommendation_root(self, period_number: str, algorithm_version: str,
                                             confidence_score: float, risk_level: str,
                                             analysis_basis: Optional[str] = None) -> Optional[int]:
        """插入算法推荐根记录，返回插入的ID"""
        dao = self.connection_manager.get_dao(AlgorithmRecommendationDAO)
        return dao.insert_algorithm_recommendation_root(
            period_number,
            algorithm_version,
            confidence_score,
            risk_level,
            analysis_basis
        )

    def insert_algorithm_recommendation(self, recommendation: AlgorithmRecommendation) -> Optional[int]:
        """插入算法推荐记录，返回插入的ID"""
        dao = self.connection_manager.get_dao(AlgorithmRecommendationDAO)
        return dao.insert_algorithm_recommendation(recommendation)

    def get_recommendation_by_period(self, period_number: str) -> Optional[AlgorithmRecommendation]:
        dao = self.connection_manager.get_dao(AlgorithmRecommendationDAO)
        return dao.get_recommendation_by_period(period_number)

    # RecommendationDetails 相关方法
    def insert_recommendation_details_batch(self, recommendation_id: int, details: List[Dict]) -> bool:
        dao = self.connection_manager.get_dao(RecommendationDetailsDAO)
        return dao.insert_recommendation_details_batch(recommendation_id, details)

    def insert_recommendation_detail(self, detail: RecommendationDetail) -> bool:
        dao = self.connection_manager.get_dao(RecommendationDetailsDAO)
        return dao.insert_recommendation_detail(detail)

    def get_recommendation_details(self, recommendation_id: int) -> List[RecommendationDetail]:
        dao = self.connection_manager.get_dao(RecommendationDetailsDAO)
        return dao.get_recommendation_details(recommendation_id)

    # UserPurchase 相关方法
    def insert_user_purchase_records_batch(self, period_metadata_id: int, purchases: List[Dict]) -> bool:
        dao = self.connection_manager.get_dao(UserPurchaseDAO)
        return dao.insert_user_purchase_records_batch(period_metadata_id, purchases)

    def insert_user_purchase_record(self, record: UserPurchaseRecord) -> bool:
        dao = self.connection_manager.get_dao(UserPurchaseDAO)
        return dao.insert_user_purchase_record(record)

    def get_user_purchase_records(self, period_metadata_id: int) -> List[UserPurchaseRecord]:
        dao = self.connection_manager.get_dao(UserPurchaseDAO)
        return dao.get_user_purchase_records(period_metadata_id)

    # PersonalBetting 相关方法
    def get_user_bets(self, user_id: str = 'default', limit: int = 20) -> List[PersonalBetting]:
        dao = self.connection_manager.get_dao(PersonalBettingDAO)
        return dao.get_user_bets(user_id, limit)

    # AlgorithmConfig 相关方法
    def get_algorithm_configs(self, is_active: bool = True) -> List[AlgorithmConfig]:
        dao = self.connection_manager.get_dao(AlgorithmConfigDAO)
        return dao.get_algorithm_configs(is_active)

    def get_default_algorithm_config(self) -> Optional[AlgorithmConfig]:
        dao = self.connection_manager.get_dao(AlgorithmConfigDAO)
        return dao.get_default_config()

    # AlgorithmPerformance 相关方法
    def get_algorithm_performance(self, algorithm_version: str = None) -> List[AlgorithmPerformance]:
        dao = self.connection_manager.get_dao(AlgorithmPerformanceDAO)
        return dao.get_algorithm_performance(algorithm_version)

    def update_algorithm_performance(self, performance: AlgorithmPerformance) -> bool:
        dao = self.connection_manager.get_dao(AlgorithmPerformanceDAO)
        return dao.update_algorithm_performance(performance)

    # NumberStatistics 相关方法
    def get_number_statistics(self, number: int = None, number_type: str = None) -> List[NumberStatistics]:
        dao = self.connection_manager.get_dao(NumberStatisticsDAO)
        return dao.get_number_statistics(number, number_type)

    def update_number_statistics(self, stats: NumberStatistics) -> bool:
        dao = self.connection_manager.get_dao(NumberStatisticsDAO)
        return dao.update_number_statistics(stats)

    # 工具方法
    @staticmethod
    def parse_ai_recommendations(response_content: str) -> List[Dict]:
        """解析AI返回的推荐内容"""
        return AlgorithmRecommendationDAO.parse_ai_recommendations(response_content)