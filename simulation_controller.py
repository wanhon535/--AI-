# file: simulation_controller.py

import os
import sys
import traceback
import time

# --- 环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 导入所有需要的组件 ---
from src.database.database_manager import DatabaseManager
from src.engine.performance_logger import PerformanceLogger
# 假设您的主决策管道封装在一个类里，如果没有，我们需要封装一下
# from main import LottoProPipeline # 这是理想情况，我们先模拟调用
# from run_prediction_generator import main as run_all_predictions  # 我们先用这个脚本
from src.analysis.database_importer import sync_lottery_data_to_db, DB_CONFIG


class SimulationController:
    """
    序贯决策仿真控制器
    模拟“预测 -> 开奖 -> 评估”的循环。
    """

    def __init__(self, db_config):
        self.db_manager = DatabaseManager(**db_config)
        self.performance_logger = None

    def setup(self):
        """初始化连接和组件。"""
        if not self.db_manager.connect():
            raise ConnectionError("数据库连接失败。")
        # 注意：PerformanceLogger现在在需要时才实例化和使用
        print("✅ 控制器初始化成功，数据库已连接。")

    def teardown(self):
        """关闭连接。"""
        self.db_manager.disconnect()
        print("🔌 控制器已关闭数据库连接。")

    def run_simulation(self, start_issue: str, end_issue: str):
        """
        按期号范围运行仿真。

        Args:
            start_issue (str): 仿真的起始期号。
            end_issue (str): 仿真的结束期号。
        """
        print("\n" + "=" * 60)
        print(f"🚀 启动仿真流程，范围: {start_issue} -> {end_issue}")
        print("=" * 60 + "\n")

        history_dao = self.db_manager.get_dao('LotteryHistoryDAO')
        reco_dao = self.db_manager.get_dao('AlgorithmRecommendationDAO')

        current_issue = int(start_issue)
        end_issue_int = int(end_issue)

        while current_issue <= end_issue_int:
            issue_str = str(current_issue)
            print("\n" + "-" * 50)
            print(f"🗓️  正在处理期号: {issue_str}")
            print("-" * 50)

            try:
                # --- 步骤 1: AI进行预测 ---
                # 在这一步，AI只能看到 `issue_str - 1` 之前的所有历史数据
                print("  [1/3] 🤖 AI 正在基于现有历史数据进行预测...")
                # 调用您的预测生成脚本
                # 注意：实际应用中，应将 run_prediction_generator 的逻辑封装成一个函数或类
                # 并传入 current_issue 作为目标期号

                # --- 这里我们暂时模拟调用，并假设它已经将预测写入数据库 ---
                # run_all_predictions(target_issue=issue_str) # 理想的调用方式
                # 为了简单，我们先假设预测已存在，或者您可以手动运行 `run_prediction_generator.py`
                # 检查数据库中是否已有该期的预测
                if not reco_dao.get_by_period(issue_str):
                    print(f"  - 🟡 警告: 数据库中未找到期号 {issue_str} 的预测。请先运行 'run_prediction_generator.py'。")
                    print(f"  - 仿真暂停，等待预测数据... (您可以现在运行脚本，然后重新开始仿真)")
                    break

                print("  - ✅ 预测阶段完成。")

                # --- 步骤 2: 模拟开奖 ---
                # 检查数据库中是否已经有这一期的真实开奖结果
                print("\n  [2/3] 🎲 正在等待开奖...")
                actual_draw = history_dao.get_by_period(issue_str)
                if not actual_draw:
                    print(f"  - 数据库中未找到期号 {issue_str} 的开奖结果。")
                    print("  - 正在尝试从API同步最新数据...")
                    sync_lottery_data_to_db()  # 尝试从API获取
                    actual_draw = history_dao.get_by_period(issue_str)

                if not actual_draw:
                    print(f"  - 🔴 错误: 仍然无法获取期号 {issue_str} 的开奖结果。仿真无法继续。")
                    break

                print(f"  - 🎉 开奖结果已获取! 前区: {actual_draw.front_area}, 后区: {actual_draw.back_area}")

                # --- 步骤 3: 评估与学习 (奖罚分明) ---
                print("\n  [3/3] 🧠 AI 正在评估预测结果并学习...")
                model_outputs = self._collect_predictions_for_issue(reco_dao, issue_str)

                if not model_outputs:
                    print("  - 🟡 评估跳过，因为没有找到有效的模型输出。")
                else:
                    perf_logger = PerformanceLogger(self.db_manager)
                    eval_report = perf_logger.evaluate_and_update(
                        issue=issue_str,
                        model_outputs=model_outputs,
                        actual_draw=actual_draw
                    )
                    print(f"  - ✅ 评估完成。各模型得分: {eval_report}")
                    print("  - 算法权重和性能已更新到数据库。")

                # 移至下一期
                current_issue += 1
                time.sleep(2)  # 模拟真实世界的时间流逝

            except Exception as e:
                print(f"❌❌❌ 处理期号 {issue_str} 时发生严重错误: {e}")
                traceback.print_exc()
                break

        print("\n" + "=" * 60)
        print("🏁 仿真流程结束。")
        print("=" * 60)

    def _collect_predictions_for_issue(self, reco_dao, issue_str):
        """一个简单的辅助函数，用于从DAO结果中整理模型输出。"""
        # 这个逻辑可以从您的 backtest 脚本中借鉴和简化
        preds = reco_dao.get_by_period(issue_str)
        outputs = {}
        for p in preds:
            model_name = p.get("model_name") or p.get("algorithm_version", "unknown")
            outputs[model_name] = {
                "front_numbers": [int(n) for n in p.get("front_numbers", "").split(',') if n],
                "back_numbers": [int(n) for n in p.get("back_numbers", "").split(',') if n],
                "confidence": p.get("confidence_score", 0.5)
            }
        return outputs


if __name__ == '__main__':
    # --- 如何运行 ---
    # 1. 确保您的 lottery_history 表中有一些基础数据。
    #    运行: python database_importer.py
    # 2. 为一个未来的期号生成预测。
    #    运行: python run_prediction_generator.py
    # 3. 运行此仿真控制器，范围应包含您预测的期号。

    # 示例: 假设数据库最新到 2025050, 且你已为 2025051 生成了预测
    START_ISSUE = "2025051"
    END_ISSUE = "2025055"  # 仿真器会尝试运行到这一期

    controller = SimulationController(DB_CONFIG)
    try:
        controller.setup()
        controller.run_simulation(START_ISSUE, END_ISSUE)
    except Exception as e:
        print(f"控制器启动失败: {e}")
    finally:
        controller.teardown()