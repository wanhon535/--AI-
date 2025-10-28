# src/database/crud/model_training_log_dao.py

import json
from datetime import datetime
from typing import Dict, Any
from src.database.database_manager import DatabaseManager


class ModelTrainingLogDAO:
    """DAO for the model_training_logs table."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def start_log(self, algorithm_version: str, data_start_period: str, data_end_period: str,
                  training_samples: int) -> int:
        """
        开始一次新的训练/预测流程，并返回该日志记录的ID。
        """
        sql = """
        INSERT INTO model_training_logs 
        (algorithm_version, training_date, data_start_period, data_end_period, training_samples, training_status, started_at)
        VALUES (%s, %s, %s, %s, %s, 'running', %s)
        """
        now = datetime.now()
        params = (algorithm_version, now.date(), data_start_period, data_end_period, training_samples, now)

        # 使用 execute_update 并获取 lastrowid
        self.db.execute_update(sql, params)
        last_id = self.db.get_last_insert_id()
        print(f"  - [LOG] Started log record with ID: {last_id}")
        return last_id

    def complete_log(self, log_id: int, training_params: Dict = None, analysis_summary: Dict = None):
        """
        标记日志为“完成”，并更新结束时间和时长。
        """
        sql = """
        UPDATE model_training_logs 
        SET 
            training_status = 'completed', 
            completed_at = %s,
            training_duration = TIMESTAMPDIFF(SECOND, started_at, %s),
            training_parameters = %s,
            feature_set = %s
        WHERE id = %s
        """
        now = datetime.now()
        params_json = json.dumps(training_params, ensure_ascii=False) if training_params else None
        analysis_json = json.dumps(analysis_summary, ensure_ascii=False) if analysis_summary else None

        params = (now, now, params_json, analysis_json, log_id)
        self.db.execute_update(sql, params)
        print(f"  - [LOG] Completed log record ID: {log_id}")

    def fail_log(self, log_id: int, error_message: str):
        """
        标记日志为“失败”，并记录错误信息。
        """
        sql = """
        UPDATE model_training_logs 
        SET 
            training_status = 'failed', 
            completed_at = %s,
            training_duration = TIMESTAMPDIFF(SECOND, started_at, %s),
            error_log = %s
        WHERE id = %s
        """
        now = datetime.now()
        params = (now, now, error_message, log_id)
        self.db.execute_update(sql, params)
        print(f"  - [LOG] Failed log record ID: {log_id}. Error has been logged.")