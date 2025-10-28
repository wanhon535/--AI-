# run_backtest_simulation.py
# 目的：模拟从历史某一点开始，逐期预测、评估、学习的完整闭环，并将学习结果存入真实数据库。

import json
import os
import sys
import time
import traceback

# --- 1. 项目环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
print(f"项目根目录已添加到路径: {project_root}")

# --- 2. 导入所有系统组件 ---
from src.database.database_manager import DatabaseManager
from src.engine.performance_logger import PerformanceLogger
from src.model.lottery_models import LotteryHistory

# 导入您的数据管理器，我们将用它来加载JSON数据
from src.analysis.manager import load_existing_data, JSON_DATA_FILENAME

# 导入所有需要被评估的基础算法
from src.algorithms.statistical_algorithms import FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, \
    OmissionValueAlgorithm
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer

# 注意：对于需要额外依赖（如PyTorch）或复杂输入的算法，请确保环境已配置
# from src.algorithms.advanced_algorithms.neural_lottery_predictor import NeuralLotteryPredictor
# from src.algorithms.advanced_algorithms.hit_rate_optimizer import HitRateOptimizer


# ----------------- 配置区 -----------------
# 使用前50期数据作为初始“冷启动”训练集，从第51期开始模拟
WARMUP_PERIODS = 50


# -------------------------------------------

def run_simulation():
    """主函数，负责编排整个回测与学习的循环"""
    print("\n" + "=" * 60)
    print("🚀  启动历史回测与学习模拟流程")
    print("=" * 60)

    db_manager = None
    try:
        # --- 步骤一：初始化组件并加载完整历史数据 ---
        print("\n[模拟流程] 步骤 1/3: 初始化组件并从JSON文件加载数据...")

        # 初始化数据库管理器，因为PerformanceLogger需要用它来写入数据
        db_manager = DatabaseManager(
            host='localhost', user='root', password='123456789',
            database='lottery_analysis_system', port=3309
        )
        if not db_manager.connect():
            raise ConnectionError("数据库连接失败，无法进行性能记录。")

        # 初始化性能记录器，并注入真实的数据库管理器
        performance_logger = PerformanceLogger(db_manager=db_manager)

        # 从 dlt_history_data.json 加载全部历史数据
        raw_history = load_existing_data()
        if not raw_history:
            print(f"❌ 错误: 未能在 '{JSON_DATA_FILENAME}' 中找到历史数据。")
            print("请先运行 'python manager.py' 来获取数据。")
            return

        # 将字典列表转换为 LotteryHistory 对象列表
        full_history = [LotteryHistory(**item) for item in raw_history]
        # 确保按期号升序排列，这是回测的基础
        full_history.sort(key=lambda x: x.period_number)

        if len(full_history) < WARMUP_PERIODS + 1:
            print(f"❌ 错误: 历史数据不足以进行回测。需要至少 {WARMUP_PERIODS + 1} 期, 但只找到 {len(full_history)} 期。")
            return

        print(f"✅ 数据加载成功: 共 {len(full_history)} 期历史数据。")
        print(f"✅ 性能记录器已连接到真实数据库。")

        # --- 步骤二：实例化所有待评估的算法 ---
        # 这就是您所有算法的“专家团队”
        base_algorithms = [
            FrequencyAnalysisAlgorithm(), HotColdNumberAlgorithm(), OmissionValueAlgorithm(),
            BayesianNumberPredictor(), MarkovTransitionModel(), NumberGraphAnalyzer(),
        ]
        print(f"✅ 已实例化 {len(base_algorithms)} 个待评估的基础算法。")

        # ======================================================================
        # 步骤三：开始逐期滚动回测
        # ======================================================================
        print("\n[模拟流程] 步骤 2/3: 开始逐期滚动回测与学习...")

        # 从第 WARMUP_PERIODS 期开始，循环到最后一期
        for i in range(WARMUP_PERIODS, len(full_history)):

            # --- a. 准备当前循环的数据 ---
            history_for_prediction = full_history[:i]  # 用于训练和预测的历史数据 (截止到上一期)
            actual_draw_to_evaluate = full_history[i]  # 本期要预测的、已知的真实结果
            issue_to_predict = actual_draw_to_evaluate.period_number

            print("\n" + "-" * 50)
            print(f"🔄  正在处理期号: {issue_to_predict} | 使用数据: {len(history_for_prediction)} 期")

            # --- b. 运行所有基础算法，生成各自的预测 ---
            model_outputs_for_evaluation = {}
            for algo in base_algorithms:
                try:
                    algo.train(history_for_prediction)
                    if algo.is_trained:
                        prediction = algo.predict(history_for_prediction)
                        model_outputs_for_evaluation[algo.name] = prediction
                except Exception as e:
                    print(f"  - 警告: 算法 '{algo.name}' 在处理期号 {issue_to_predict} 时出错: {e}")
                    model_outputs_for_evaluation[algo.name] = {'error': str(e)}

            print(f"  - 所有基础算法已为期号 {issue_to_predict} 生成预测。")

            # --- c. 评估与学习：将本期所有算法的预测与真实结果对比，并记录到数据库 ---
            print(f"  - 正在评估预测结果并记录到数据库...")
            performance_logger.evaluate_and_update(
                issue=issue_to_predict,
                model_outputs=model_outputs_for_evaluation,
                actual_draw=actual_draw_to_evaluate
            )
            print(f"  - ✅ 期号 {issue_to_predict} 的算法表现已成功记录到数据库。")

            time.sleep(0.1)  # 短暂休眠，避免日志滚动过快

        # ======================================================================
        # 步骤四：结束
        # ======================================================================
        print("\n[模拟流程] 步骤 3/3: 所有历史数据回测完毕。")
        print("✅ 您的 'algorithm_performance' 数据库表现已填充完毕！")
        print("现在您可以运行 main.py 来进行一次基于学习的未来预测了。")


    except Exception as e:
        print(f"\n❌ 模拟流程发生意外错误: {e}")
        traceback.print_exc()
    finally:
        if db_manager and db_manager._connected:
            db_manager.disconnect()
        print("\n" + "=" * 60)
        print("🏁  模拟流程结束。数据库连接已关闭。")
        print("=" * 60)


if __name__ == "__main__":
    run_simulation()