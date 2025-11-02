# 文件: scripts/run_reward_system.py
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path: sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from src.engine.evaluation_service import run_evaluation_for_period


def run_full_reward_calculation():
    db = DatabaseManager(**DB_CONFIG)
    if not db.connect(): return

    print("开始对所有需要评估的推荐进行“奖罚分明”计算...")
    periods_raw = db.execute_query("""
                                   SELECT DISTINCT ar.period_number
                                   FROM algorithm_recommendation ar
                                            JOIN lottery_history lh ON ar.period_number = lh.period_number
                                            LEFT JOIN reward_penalty_records rpr ON ar.id = rpr.recommendation_id
                                   WHERE rpr.id IS NULL
                                   ORDER BY ar.period_number ASC
                                   """)
    if not periods_raw:
        print("✅ 所有推荐均已评估。")
        return

    periods = {p['period_number'] for p in periods_raw}
    print(f"发现 {len(periods)} 个期号的推荐需要评估。")

    for period in sorted(list(periods)):
        # 对每个需要评估的期号，运行一次完整的双重评估服务
        run_evaluation_for_period(db, period)

    db.disconnect()
    print("\n🏁 “奖罚分明”评估全部完成！")


if __name__ == "__main__":
    run_full_reward_calculation()