# run_backtest_simulation.py
import json
import os
import sys
from datetime import datetime

# 环境设置
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.engine.performance_logger import PerformanceLogger


class BacktestRunner:
    def __init__(self, db_config):
        self.db_config = db_config
        self.db_manager = None
        self.performance_logger = None

    def connect(self):
        """连接数据库"""
        self.db_manager = DatabaseManager(**self.db_config)
        if not self.db_manager.connect():
            raise ConnectionError("数据库连接失败")
        self.performance_logger = PerformanceLogger(db_manager=self.db_manager)
        return True

    def disconnect(self):
        """断开数据库连接"""
        if self.db_manager:
            self.db_manager.disconnect()

    def _get_issue_range_from_db(self):
        """从数据库获取期号范围"""
        query = """
            SELECT MIN(period_number) as start, MAX(period_number) as end 
            FROM lottery_history 
            WHERE period_number REGEXP '^[0-9]+$'
        """
        result = self.db_manager.execute_query(query)
        if result and result[0]['start'] and result[0]['end']:
            return result[0]['start'], result[0]['end']
        return None, None

    def _get_model_outputs_for_issue(self, issue_str: str):
        """修复：正确解析analysis_basis字段"""
        query = """
            SELECT analysis_basis, algorithm_parameters, model_weights
            FROM algorithm_recommendation 
            WHERE period_number = %s AND analysis_basis IS NOT NULL
        """
        records = self.db_manager.execute_query(query, (issue_str,))

        if not records:
            print(f"  - ⏸️  跳过: 未找到期号 {issue_str} 的原始算法预测")
            return None

        analysis_basis = records[0]['analysis_basis']

        # 修复：正确处理analysis_basis字段（可能是字符串或字典）
        if isinstance(analysis_basis, str):
            try:
                analysis_basis = json.loads(analysis_basis)
            except json.JSONDecodeError:
                print(f"  - ❌ 解析analysis_basis失败，期号: {issue_str}")
                return None

        if not analysis_basis or not isinstance(analysis_basis, dict):
            print(f"  - ⏸️  跳过: 期号 {issue_str} 的analysis_basis格式不正确")
            return None

        # 提取individual_predictions
        individual_predictions = analysis_basis.get('individual_predictions', {})

        model_outputs = {}
        for algo_name, prediction in individual_predictions.items():
            # 确保prediction是字典
            if isinstance(prediction, str):
                try:
                    prediction = json.loads(prediction)
                except json.JSONDecodeError:
                    continue

            if isinstance(prediction, dict):
                # 安全地提取号码
                front_numbers = prediction.get('front_area', [])
                back_numbers = prediction.get('back_area', [])

                # 如果号码是字符串，转换为列表
                if isinstance(front_numbers, str):
                    front_numbers = [int(x.strip()) for x in front_numbers.split(',') if x.strip().isdigit()]
                if isinstance(back_numbers, str):
                    back_numbers = [int(x.strip()) for x in back_numbers.split(',') if x.strip().isdigit()]

                model_outputs[algo_name] = {
                    'front_area': front_numbers,
                    'back_area': back_numbers
                }

        return model_outputs if model_outputs else None

    def _get_actual_numbers_for_issue(self, issue_str: str):
        """获取实际开奖号码"""
        query = """
            SELECT front_area_1, front_area_2, front_area_3, front_area_4, front_area_5,
                   back_area_1, back_area_2
            FROM lottery_history 
            WHERE period_number = %s
        """
        records = self.db_manager.execute_query(query, (issue_str,))

        if not records:
            return None, None

        record = records[0]
        front_actual = [
            record['front_area_1'], record['front_area_2'], record['front_area_3'],
            record['front_area_4'], record['front_area_5']
        ]
        back_actual = [record['back_area_1'], record['back_area_2']]

        return front_actual, back_actual

    def _calculate_hit_score(self, predicted_front, predicted_back, actual_front, actual_back):
        """计算命中分数"""
        front_hits = len(set(predicted_front) & set(actual_front))
        back_hits = len(set(predicted_back) & set(actual_back))

        # 简单的命中评分算法
        score = (front_hits * 2) + (back_hits * 3)  # 后区命中权重更高
        return score, front_hits, back_hits

    def run(self, start_issue, end_issue):
        """运行回测"""
        print(f"开始回测与学习, 区间: {start_issue} → {end_issue}")

        # 获取期号列表
        query = """
            SELECT period_number FROM lottery_history 
            WHERE period_number BETWEEN %s AND %s 
            AND period_number REGEXP '^[0-9]+$'
            ORDER BY period_number
        """
        issues = self.db_manager.execute_query(query, (start_issue, end_issue))

        if not issues:
            print("❌ 未找到指定区间的期号数据")
            return

        total_issues = len(issues)
        print(f"共 {total_issues} 期")

        processed_count = 0
        skipped_count = 0
        error_count = 0

        for i, issue_record in enumerate(issues, 1):
            issue_str = issue_record['period_number']
            print(f"\n{'=' * 60}")
            print(f"🔎 处理期号: {issue_str} ({i}/{total_issues})")

            try:
                # 1. 获取模型输出
                model_outputs = self._get_model_outputs_for_issue(issue_str)
                if not model_outputs:
                    skipped_count += 1
                    continue

                # 2. 获取实际开奖号码
                actual_front, actual_back = self._get_actual_numbers_for_issue(issue_str)
                if not actual_front or not actual_back:
                    print(f"  - ⏸️  跳过: 未找到期号 {issue_str} 的实际开奖数据")
                    skipped_count += 1
                    continue

                # 3. 为每个算法计算命中率并更新性能
                for algo_name, prediction in model_outputs.items():
                    predicted_front = prediction.get('front_area', [])
                    predicted_back = prediction.get('back_area', [])

                    if not predicted_front or not predicted_back:
                        continue

                    hit_score, front_hits, back_hits = self._calculate_hit_score(
                        predicted_front, predicted_back, actual_front, actual_back
                    )

                    # 4. 更新算法性能
                    try:
                        # 修复：使用正确的DAO方法
                        performance_data = {
                            'algorithm_version': f"{algo_name}_1.0",
                            'period_number': issue_str,
                            'predictions': json.dumps(prediction, ensure_ascii=False),
                            'confidence_score': 0.5,  # 默认置信度
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }

                        # 使用performance_logger的dao来插入
                        self.performance_logger.dao.insert_algorithm_performance(performance_data)
                        print(f"  - ✅ {algo_name}: 前区命中 {front_hits}/5, 后区命中 {back_hits}/2, 分数: {hit_score}")

                    except Exception as e:
                        print(f"  - ❌ 更新{algo_name}性能失败: {e}")
                        error_count += 1

                processed_count += 1

            except Exception as e:
                print(f"❌ 处理期号 {issue_str} 时发生严重错误: {e}")
                import traceback
                traceback.print_exc()
                error_count += 1

        # 输出总结
        print(f"\n{'=' * 60}")
        print("📊 回测总结:")
        print(f"  - 总期数: {total_issues}")
        print(f"  - 成功处理: {processed_count}")
        print(f"  - 跳过: {skipped_count}")
        print(f"  - 错误: {error_count}")

        if processed_count > 0:
            print("✅ 回测学习任务完成。`algorithm_performance` 表已更新！")
        else:
            print("⚠️  没有成功处理任何期号，请检查数据完整性")


if __name__ == "__main__":
    DB_CONFIG = dict(
        host='localhost', user='root', password='123456789',
        database='lottery_analysis_system', port=3309
    )

    runner = BacktestRunner(DB_CONFIG)
    try:
        runner.connect()
        start, end = runner._get_issue_range_from_db()
        if start and end:
            runner.run(start, end)
        else:
            print("❌ 无法获取期号范围")
    finally:
        runner.disconnect()