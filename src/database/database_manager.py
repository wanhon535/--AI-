# file: src/database/database_manager.py (安全、完整、已修复超时和乱码问题的最终版)

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import mysql.connector
from mysql.connector import pooling
import logging

# 导入您项目中定义的模型类，确保所有函数的返回类型提示正确
from src.model.lottery_models import (
    LotteryHistory, NumberStatistics, AlgorithmConfig,
    AlgorithmPerformance, AlgorithmRecommendation,
    PersonalBetting, RecommendationDetail, UserPurchaseRecord
)

# 配置日志，这比使用print()更专业
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [DatabaseManager] %(message)s')


class DatabaseManager:
    """
    统一数据库管理器 (已升级为连接池模式)。
    - 完全保留了项目原有的所有方法和接口。
    - 内部实现已替换为健壮的数据库连接池，解决了连接超时和乱码问题。
    """
    _connection_pool = None

    def __init__(self, **db_config: Any):
        """
        构造函数。在第一次实例化时，会创建并初始化一个全局的数据库连接池。
        """
        if not all(key in db_config for key in ['host', 'user', 'password', 'database', 'port']):
            raise ValueError("数据库配置字典缺少必要的键。")
        self.db_config = db_config.copy()

        # 使用单例模式确保连接池只被创建一次
        if not DatabaseManager._connection_pool:
            try:
                logging.info("正在初始化数据库连接池...")
                # 强制指定字符集以解决乱码问题
                db_config['charset'] = 'utf8mb4'


                DatabaseManager._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="lotto_pool",
                    pool_size=10,  # 增加池大小以应对可能的并发
                    pool_reset_session=True,
                    **db_config
                )
                logging.info("数据库连接池初始化成功。")
            except mysql.connector.Error as err:
                logging.error(f"创建连接池失败: {err}")
                DatabaseManager._connection_pool = None

        self.last_insert_id = None  # 保留您原有的属性

        # =================================================================================
        # --- 请用此版本完整替换 get_current_time 方法 ---
        # =================================================================================
    def get_current_time(self):  # Type hint removed temporarily for maximum compatibility
            """
            获取数据库服务器的当前时间 (V3 - 最终健壮版)。
            返回一个可被数据库驱动直接使用的 datetime 对象。
            """
            # <<< 关键：在方法开头就导入，避免在except块中产生歧义 >>>
            from datetime import datetime

            try:
                # 使用最通用的SQL标准
                query = "SELECT CURRENT_TIMESTAMP AS db_time"
                result = self.fetch_one(query)

                if result and 'db_time' in result and isinstance(result['db_time'], datetime):
                    # 确认返回的是一个 datetime 对象
                    return result['db_time']
                else:
                    # 如果查询失败或返回类型不正确，则回退到系统本地时间
                    logging.warning("获取数据库时间失败或返回类型不正确，回退到系统本地时间。")
                    return datetime.now()
            except Exception as e:
                logging.error(f"获取数据库当前时间时发生异常: {e}, 回退到系统本地时间。")
                return datetime.now()

    def _get_connection(self):
        """内部方法：从连接池获取一个连接。"""
        if not self._connection_pool:
            logging.error("连接池不可用，无法获取连接。")
            return None
        try:
            return self._connection_pool.get_connection()
        except mysql.connector.Error as err:
            logging.error(f"从连接池获取连接失败: {err}")
            return None

    # --- 兼容旧代码的核心方法 ---

    def connect(self) -> bool:
        """
        (兼容性方法) 检查连接池是否可用。
        在连接池模式下，不需要显式连接，但保留此方法以兼容旧代码。
        """
        return DatabaseManager._connection_pool is not None

    def disconnect(self):
        """
        (兼容性方法) 在连接池模式下，此方法无需执行任何操作。
        连接的归还由每个执行方法自动处理。
        """
        pass  # 连接池会自动管理连接，无需手动断开

    def is_connected(self) -> bool:
        """(兼容性方法) 检查连接池是否就绪。"""
        return self.connect()

    def get_dao(self, dao_class):
        """(兼容性方法) 不再需要DAO，但为了不让调用它的代码报错，返回self。"""
        logging.warning(f"调用了已废弃的 get_dao 方法 ({dao_class.__name__})。数据库操作现在由DatabaseManager直接处理。")
        return self

    # --- 底层数据执行方法 ---

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行SELECT查询并返回所有结果（作为字典列表）。"""
        logging.debug(f"执行查询: {query} | 参数: {params}")
        conn = self._get_connection()
        if not conn: return []

        results = []
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f"查询执行失败: {err.msg} | SQL: {query}")
        finally:
            if conn: conn.close()
        return results

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """执行SELECT查询并返回第一条结果（作为字典）。"""
        logging.debug(f"执行单条查询: {query} | 参数: {params}")
        conn = self._get_connection()
        if not conn: return None

        result = None
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchone()
        except mysql.connector.Error as err:
            logging.error(f"单条查询执行失败: {err.msg} | SQL: {query}")
        finally:
            if conn: conn.close()
        return result

    def execute_update(self, query: str, params: tuple = None) -> Optional[int]:
        """
        执行INSERT, UPDATE, DELETE操作。
        返回新插入行的自增ID或受影响的行数。
        """
        logging.debug(f"执行更新: {query} | 参数: {params}")
        conn = self._get_connection()
        if not conn: return None

        result_id = None
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                # 更新 last_insert_id 属性，以兼容 get_last_insert_id()
                self.last_insert_id = cursor.lastrowid
                result_id = cursor.lastrowid or cursor.rowcount
        except mysql.connector.Error as err:
            logging.error(f"更新操作失败: {err.msg} | SQL: {query}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
        return result_id

    def delete_recommendations_by_period_and_model_base(self, period_number: str, model_base_name: str) -> int:
        """
        [CRITICAL ADDITION FOR ATOMICITY]
        Deletes all recommendation records for a given period that match a model's base name.
        Uses LIKE to catch all stages (e.g., 'qwen-max_Strategy_A', 'qwen-max_Strategy_B', etc.).
        Returns the number of deleted rows.
        """
        # The '%' is a wildcard character for the LIKE operator
        model_pattern = f"{model_base_name}%"
        query = "DELETE FROM algorithm_recommendation WHERE period_number = %s AND models LIKE %s"

        # We use execute_update as it handles write operations and returns affected rows
        deleted_rows = self.execute_update(query, (period_number, model_pattern))
        return deleted_rows if deleted_rows is not None else 0

    def get_recommendation_by_period_and_model(self, period_number: str, model_identifier: str) -> Optional[
        Dict[str, Any]]:
        """
        [NEW & SAFE] Specifically queries for a recommendation record based on the
        period and the unique model identifier (e.g., 'qwen-max_Strategy_A').
        """
        query = "SELECT * FROM algorithm_recommendation WHERE period_number = %s AND models = %s LIMIT 1"
        return self.fetch_one(query, (period_number, model_identifier))

    def delete_recommendations_by_period_and_model_base(self, period_number: str, model_base_name: str) -> int:
        """
        [NEW & SAFE] Deletes all recommendation records for a given period that match
        a model's base name (e.g., 'qwen-max'). This is for cleaning up partial runs.
        """
        model_pattern = f"{model_base_name}%"
        query = "DELETE FROM algorithm_recommendation WHERE period_number = %s AND models LIKE %s"
        deleted_rows = self.execute_update(query, (period_number, model_pattern))

        # Your execute_update returns the count, which is perfect.
        # Log the action for clarity.
        if deleted_rows and deleted_rows > 0:
            logging.info(
                f"Cleaned up {deleted_rows} stale records for model '{model_base_name}' in period {period_number}.")

        return deleted_rows if deleted_rows is not None else 0

    def execute_insert(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
        """通用的插入方法，根据字典动态生成SQL语句。"""
        columns = ', '.join(f"`{k}`" for k in data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_update(sql, tuple(data.values()))

    def execute_batch_insert(self, query: str, params_list: List[tuple]) -> bool:
        """执行批量插入操作。"""
        logging.debug(f"执行批量插入: {query} | 记录数: {len(params_list)}")
        conn = self._get_connection()
        if not conn or not params_list: return False

        success = False
        try:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()
                logging.info(f"批量插入成功，影响行数: {cursor.rowcount}")
                success = True
        except mysql.connector.Error as err:
            logging.error(f"批量插入失败: {err.msg} | SQL: {query}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
        return success

    def get_last_insert_id(self) -> Optional[int]:
        """返回上一次 INSERT 操作生成的自增 ID。"""
        return self.last_insert_id

    # --- 保留所有原有的高级功能方法 ---

    def _convert_rows_to_history_list(self, rows: List[dict]) -> List[LotteryHistory]:
        """
        【核心修复】将从数据库查询出的字典行列表，安全地转换为 LotteryHistory 对象列表。
        这个方法会处理字段合并和JSON解析。
        """
        results = []
        if not rows:
            return results

        for row in rows:
            try:
                # 1. 准备构造函数需要的参数字典
                init_params = row.copy()  # 复制所有匹配的字段

                # 2. 【关键】合并独立的号码字段为一个列表
                init_params['front_area'] = [
                    row.get('front_area_1'), row.get('front_area_2'),
                    row.get('front_area_3'), row.get('front_area_4'), row.get('front_area_5')
                ]
                init_params['back_area'] = [row.get('back_area_1'), row.get('back_area_2')]

                # 3. 安全地解析JSON字段
                consecutive_str = row.get('consecutive_numbers')
                if isinstance(consecutive_str, str):
                    init_params['consecutive_numbers'] = json.loads(consecutive_str)

                tail_str = row.get('tail_numbers')
                if isinstance(tail_str, str):
                    init_params['tail_numbers'] = json.loads(tail_str)

                # 4. 使用准备好的参数字典来创建对象
                results.append(LotteryHistory(**init_params))

            except (json.JSONDecodeError, TypeError, KeyError) as e:
                logging.warning(f"解析或转换期号 {row.get('period_number')} 的数据时出错: {e}。该条记录将被跳过。")
                continue
        return results

    # LotteryHistory 相关方法
    def get_latest_lottery_history(self, limit: int = 50) -> List[LotteryHistory]:
        query = "SELECT * FROM lottery_history ORDER BY period_number DESC LIMIT %s"
        results_raw = self.execute_query(query, (limit,))
        return self._convert_rows_to_history_list(results_raw)

    def get_lottery_history(self, limit: int = 100, offset: int = 0) -> List[LotteryHistory]:
        query = "SELECT * FROM lottery_history ORDER BY period_number ASC LIMIT %s OFFSET %s"
        results_raw = self.execute_query(query, (limit, offset))
        return self._convert_rows_to_history_list(results_raw)

    def get_all_lottery_history(self, limit: int = 200) -> List[LotteryHistory]:
        return self.get_lottery_history(limit, 0)

    def get_lottery_history_before_period(self, period_number: str, limit: int = 100) -> List[LotteryHistory]:
        query = "SELECT * FROM lottery_history WHERE period_number < %s ORDER BY period_number DESC LIMIT %s"
        results_raw = self.execute_query(query, (period_number, limit))
        return self._convert_rows_to_history_list(results_raw)

    def insert_lottery_history(self, history: LotteryHistory) -> bool:
        # 假设 LotteryHistory 对象可以被转换为字典
        data = history.dict() if hasattr(history, 'dict') else vars(history)
        result_id = self.execute_insert('lottery_history', data)
        return result_id is not None

    def get_next_period_number(self) -> str:
        query = "SELECT period_number FROM lottery_history ORDER BY period_number DESC LIMIT 1"
        latest = self.fetch_one(query)
        if latest and latest.get('period_number'):
            return str(int(latest['period_number']) + 1)
        return datetime.now().strftime('%Y') + "001"

    # AlgorithmRecommendation 相关方法
    def insert_algorithm_recommendation_root(self, **kwargs: Any) -> Optional[int]:
        """
        使用通用插入方法来插入算法推荐主记录。
        """
        if 'recommend_time' not in kwargs:
            kwargs['recommend_time'] = datetime.now()
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now()

        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                kwargs[key] = json.dumps(value, ensure_ascii=False)

        return self.execute_insert('algorithm_recommendation', kwargs)

    def get_recommendation_by_period(self, period_number: str) -> Optional[AlgorithmRecommendation]:
        query = "SELECT * FROM algorithm_recommendation WHERE period_number = %s LIMIT 1"
        result_raw = self.fetch_one(query, (period_number,))
        return AlgorithmRecommendation(**result_raw) if result_raw else None

    # AlgorithmPerformance 相关方法
    def get_algorithm_performance(self, algorithm_version: str = None) -> List[AlgorithmPerformance]:
        if algorithm_version:
            query = "SELECT * FROM algorithm_performance WHERE algorithm_version = %s"
            results_raw = self.execute_query(query, (algorithm_version,))
        else:
            query = "SELECT * FROM algorithm_performance"
            results_raw = self.execute_query(query)
        return [AlgorithmPerformance(**data) for data in results_raw]

    def update_algorithm_performance_result(self, algorithm_id: str, period_number: str, actual_numbers: str,
                                            is_correct: bool, performance_metrics: str) -> bool:
        query = """
                UPDATE algorithm_performance
                SET actual_numbers      = %s, \
                    is_correct          = %s, \
                    performance_metrics = %s
                WHERE algorithm_id = %s \
                  AND period_number = %s \
                """
        params = (actual_numbers, is_correct, performance_metrics, algorithm_id, period_number)
        affected_rows = self.execute_update(query, params)
        return affected_rows is not None and affected_rows > 0

    def insert_algorithm_prediction_log_batch(self, logs: List[Dict[str, Any]]) -> bool:
        """
        [NEW & SAFE] Specifically for logging individual algorithm predictions.
        Performs a batch insert into the algorithm_prediction_logs table.
        """
        if not logs:
            return True  # Nothing to insert, so it's a success.

        query = """
            INSERT INTO algorithm_prediction_logs 
            (period_number, algorithm_version, predictions, confidence_score, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """

        params_list = []
        for log_entry in logs:
            params_list.append((
                log_entry.get('period_number'),
                log_entry.get('algorithm_version'),
                # Ensure predictions are stored as a JSON string
                json.dumps(log_entry.get('predictions'), ensure_ascii=False),
                log_entry.get('confidence_score'),
                datetime.now()  # Use current time for creation
            ))

        return self.execute_batch_insert(query, params_list)

    def upsert_algorithm_performance_record(self, record_data: Dict[str, Any]) -> bool:
        """
        [NEW & SAFE] Inserts a new performance record. If a record for the same
        period_number and algorithm_version already exists, it updates it.
        This is the correct way to handle per-period performance logging.
        """
        # The base of the INSERT statement
        columns = ', '.join(f"`{k}`" for k in record_data.keys())
        placeholders = ', '.join(['%s'] * len(record_data))
        sql = f"INSERT INTO algorithm_performance ({columns}) VALUES ({placeholders})"

        # The ON DUPLICATE KEY UPDATE part
        # This requires a UNIQUE key on (period_number, algorithm_version) in your table.
        update_placeholders = ', '.join(
            [f"`{k}`=VALUES(`{k}`)" for k in record_data.keys() if k not in ['period_number', 'algorithm_version']])
        sql += f" ON DUPLICATE KEY UPDATE {update_placeholders}, `updated_at`=NOW()"

        # execute_update will return the number of affected rows
        affected_rows = self.execute_update(sql, tuple(record_data.values()))
        return affected_rows is not None and affected_rows > 0
    # RecommendationDetails 相关方法
    def insert_recommendation_details_batch(self, root_id: int, details_list: List[Dict[str, Any]]) -> bool:
        if not details_list:
            return True
        query = """
                INSERT INTO recommendation_details
                (recommendation_metadata_id, recommend_type, strategy_logic,
                 front_numbers, back_numbers, win_probability)
                VALUES (%s, %s, %s, %s, %s, %s) \
                """
        params_list = [
            (
                root_id,
                detail.get("recommend_type", "Unknown"),
                detail.get("strategy_logic", ""),
                detail.get("front_numbers", ""),
                detail.get("back_numbers", ""),
                float(detail.get("win_probability", 0.0))
            ) for detail in details_list
        ]
        return self.execute_batch_insert(query, params_list)

    def get_config(self) -> Dict[str, Any]:
        """
        返回db_config (dict) - 兼容DAO初始化。
        """
        return self.db_config.copy()