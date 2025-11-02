# 文件: scripts/evaluate_and_learn.py (V4 - 调度器版)
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path: sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from src.engine.evaluation_service import run_evaluation_for_period  # 从核心服务导入


def run_full_backtest(db_manager: DatabaseManager):
    print("\n" + "#" * 70 + "\n###      🚀 执行完整历史回测与学习      ###\n" + "#" * 70)
    db_manager.execute_update("TRUNCATE TABLE algorithm_performance")
    periods_raw = db_manager.execute_query(
        "SELECT DISTINCT period_number FROM algorithm_prediction_logs ORDER BY period_number ASC")
    if not periods_raw:
        print("  - ❌ `algorithm_prediction_logs` 为空，无法回测。")
        return
    periods = [p['period_number'] for p in periods_raw]
    print(f"  - 将对 {len(periods)} 个历史期号进行评估...")
    for i, period in enumerate(periods):
        print(f"\r--- 进度: {i + 1}/{len(periods)} (期号: {period}) ---", end="")
        run_evaluation_for_period(db_manager, period)
    print("\n" + "#" * 70 + "\n###      🏁 完整历史回测与学习完成！      ###\n" + "#" * 70)


if __name__ == "__main__":
    db = DatabaseManager(**DB_CONFIG)
    if not db.connect(): sys.exit(1)
    run_full_backtest(db)
    db.disconnect()