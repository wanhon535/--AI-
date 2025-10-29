import os
import sys
import traceback
from datetime import datetime

# --- 1️⃣ 环境导入 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.config.database_config import DatabaseConfig
from src.database.database_manager import DatabaseManager
from src.database.crud.algorithm_performance_dao import AlgorithmPerformanceDAO
from src.database.crud.algorithm_recommendation_dao import AlgorithmRecommendationDAO
from src.algorithms import *  # 自动加载所有算法模块
from src.model.lottery_models import LotteryHistory

# --- 2️⃣ 自动收集算法 ---
def discover_algorithms():
    alg_classes = []
    for name, obj in globals().items():
        if name.endswith("Algorithm") and callable(obj):
            try:
                instance = obj()
                if hasattr(instance, "predict") and hasattr(instance, "evaluate"):
                    alg_classes.append(instance)
            except Exception:
                continue
    return alg_classes

# --- 3️⃣ 回测主流程 ---
def run_backtest(limit=300):
    db = DatabaseManager(
        host=DatabaseConfig.HOST,
        user=DatabaseConfig.USER,
        password=DatabaseConfig.PASSWORD,
        database=DatabaseConfig.DATABASE,
        port=getattr(DatabaseConfig, "PORT", 3306),
    )

    perf_dao = AlgorithmPerformanceDAO(db)
    rec_dao = AlgorithmRecommendationDAO(db)

    print("\n🔥 启动 Lotto-Pro 历史回测引擎 V1.0")
    print("=" * 60)
    from src.database.crud.lottery_history_dao import LotteryHistoryDAO

    lottery_dao = LotteryHistoryDAO(db)
    draws = lottery_dao.get_all_history(limit=limit)
    algorithms = discover_algorithms()

    print(f"✅ 检测到算法数量: {len(algorithms)} 个")
    print(f"✅ 历史期数: {len(draws)}")

    for alg in algorithms:
        print(f"\n🔹 回测算法: {alg.__class__.__name__}")
        for draw in draws:
            try:
                period = draw["period_number"]
                real_nums = draw.get("numbers") or draw.get("winning_numbers")

                prediction = alg.predict()
                score = alg.evaluate(prediction, real_nums)

                perf_dao.insert_performance(period, alg.__class__.__name__, score)
                rec_dao.insert_algorithm_recommendation_root(period, alg.__class__.__name__, score, "Medium")

            except Exception as e:
                print(f"❌ {alg.__class__.__name__} 在期 {period} 失败: {e}")
                continue

    print("\n🏁 回测完成，数据库已更新。\n")


if __name__ == "__main__":
    try:
        run_backtest(limit=300)
    except Exception as e:
        print("❌ 回测执行失败:", e)
        traceback.print_exc()
