# scripts/initialize_configs.py

import json
import os
import sys

# --- 环境设置 ---
# 确保脚本能找到 src 目录下的模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager

# --- 数据库配置 (建议从统一配置中导入) ---
DB_CONFIG = dict(
    host='localhost', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)

# --- 算法武器库定义 ---
# 定义了系统中所有可用的算法及其元数据
# is_active: 1 表示默认启用, 0 表示默认禁用 (对于复杂或实验性算法)
AVAILABLE_ALGORITHMS = {
    # --- 1. 基础统计算法 (默认启用) ---
    "FrequencyAnalysisAlgorithm": {
        "type": "statistical",
        "description": "基于历史出现频率进行分析的基础统计算法。",
        "params": {"top_n": 10},
        "is_active": 1
    },
    "HotColdNumberAlgorithm": {
        "type": "statistical",
        "description": "分析号码的热冷状态，追踪近期热门和冷门号码。",
        "params": {"hot_threshold": 3, "cold_window": 20},  # 热号定义为最近20期出现3次以上
        "is_active": 1
    },
    "OmissionValueAlgorithm": {
        "type": "statistical",
        "description": "基于号码的当前遗漏值进行分析。",
        "params": {"high_omission_threshold": 15},
        "is_active": 1
    },

    # --- 2. 核心机器学习算法 (默认启用) ---
    "BayesianNumberPredictor": {
        "type": "ml",
        "description": "使用贝叶斯理论，根据先验知识更新号码出现的后验概率。",
        "params": {},  # 无需额外参数
        "is_active": 1
    },
    "MarkovTransitionModel": {
        "type": "ml",
        "description": "将号码出现视为状态转移，构建马尔可夫链进行预测。",
        "params": {},  # 无需额外参数
        "is_active": 1
    },
    "NumberGraphAnalyzer": {
        "type": "ml",
        "description": "构建号码关系图网络，分析号码之间的伴随关系。",
        "params": {},  # 无需额外参数
        "is_active": 1
    },

    # --- 3. 高级与集成算法 (默认部分禁用，可手动开启) ---
    "IntelligentPatternRecognizer": {
        "type": "ml",
        "description": "智能模式识别 - 发现深层号码规律，如序列、间隔、趋势等。",
        "params": {"min_pattern_length": 3, "confidence_threshold": 0.8},
        "is_active": 1  # 模式识别很有用，默认开启
    },
    "HitRateOptimizer": {
        "type": "optimization",
        "description": "[高级] 通过遗传算法搜索，找到期望命中率最高的号码组合。依赖子模型。",
        "params": {"population_size": 30, "generations": 50, "mutation_rate": 0.15},
        "is_active": 0  # 依赖其他模型，默认禁用
    },
    "NeuralLotteryPredictor": {
        "type": "ml",
        "description": "[高级] 基于LSTM的神经网络预测器，需要PyTorch。计算成本高。",
        "params": {"epochs": 10, "learning_rate": 0.001, "hidden_size": 64},
        "is_active": 0  # 依赖PyTorch且耗时，默认禁用
    },
    "LotteryRLAgent": {
        "type": "ml",
        "description": "[实验性] Q-learning 简化强化学习代理，用于决策。",
        "params": {"episodes": 500, "gamma": 0.9, "alpha": 0.1, "epsilon": 0.2},
        "is_active": 0  # 实验性功能，默认禁用
    },

    # --- 4. 风险与策略算法 (作为辅助分析，默认禁用) ---
    "RiskAssessmentAlgorithm": {
        "type": "optimization",
        "description": "评估系统风险，提供投注策略建议。",
        "params": {"max_stake_ratio": 0.05, "risk_tolerance": 0.7},
        "is_active": 0
    },
    "PortfolioOptimizationAlgorithm": {
        "type": "optimization",
        "description": "应用投资组合理论优化投注分配。",
        "params": {"target_return": 0.1, "max_volatility": 0.15},
        "is_active": 0
    },
    "StopLossAlgorithm": {
        "type": "optimization",
        "description": "提供止损策略以控制风险。",
        "params": {"max_loss_ratio": 0.2, "trailing_stop": 0.1},
        "is_active": 0
    },

    # --- 5. 集成器与学习器 (这些是元算法，通常在代码中直接使用，但也可注册) ---
    # 注意：这些元算法通常包装其他算法，所以这里只做注册，实际使用时逻辑更复杂
    "DynamicEnsembleOptimizer": {
        "type": "ensemble",
        "description": "[元算法] 动态权重集成优化器，实时调整其他算法的权重。",
        "params": {"evaluation_window": 20, "weight_decay_factor": 0.95},
        "is_active": 0  # 这是元算法，由推荐引擎直接调用，而非独立运行
    },
    "RealTimeFeedbackLearner": {
        "type": "ensemble",
        "description": "[元算法] 实时反馈学习器，根据最新结果立即调整策略。",
        "params": {"learning_rate": 0.2, "pattern_memory_size": 50},
        "is_active": 0  # 元算法
    }
}


def initialize_algorithm_configs():
    """
    初始化或更新算法配置表 (algorithm_configs)。
    将代码中定义的算法元数据写入数据库，实现配置驱动。
    """
    db_manager = DatabaseManager(**DB_CONFIG)
    if not db_manager.connect():
        print("❌ 数据库连接失败。")
        return

    print("\n" + "=" * 60)
    print("🚀 正在同步算法库到数据库配置...")
    print("=" * 60)

    try:
        inserted_count = 0
        skipped_count = 0
        for name, config in AVAILABLE_ALGORITHMS.items():
            # 检查算法是否已存在
            exists_query = "SELECT id FROM algorithm_configs WHERE algorithm_name = %s"
            result = db_manager.execute_query(exists_query, (name,))

            if result:
                # print(f"  - 算法 '{name}' 已存在，跳过。")
                skipped_count += 1
                continue

            # 插入新算法
            insert_query = """
            INSERT INTO algorithm_configs 
            (algorithm_name, algorithm_type, parameters, description, version, is_active, is_default, created_by)
            VALUES (%s, %s, %s, %s, '1.0.0', %s, 0, 'system_init')
            """
            params_json = json.dumps(config['params'])
            db_manager.execute_update(
                insert_query,
                (name, config['type'], params_json, config['description'], config['is_active'])
            )
            print(f"  ✅ 成功注册新算法: {name}")
            inserted_count += 1

        print("\n" + "-" * 60)
        print("✨ 同步完成！")
        print(f"  - 新增注册算法: {inserted_count} 个")
        print(f"  - 已存在的算法: {skipped_count} 个")
        print(f"  - 数据库中的算法配置已是最新状态。")
        print("-" * 60)


    except Exception as e:
        print(f"❌ 初始化过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    initialize_algorithm_configs()