from datetime import datetime
from src.database.database_manager import DatabaseManager

def log_system_event(db_manager: DatabaseManager, user_id: str, event_type: str,
                     status: str, details: dict = None, event_source: str = 'Unknown'):
    """
    向 system_logs 表插入一条系统事件日志。
    """
    try:
        log_entry = {
            'event_time': datetime.now(),
            'user_id': user_id,
            'event_type': event_type,
            'status': status,
            'details': json.dumps(details, ensure_ascii=False) if details else None,
            'event_source': event_source
        }
        db_manager.execute_insert('system_logs', log_entry)
    except Exception as e:
        # 日志记录失败不能中断主流程，只能打印错误
        print(f"🚨 CRITICAL: 系统日志记录失败！ Event: {event_type}, Error: {e}")