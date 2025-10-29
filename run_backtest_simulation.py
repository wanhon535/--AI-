#!/usr/bin/env python3
# run_backtest_simulation.py (Refactored for Robustness)

import os
import sys
import csv
import json
import time
import argparse
import traceback
from datetime import datetime
from typing import List, Dict, Any

# --- 1. Project Environment Setup ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.model.model_prediction import ModelPrediction
from src.database.database_manager import DatabaseManager
from src.database.crud.lottery_history_dao import LotteryHistoryDAO
from src.database.crud.algorithm_recommendation_dao import AlgorithmRecommendationDAO
from src.engine.performance_logger import PerformanceLogger

# --- 2. Configuration ---
DB_CONFIG = dict(
    host='127.0.0.1', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)
OUTPUT_DIR = os.path.join(project_root, "outputs")
DEFAULT_SLEEP_INTERVAL = 0.0  # 在本地回测时，通常不需要等待


class BacktestRunner:
    """
    一个健壮的彩票回测运行器.
    - 增强了数据解析能力
    - 改进了日志输出
    - 优化了CSV导出格式
    """

    def __init__(self, db_config, sleep_interval=DEFAULT_SLEEP_INTERVAL):
        self.db = DatabaseManager(**db_config)
        self.history_dao: LotteryHistoryDAO = None
        self.reco_dao: AlgorithmRecommendationDAO = None
        self.performance_logger: PerformanceLogger = None
        self.summary_rows: List[Dict[str, Any]] = []
        self.sleep_interval = sleep_interval
        self._all_model_names = set()  # 用于收集所有出现过的模型名称

    def connect(self):
        """建立数据库连接并初始化所有DAO."""
        if not self.db.connect():
            raise ConnectionError("❌ 无法连接到数据库，请检查配置。")
        self.history_dao = LotteryHistoryDAO(self.db)
        self.reco_dao = AlgorithmRecommendationDAO(self.db)
        self.performance_logger = PerformanceLogger(db_manager=self.db)
        print("✅ 数据库连接成功，所有组件已初始化。")

    def disconnect(self):
        """安全地关闭数据库连接."""
        if self.db and getattr(self.db, "_connected", False):
            self.db.disconnect()
            print("\n🔌 数据库连接已关闭。")

    def _auto_range(self) -> (int, int):
        """自动从数据库中检测回测的起止期号."""
        print("🔎 正在自动检测回测区间...")
        earliest_pred = self.reco_dao.get_earliest_period()
        latest_pred = self.reco_dao.get_latest_period()
        earliest_hist = self.history_dao.get_earliest_period()
        latest_hist = self.history_dao.get_latest_period()

        # ✅ 过滤掉None和无法转换为整数的值
        candidates_start = [int(p) for p in [earliest_pred, earliest_hist] if p and str(p).isdigit()]
        candidates_end = [int(p) for p in [latest_pred, latest_hist] if p and str(p).isdigit()]

        if not candidates_start or not candidates_end:
            raise RuntimeError(
                "无法自动确定回测区间，请确认 'lottery_history' 和 'algorithm_recommendation' 表中有数据。")

        start_issue, end_issue = min(candidates_start), max(candidates_end)
        print(f"➡️  自动检测到有效区间: {start_issue} → {end_issue}")
        return start_issue, end_issue

    def _parse_numbers(self, data: Any) -> List[int]:
        """【健壮性提升】从多种格式中安全地解析出数字列表."""
        if isinstance(data, list):
            return [int(n) for n in data if str(n).isdigit()]
        if not isinstance(data, str):
            return []

        # 尝试作为JSON解析
        try:
            nums = json.loads(data)
            return [int(n) for n in nums if isinstance(n, (int, str)) and str(n).isdigit()]
        except json.JSONDecodeError:
            # 尝试作为逗号分隔的字符串解析
            return [int(n.strip()) for n in data.split(',') if n.strip().isdigit()]

    def _collect_model_outputs_for_issue(self, issue_str: str) -> Dict[str, ModelPrediction]:
        """
        【核心重构】从数据库记录中收集并统一所有模型的预测输出.
        """
        predictions_from_db = self.reco_dao.get_by_period(issue_str)
        model_outputs = {}
        if not predictions_from_db:
            return model_outputs

        for idx, p_data in enumerate(predictions_from_db):
            try:
                # 兼容字典和对象两种来源
                p = p_data if isinstance(p_data, dict) else p_data.__dict__

                model_name = p.get("model_name") or p.get("algorithm_version") or f"unknown_model_{idx}"

                # ✅ 兼容不同的键名
                front_numbers_raw = p.get("front_numbers") or p.get("front_area") or p.get("recommended_numbers")
                back_numbers_raw = p.get("back_numbers") or p.get("back_area")

                front_numbers = self._parse_numbers(front_numbers_raw)
                back_numbers = self._parse_numbers(back_numbers_raw)

                confidence = float(p.get("confidence_score") or p.get("confidence") or 0.0)

                if not front_numbers or not back_numbers:
                    print(f"  - 🟡 警告: 模型 '{model_name}' 在期号 {issue_str} 的预测数据不完整或无法解析，已跳过。")
                    continue

                model_outputs[model_name] = ModelPrediction(
                    front_numbers=front_numbers,
                    back_numbers=back_numbers,
                    confidence=confidence
                )
                self._all_model_names.add(model_name)  # 收集模型名称

            except Exception as e:
                print(f"  - 🔴 错误: 解析期号 {issue_str} 的一条预测记录时失败: {e}")
                continue
        return model_outputs

    def run(self, start_issue: int, end_issue: int):
        """执行回测的主循环."""
        print(f"\n▶️  开始回测, 区间: {start_issue} → {end_issue}, 共 {end_issue - start_issue + 1} 期")

        for issue in range(start_issue, end_issue + 1):
            issue_str = str(issue)
            try:
                print("\n" + "-" * 70)
                print(f"🔎 处理期号: {issue_str} ({issue - start_issue + 1}/{end_issue - start_issue + 1})")

                # 1. 获取真实开奖结果 (现在返回的是LotteryHistory对象)
                actual_draw = self.history_dao.get_by_period(issue_str)
                if not actual_draw:
                    print(f"  - ⏸️  未找到期号 {issue_str} 的开奖历史，跳过。")
                    continue

                # 2. 收集所有模型的预测
                model_outputs = self._collect_model_outputs_for_issue(issue_str)
                if not model_outputs:
                    print(f"  - ⏸️  未找到期号 {issue_str} 的算法预测，跳过。")
                    continue

                # 3. 评估并更新性能
                print(f"  - ✅ 找到 {len(model_outputs)} 个模型预测，正在评估...")
                eval_report = self.performance_logger.evaluate_and_update(
                    issue=issue_str,
                    model_outputs=model_outputs,
                    actual_draw=actual_draw
                )

                # 4. 准备本期回测摘要
                row = {'issue': issue_str}
                if eval_report:
                    scores = list(eval_report.values())
                    best_model = max(eval_report, key=eval_report.get)
                    row.update({
                        'num_models': len(model_outputs),
                        'avg_score': sum(scores) / len(scores) if scores else 0.0,
                        'best_model': best_model,
                        'best_score': eval_report[best_model],
                        **{f"score_{model}": score for model, score in eval_report.items()}  # ✅ 扁平化处理
                    })
                else:
                    row.update({'num_models': len(model_outputs), 'avg_score': 0.0})

                self.summary_rows.append(row)

                if self.sleep_interval > 0:
                    time.sleep(self.sleep_interval)

            except KeyboardInterrupt:
                print("\n⛔ 用户中断。正在停止回测并导出已有结果...")
                break
            except Exception as e:
                print(f"❌ 处理期号 {issue_str} 时发生严重错误: {e}")
                traceback.print_exc()
                continue

        self._export_summary_csv()
        print("\n✅ 回测任务完成。")

    def _export_summary_csv(self):
        """【功能改进】导出扁平化、更易于分析的CSV摘要文件."""
        if not self.summary_rows:
            print("（无回测摘要可导出）")
            return

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = f"backtest_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # ✅ 动态生成表头，确保所有模型的得分列都被包含
        fieldnames = ['issue', 'num_models', 'avg_score', 'best_model', 'best_score']
        score_fields = sorted([f"score_{name}" for name in self._all_model_names])
        fieldnames.extend(score_fields)

        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, restval='N/A')
            writer.writeheader()
            writer.writerows(self.summary_rows)

        print(f"📁 回测摘要已成功导出到: {filepath}")


def parse_args():
    """解析命令行参数."""
    p = argparse.ArgumentParser(
        description="逐期回测引擎：使用数据库中的历史预测与开奖结果，评估算法性能并生成报告。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    p.add_argument("--start", type=int, help="开始期号（包含）")
    p.add_argument("--end", type=int, help="结束期号（包含）")
    p.add_argument("--auto", action="store_true", help="自动从数据库中检测完整的起止期号进行回测。")
    p.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_INTERVAL,
                   help="每期处理后的等待时间（秒）。默认: %(default)s")
    return p.parse_args()


def main():
    """主执行函数."""
    args = parse_args()
    runner = BacktestRunner(DB_CONFIG, sleep_interval=args.sleep)

    try:
        runner.connect()

        if args.auto:
            start_issue, end_issue = runner._auto_range()
        else:
            if args.start is None or args.end is None:
                print("❌ 错误: 请使用 --start 和 --end 指定回测区间, 或使用 --auto 自动检测。")
                return
            start_issue, end_issue = args.start, args.end

        if start_issue > end_issue:
            print(f"❌ 错误: 开始期号 ({start_issue}) 不能大于结束期号 ({end_issue})。")
            return

        runner.run(start_issue=start_issue, end_issue=end_issue)

    except Exception as e:
        print(f"\n❌ 回测任务因严重错误而失败: {e}")
        traceback.print_exc()
    finally:
        runner.disconnect()


if __name__ == "__main__":
    main()