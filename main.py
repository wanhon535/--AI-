# main.py (V13 - 工作流驱动版)

import os
import sys
import json
from typing import List

# --- 环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 核心组件导入 ---
from src.database.database_manager import DatabaseManager
from src.engine.scheduler import Scheduler  # 导入新的调度器
from src.algorithms.base_algorithm import BaseAlgorithm
from src.algorithms import AVAILABLE_ALGORITHMS
from src.config.database_config import DatabaseConfig
from src.config.database_config import DB_CONFIG
from src.engine.algorithm_factory import create_algorithms_from_db


# --- 全局配置 ---
DB_CONFIG = DatabaseConfig.get_config()

MODELS_TO_RUN = [
    # "qwen3-max",
    # "gpt-4o" # 将来要用时取消注释
    # "gemini-2.5-flash"
    "deepseek-chat"
]


# --- 算法工厂函数 (保持不变) ---



# --- 主函数 (最终简化版) ---
def main():
    db_manager = DatabaseManager(**DB_CONFIG)
    if not db_manager.connect():
        print("❌ 数据库连接失败，程序终止。")
        return

    try:
        # 1. 创建调度器
        scheduler = Scheduler(db_manager)

        # 2. 配置工作流 (传入要运行的模型列表)
        scheduler.setup_daily_workflow(models_to_run=MODELS_TO_RUN)

        # 3. 运行！
        scheduler.run()

    except Exception as e:
        print(f"\n❌ 系统主流程发生顶层严重错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db_manager and db_manager.is_connected():
            db_manager.disconnect()


if __name__ == "__main__":
    main()