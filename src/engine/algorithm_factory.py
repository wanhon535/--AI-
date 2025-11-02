# 文件: src/engine/algorithm_factory.py

import json
from typing import List

# --- 只导入必要的、安全的模块 ---
from src.database.database_manager import DatabaseManager
from src.algorithms.base_algorithm import BaseAlgorithm
from src.algorithms import AVAILABLE_ALGORITHMS  # 导入算法注册表


def create_algorithms_from_db(db_manager: DatabaseManager) -> List[BaseAlgorithm]:
    """
    从数据库读取 'algorithm_configs' 表，动态创建并返回所有启用的算法实例列表。
    这是一个独立的工厂函数，不依赖 main.py。
    """
    active_algorithms = []
    try:
        configs = db_manager.execute_query("SELECT * FROM algorithm_configs WHERE is_active = 1")
    except Exception as e:
        print(f"❌ [算法工厂] 严重错误: 无法从数据库读取算法配置。错误: {e}")
        return []

    print(f"\n🏭 [算法工厂] 从数据库发现 {len(configs)} 个启用的算法配置...")
    for config in configs:
        algo_name = config.get('algorithm_name')
        if not algo_name:
            continue
        if algo_name in AVAILABLE_ALGORITHMS:
            try:
                algorithm_class = AVAILABLE_ALGORITHMS[algo_name]
                algorithm_instance = algorithm_class()
                db_params_str = config.get('parameters')
                if db_params_str:
                    params_dict = json.loads(db_params_str)
                    if hasattr(algorithm_instance, 'set_parameters'):
                        algorithm_instance.set_parameters(params_dict)
                active_algorithms.append(algorithm_instance)
                print(f"  - ✅ 已成功创建并配置算法: {algo_name}")
            except Exception as e:
                print(f"  - ❌ 创建算法实例 '{algo_name}' 时失败: {e}")
        else:
            print(f"  - ⚠️ 警告: 数据库中配置的算法 '{algo_name}' 在代码中未注册，已跳过。")

    return active_algorithms