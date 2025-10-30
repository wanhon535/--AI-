#!/usr/bin/env python3
# run_backtest_simulation.py (V2.3 - 修复 get_dao 调用方式)

import os
import sys
import csv
import json
import time
import argparse
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- 1. 环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# <<< 关键修正 1/2 >>>
# 导入我们需要用到的 DAO 类本身，而不是它的名字字符串
from src.database.crud.lottery_history_dao import LotteryHistoryDAO
from src.model.lottery_models import LotteryHistory
from src.database.database_manager import DatabaseManager
from src.engine.performance_logger import PerformanceLogger

# --- 2. 配置 (保持不变) ---
DB_CONFIG = dict(
    host='localhost', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)
OUTPUT_DIR = os.path.join(project_root, "outputs")
DEFAULT_SLEEP_INTERVAL = 0.0

class BacktestRunner:
    # ... (这个类的其他部分代码保持不变) ...
    def __init__(self, db_config, sleep_interval=DEFAULT_SLEEP_INTERVAL):
        self.db = DatabaseManager(**db_config)
        self.performance_logger: Optional[PerformanceLogger] = None
        self.summary_rows: List[Dict[str, Any]] = []
        self.sleep_interval = sleep_interval
        self._all_model_names = set()
    def connect(self):
        if not self.db.connect():
            raise ConnectionError("❌ 无法连接到数据库，请检查配置。")
        self.performance_logger = PerformanceLogger(db_manager=self.db)
        print("✅ 数据库连接成功，所有组件已初始化。")
    def disconnect(self):
        if self.db and getattr(self.db, "_connected", False):
            self.db.disconnect()
            print("\n🔌 数据库连接已关闭。")
    def _get_issue_range_from_db(self) -> (Optional[int], Optional[int]):
        print("🔎 正在自动检测回测区间...")
        query = """
            SELECT ar.period_number FROM algorithm_recommendation ar
            INNER JOIN lottery_history lh ON ar.period_number = lh.period_number
            WHERE ar.analysis_basis IS NOT NULL AND ar.analysis_basis != '' AND ar.analysis_basis != 'null'
            GROUP BY ar.period_number
        """
        results = self.db.execute_query(query)
        if not results: return None, None
        issues = sorted([int(r['period_number']) for r in results])
        start, end = issues[0], issues[-1]
        print(f"➡️  自动检测到有效区间: {start} → {end}")
        return start, end
    def _get_model_outputs_for_issue(self, issue: str) -> Dict[str, Any]:
        query = "SELECT analysis_basis FROM algorithm_recommendation WHERE period_number = %s LIMIT 1"
        result = self.db.execute_query(query, (issue,))
        model_outputs = {}
        if not result or not result[0].get('analysis_basis'): return model_outputs
        try:
            raw_data_str = result[0]['analysis_basis']
            if not raw_data_str or raw_data_str.lower() == 'null': return model_outputs
            raw_data = json.loads(raw_data_str)
            if 'dynamic_ensemble_optimizer' in raw_data:
                 algorithms_data = raw_data['dynamic_ensemble_optimizer'].get('model_outputs', {})
            else:
                 algorithms_data = raw_data
            for model_name, prediction_data in algorithms_data.items():
                front = prediction_data.get('front_area', {}).get('numbers', [])
                back = prediction_data.get('back_area', {}).get('numbers', [])
                confidence = prediction_data.get('confidence', 0.5)
                if not front or not back: continue
                model_outputs[model_name] = {"front_numbers": front, "back_numbers": back, "confidence": confidence}
                self._all_model_names.add(model_name)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"  - 🔴 错误: 解析期号 {issue} 的 analysis_basis 字段失败: {e}")
        return model_outputs

    def run(self, start_issue: int, end_issue: int):
        """执行回测和学习的主循环。"""
        print(f"\n▶️  开始回测与学习, 区间: {start_issue} → {end_issue}, 共 {end_issue - start_issue + 1} 期")

        # <<< 关键修正 2/2 >>>
        # 调用 get_dao 时，传递 LotteryHistoryDAO 这个类，而不是 'LotteryHistoryDAO' 字符串
        history_dao = self.db.get_dao(LotteryHistoryDAO)

        for issue in range(start_issue, end_issue + 1):
            issue_str = str(issue)
            try:
                print("\n" + "-" * 70)
                print(f"🔎 处理期号: {issue_str} ({issue - start_issue + 1}/{end_issue - start_issue + 1})")
                actual_draw = history_dao.get_by_period(issue_str)
                if not actual_draw:
                    print(f"  - ⏸️  跳过: 未找到期号 {issue_str} 的开奖历史。")
                    continue
                model_outputs = self._get_model_outputs_for_issue(issue_str)
                if not model_outputs:
                    print(f"  - ⏸️  跳过: 未找到期号 {issue_str} 的原始算法预测 (analysis_basis 字段为空或解析失败)。")
                    continue
                print(f"  - 🧠 找到 {len(model_outputs)} 个算法预测，正在调用 PerformanceLogger 进行评估和学习...")
                eval_report = self.performance_logger.evaluate_and_update(
                    issue=issue_str,
                    model_outputs=model_outputs,
                    actual_draw=actual_draw
                )
                print(f"  - ✅ PerformanceLogger 处理完毕。返回的命中率报告: {eval_report}")
                if eval_report:
                    row = {'issue': issue_str, 'num_models': len(model_outputs)}
                    scores = list(eval_report.values())
                    best_model = max(eval_report, key=eval_report.get) if eval_report else "N/A"
                    row.update({
                        'avg_hit_rate': sum(scores) / len(scores) if scores else 0.0,
                        'best_model_by_hit_rate': best_model,
                        'best_hit_rate': eval_report.get(best_model, 0.0),
                        **{f"hit_rate_{model}": rate for model, rate in eval_report.items()}
                    })
                    self.summary_rows.append(row)
                if self.sleep_interval > 0:
                    time.sleep(self.sleep_interval)
            except KeyboardInterrupt:
                print("\n⛔ 用户中断。正在停止并导出已有结果...")
                break
            except Exception as e:
                print(f"❌ 处理期号 {issue_str} 时发生严重错误: {e}")
                traceback.print_exc()
        self._export_summary_csv()
        print("\n✅ 回测学习任务完成。`algorithm_performance` 表已由 PerformanceLogger 更新！")

    def _export_summary_csv(self):
        if not self.summary_rows:
            print("（无回测摘要可导出）")
            return
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = f"backtest_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        fieldnames = ['issue', 'num_models', 'avg_hit_rate', 'best_model_by_hit_rate', 'best_hit_rate']
        score_fields = sorted([f"hit_rate_{name}" for name in self._all_model_names])
        fieldnames.extend(score_fields)
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, restval='N/A')
            writer.writeheader()
            writer.writerows(self.summary_rows)
        print(f"📁 回测摘要已成功导出到: {filepath}")

# --- main 函数部分保持不变 ---
def parse_args():
    p = argparse.ArgumentParser(description="回测与学习引擎：驱动 PerformanceLogger 评估历史预测，更新数据库中的性能与权重。")
    p.add_argument("--start", type=int, help="开始期号")
    p.add_argument("--end", type=int, help="结束期号")
    p.add_argument("--auto", action="store_true", help="自动检测数据库中所有可评估的期号范围。")
    return p.parse_args()
def main():
    args = parse_args()
    runner = BacktestRunner(DB_CONFIG)
    try:
        runner.connect()
        start, end = (None, None)
        if args.auto:
            start, end = runner._get_issue_range_from_db()
        else:
            start, end = args.start, args.end
        if not start or not end:
            print("❌ 错误: 无法确定回测区间。请确保 `algorithm_recommendation` 表中有带 `analysis_basis` 的记录，且 `lottery_history` 中有对应开奖数据。")
            return
        runner.run(start_issue=start, end_issue=end)
    except Exception as e:
        print(f"\n❌ 任务失败: {e}")
        traceback.print_exc()
    finally:
        runner.disconnect()

if __name__ == "__main__":
    main()