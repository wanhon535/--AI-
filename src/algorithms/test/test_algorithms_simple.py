# test_algorithms_simple.py
"""
简洁算法测试器 - 直接连接数据库测试算法性能
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.database_manager import DatabaseManager
from src.model.lottery_models import LotteryHistory


class SimpleAlgorithmTester:
    """简洁算法测试器"""

    def __init__(self):
        self.db = DatabaseManager(
            host='localhost', port=3309, user='root',
            password='123456789', database='lottery_analysis_system'
        )

    def test_algorithm(self, algorithm_class, data_limit=100):
        """测试单个算法"""
        print(f"\n🧪 测试算法: {algorithm_class.name}")

        # 1. 从数据库加载数据
        history_data = self.db.get_all_lottery_history(limit=data_limit)
        print(f"📊 加载 {len(history_data)} 条历史数据")

        if len(history_data) < 20:
            print("❌ 数据不足，至少需要20条数据")
            return

        # 2. 划分训练集和测试集 (80%训练, 20%测试)
        split_idx = int(len(history_data) * 0.8)
        train_data = history_data[:split_idx]
        test_data = history_data[split_idx:]

        # 3. 初始化并训练算法
        algorithm = algorithm_class()
        algorithm.train(train_data)

        # 4. 测试算法
        hits = []
        for i, test_record in enumerate(test_data):
            # 使用到当前期之前的所有数据
            current_data = history_data[:split_idx + i]
            prediction = algorithm.predict(current_data)

            # 计算命中
            hit_info = self._calculate_hit(prediction, test_record)
            hits.append(hit_info)

        # 5. 分析结果
        self._analyze_results(hits, algorithm_class.name)
        return hits

    def _calculate_hit(self, prediction, actual_record):
        """计算单次预测命中情况"""
        try:
            if 'error' in prediction:
                return {"error": prediction['error']}

            # 提取预测号码
            pred_front = []
            pred_back = []

            if 'recommendations' in prediction and prediction['recommendations']:
                rec = prediction['recommendations'][0]

                # 处理两种输出格式
                if 'front_numbers' in rec:
                    pred_front = rec['front_numbers'][:5]  # 取前5个
                elif 'front_number_scores' in rec:
                    scores = sorted(rec['front_number_scores'],
                                    key=lambda x: x['score'], reverse=True)
                    pred_front = [item['number'] for item in scores[:5]]

                if 'back_numbers' in rec:
                    pred_back = rec['back_numbers'][:2]  # 取前2个
                elif 'back_number_scores' in rec:
                    scores = sorted(rec['back_number_scores'],
                                    key=lambda x: x['score'], reverse=True)
                    pred_back = [item['number'] for item in scores[:2]]

            # 计算命中
            front_hit = len(set(pred_front) & set(actual_record.front_area))
            back_hit = len(set(pred_back) & set(actual_record.back_area))

            return {
                "period": actual_record.period_number,
                "front_hit": front_hit,
                "back_hit": back_hit,
                "total_hit": front_hit + back_hit,
                "predicted_front": pred_front,
                "predicted_back": pred_back,
                "actual_front": actual_record.front_area,
                "actual_back": actual_record.back_area
            }

        except Exception as e:
            return {"error": str(e)}

    def _analyze_results(self, hits, algorithm_name):
        """分析并打印结果"""
        valid_hits = [h for h in hits if 'error' not in h]

        if not valid_hits:
            print("❌ 没有有效测试结果")
            return

        # 计算统计
        front_hits = [h['front_hit'] for h in valid_hits]
        back_hits = [h['back_hit'] for h in valid_hits]
        total_hits = [h['total_hit'] for h in valid_hits]

        # 命中率
        front_hit_rate = sum(front_hits) / (len(valid_hits) * 5)
        back_hit_rate = sum(back_hits) / (len(valid_hits) * 2)

        # 命中分布
        front_dist = {f"命中{i}个": front_hits.count(i) for i in range(6)}
        back_dist = {f"命中{i}个": back_hits.count(i) for i in range(3)}

        # 打印结果
        print(f"\n📈 {algorithm_name} 测试结果:")
        print(f"   测试期数: {len(valid_hits)}")
        print(f"   前区命中率: {front_hit_rate:.3f}")
        print(f"   后区命中率: {back_hit_rate:.3f}")
        print(f"   前区命中分布: {front_dist}")
        print(f"   后区命中分布: {back_dist}")
        print(f"   平均每期命中: {sum(total_hits) / len(total_hits):.2f} 个号码")

        # 高命中统计
        high_front_hits = sum(1 for h in front_hits if h >= 2)
        high_back_hits = sum(1 for h in back_hits if h >= 1)
        print(f"   前区命中≥2个的概率: {high_front_hits / len(valid_hits):.3f}")
        print(f"   后区命中≥1个的概率: {high_back_hits / len(valid_hits):.3f}")


# 使用示例
if __name__ == "__main__":
    tester = SimpleAlgorithmTester()

    # 测试不同的算法 - 只需要替换这里的导入
    try:
        from src.algorithms.statistical_algorithms import FrequencyAnalysisAlgorithm

        tester.test_algorithm(FrequencyAnalysisAlgorithm, data_limit=100)
    except ImportError as e:
        print(f"❌ 导入算法失败: {e}")

    try:
        from src.algorithms.statistical_algorithms import HotColdNumberAlgorithm

        tester.test_algorithm(HotColdNumberAlgorithm, data_limit=100)
    except ImportError as e:
        print(f"❌ 导入算法失败: {e}")

    try:
        from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor

        tester.test_algorithm(BayesianNumberPredictor, data_limit=100)
    except ImportError as e:
        print(f"❌ 导入算法失败: {e}")