# src/database/database_manager.py
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import mysql.connector
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
    """统一数据库管理器（增强错误处理版本）"""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3309):
        self.connection_manager = DatabaseConnectionManager(host, user, password, database, port)
        self._connected = False
        self.last_insert_id = None

    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            dao = self.connection_manager.get_dao(LotteryHistoryDAO)
            self._connected = dao.connection and dao.connection.is_connected()
            return self._connected
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False

    def disconnect(self):
        """关闭数据库连接"""
        self.connection_manager.disconnect_all()
        self._connected = False

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected

    def get_dao(self, dao_class):
        """获取 DAO 实例"""
        return self.connection_manager.get_dao(dao_class)

    def get_config(self):
        """获取连接配置"""
        return self.connection_manager.connection_config

    def execute_query(self, query: str, params: tuple = None) -> list:
        """执行查询操作（增强版本）"""
        try:
            dao = self.connection_manager.get_dao(LotteryHistoryDAO)
            cursor = dao.connection.cursor(dictionary=True)

            # 打印调试信息
            print(f"[DEBUG] 执行查询: {query}")
            if params:
                print(f"[DEBUG] 参数: {params}")

            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except mysql.connector.Error as e:
            print(f"[DatabaseManager] MySQL错误: {e}")
            print(f"[DatabaseManager] SQL状态: {e.sqlstate}")
            return []
        except Exception as e:
            print(f"[DatabaseManager] 执行查询失败: {e}")
            return []

        # ... (在 class DatabaseManager: 的定义内部，可以放在 execute_query 方法的下面)

    def execute_insert(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
            """
            通用的插入方法，根据字典动态生成SQL语句。
            :param table_name: 要插入的表名
            :param data: 包含列名和值的字典
            :return: 插入记录的ID，如果失败则返回None
            """
            try:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                # 使用已有的 execute_update 方法来执行
                # 注意：这里假设 execute_update 返回 lastrowid
                return self.execute_update(sql, tuple(data.values()))
            except Exception as e:
                print(f"❌ 在 DatabaseManager 中执行通用插入失败: {e}")
                return None


    def execute_update(self, query: str, params: tuple = None) -> Optional[int]:
        """执行更新/插入语句（修改后版本）"""
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        # 直接调用底层的DAO方法，它已经能正确返回ID
        return dao.execute_update(query, params)

    def execute_batch_insert(self, query: str, params_list: List[tuple]) -> bool:
        """执行批量插入操作"""
        try:
            dao = self.connection_manager.get_dao(LotteryHistoryDAO)
            cursor = dao.connection.cursor()

            print(f"[DEBUG] 执行批量插入: {query}")
            print(f"[DEBUG] 参数数量: {len(params_list)}")

            cursor.executemany(query, params_list)
            dao.connection.commit()
            cursor.close()
            print(f"[DEBUG] 批量插入成功，影响行数: {cursor.rowcount}")
            return True
        except mysql.connector.Error as e:
            print(f"[DatabaseManager] MySQL批量插入错误: {e}")
            print(f"[DatabaseManager] SQL状态: {e.sqlstate}")
            dao.connection.rollback()
            return False
        except Exception as e:
            print(f"[DatabaseManager] 批量插入失败: {e}")
            dao.connection.rollback()
            return False

    # 其他方法保持不变...
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """获取所有结果"""
        return self.execute_query(query, params)

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """获取单条结果"""
        try:
            dao = self.connection_manager.get_dao(LotteryHistoryDAO)
            cursor = dao.connection.cursor(dictionary=True)

            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            print(f"[DatabaseManager] 获取单条结果失败: {e}")
            return None

    # LotteryHistory 相关方法
    def get_latest_lottery_history(self, limit: int = 50) -> List[LotteryHistory]:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_latest_lottery_history(limit)

    def get_lottery_history(self, limit: int = 100, offset: int = 0) -> List[LotteryHistory]:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_lottery_history(limit, offset)

    def get_all_lottery_history(self, limit: int = 200) -> List[LotteryHistory]:
        """获取所有历史数据（按时间正序）"""
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_lottery_history(limit, 0)

    def get_lottery_history_before_period(self, period_number: str, limit: int = 100) -> List[LotteryHistory]:
        """获取指定期号之前的历史数据"""
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_lottery_history_before_period(period_number, limit)

    def insert_lottery_history(self, history: LotteryHistory) -> bool:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.insert_lottery_history(history)

    def get_next_period_number(self) -> str:
        dao = self.connection_manager.get_dao(LotteryHistoryDAO)
        return dao.get_next_period_number()

    # 其他原有方法保持不变...
    # AlgorithmRecommendation 相关方法
    # def insert_algorithm_recommendation_root(self, period_number, recommend_time, algorithm_version,
    #                                          algorithm_parameters=None, model_weights=None,
    #                                          confidence_score=0.8, risk_level='medium',
    #                                          analysis_basis=None, key_patterns=None,
    #                                          models=None):  # <--- 1. 添加 models 参数
    #     """插入算法推荐主记录 - 增强版"""
    #     query = """
    #     INSERT INTO algorithm_recommendation
    #     (period_number, recommend_time, algorithm_version, algorithm_parameters,
    #      model_weights, confidence_score, risk_level, analysis_basis, key_patterns, models, created_at) -- <--- 2. 在SQL中添加 models 列
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     """
    #
    #     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #
    #     algo_params = json.dumps(algorithm_parameters, ensure_ascii=False) if algorithm_parameters else '{}'
    #     weights = json.dumps(model_weights, ensure_ascii=False) if model_weights else '{}'
    #     basis = json.dumps(analysis_basis, ensure_ascii=False) if analysis_basis else '{}'
    #     patterns = json.dumps(key_patterns, ensure_ascii=False) if key_patterns else '[]'
    #
    #     # 使用 self.execute_insert, 这是我们在错误1中添加的新方法
    #     data_to_insert = {
    #         'period_number': period_number,
    #         'recommend_time': current_time,
    #         'algorithm_version': algorithm_version,
    #         'algorithm_parameters': algo_params,
    #         'model_weights': weights,
    #         'confidence_score': confidence_score,
    #         'risk_level': risk_level,
    #         'analysis_basis': basis,
    #         'key_patterns': patterns,
    #         'models': models,  # <--- 3. 将 models 值加入
    #         'created_at': current_time
    #     }
    #
    #     # 使用新添加的通用插入方法
    #     return self.execute_insert('algorithm_recommendation', data_to_insert)
    def insert_algorithm_recommendation_root(self, **kwargs: Any) -> Optional[int]:
        """
        使用通用插入方法来插入算法推荐主记录 (V12 - 最终灵活版)。
        这个版本使用 **kwargs 来灵活接收所有字段，与 main.py 的调用完全匹配。
        """
        # 自动添加时间戳，如果调用时没有提供
        if 'recommend_time' not in kwargs:
            kwargs['recommend_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # main.py 已经将复杂的字段转换为了JSON字符串，这里直接调用即可
        # 直接调用我们已经修复好的、可靠的通用插入方法
        return self.execute_insert('algorithm_recommendation', kwargs)

    def insert_algorithm_recommendation(self, recommendation: AlgorithmRecommendation) -> Optional[int]:
        """插入算法推荐记录，返回插入的ID"""
        dao = self.connection_manager.get_dao(AlgorithmRecommendationDAO)
        return dao.insert_algorithm_recommendation(recommendation)

    def get_recommendation_by_period(self, period_number: str) -> Optional[AlgorithmRecommendation]:
        dao = self.connection_manager.get_dao(AlgorithmRecommendationDAO)
        return dao.get_recommendation_by_period(period_number)

    def insert_algorithm_performance(self,
                                     algorithm_id: str,
                                     algorithm_version: str,
                                     period_number: str,
                                     predicted_numbers: str,
                                     confidence_score: float,
                                     actual_numbers: str = None,
                                     is_correct: bool = None,
                                     performance_metrics: str = None) -> bool:
        """插入算法性能记录"""
        try:
            prediction_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = """
                INSERT INTO algorithm_performance 
                (algorithm_id, algorithm_version, period_number, prediction_time, 
                 predicted_numbers, confidence_score, actual_numbers, is_correct, performance_metrics)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                algorithm_id,
                algorithm_version,
                period_number,
                prediction_time,
                predicted_numbers,
                confidence_score,
                actual_numbers,
                is_correct,
                performance_metrics
            )

            result = self.execute_insert(query, params)
            return result is not None
        except Exception as e:
            print(f"[DatabaseManager] 插入算法性能记录失败: {e}")
            return False
    def get_last_insert_id(self) -> int:
        """返回上一次 INSERT 操作生成的自增 ID"""
        return self.last_insert_id

    def get_algorithm_performance(self, algorithm_version: str = None) -> List[AlgorithmPerformance]:
        """获取算法性能数据（兼容原有接口）"""
        try:
            # 使用原始的 DAO 方法
            dao = self.connection_manager.get_dao(AlgorithmPerformanceDAO)
            return dao.get_algorithm_performance(algorithm_version)
        except Exception as e:
            print(f"[DatabaseManager] 获取算法性能数据失败: {e}")
            # 降级处理：返回空列表
            return []

    def update_algorithm_performance_result(self,
                                            algorithm_id: str,
                                            period_number: str,
                                            actual_numbers: str,
                                            is_correct: bool,
                                            performance_metrics: str) -> bool:
        """更新算法性能结果（开奖后）"""
        try:
            query = """
                UPDATE algorithm_performance 
                SET actual_numbers = %s, is_correct = %s, performance_metrics = %s
                WHERE algorithm_id = %s AND period_number = %s
            """
            params = (actual_numbers, is_correct, performance_metrics, algorithm_id, period_number)

            return self.execute_update(query, params)
        except Exception as e:
            print(f"[DatabaseManager] 更新算法性能结果失败: {e}")
            return False



    @staticmethod
    def parse_ai_recommendations(response_content: str) -> List[Dict]:
        """解析AI返回的推荐内容"""
        return AlgorithmRecommendationDAO.parse_ai_recommendations(response_content)

    def insert_recommendation_details_batch(self, root_id: int, details_list: list) -> bool:
        """批量插入推荐详情"""
        try:
            if not details_list:
                return True

            query = """
                INSERT INTO recommendation_details 
                (recommendation_metadata_id, recommend_type, strategy_logic, 
                 front_numbers, back_numbers, win_probability)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            # 使用 RecommendationDetailsDAO 来获取连接
            dao = self.connection_manager.get_dao(RecommendationDetailsDAO)
            cursor = dao.connection.cursor()

            for detail in details_list:
                params = (
                    root_id,
                    detail.get("recommend_type", "Unknown"),
                    detail.get("strategy_logic", ""),
                    detail.get("front_numbers", ""),
                    detail.get("back_numbers", ""),
                    detail.get("win_probability", 0.0)
                )
                cursor.execute(query, params)

            dao.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"[DatabaseManager] 批量插入推荐详情失败: {e}")
            dao.connection.rollback()
            return False