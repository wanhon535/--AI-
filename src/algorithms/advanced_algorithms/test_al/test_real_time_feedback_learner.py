# test_real_time_feedback_learner.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG

# 尝试导入实时反馈学习器
try:
    from src.algorithms.real_time_feedback_learner import RealTimeFeedbackLearner

    FEEDBACK_AVAILABLE = True
except ImportError as e:
    print(f"❌ 无法导入实时反馈学习器: {e}")
    FEEDBACK_AVAILABLE = False


def test_real_time_feedback_learner():
    """测试实时反馈学习器"""
    print("=== 测试实时反馈学习器 ===")

    if not FEEDBACK_AVAILABLE:
        print("❌ 实时反馈学习器不可用，请先实现该算法")
        return

    # 创建预测器实例
    predictor = RealTimeFeedbackLearner()
    print(f"算法名称: {predictor.name}")
    print(f"版本: {predictor.version}")

    try:
        # 从数据库获取真实历史数据
        print("\n1. 连接数据库并获取历史数据...")
        db_manager = DatabaseManager(**DB_CONFIG)

        # 获取历史数据
        history_data = db_manager.get_all_lottery_history(limit=100)
        print(f"从数据库获取到 {len(history_data)} 条历史记录")

        if not history_data:
            print("❌ 数据库中没有历史数据，测试终止")
            return

        # 显示数据范围
        if len(history_data) > 0:
            first_period = history_data[0].period_number
            last_period = history_data[-1].period_number
            print(f"数据范围: 第{first_period}期 - 第{last_period}期")

        # 测试训练
        print("\n2. 训练实时反馈学习器...")
        train_success = predictor.train(history_data)
        print(f"训练状态: {'✅ 成功' if train_success else '❌ 失败'}")
        print(f"模型已训练: {predictor.is_trained}")

        if not train_success:
            print("❌ 训练失败，退出测试")
            return

        # 测试预测
        print("\n3. 进行实时反馈预测...")
        result = predictor.predict(history_data)

        if 'error' in result:
            print(f"❌ 预测失败: {result['error']}")
            return

        # 检查结果结构
        print("\n4. 检查预测结果:")
        print(f"算法名称: {result.get('algorithm')}")
        print(f"版本: {result.get('version')}")

        # 显示学习状态
        analysis = result.get('analysis', {})
        print(f"学习状态: {analysis.get('learning_state', 'N/A')}")
        print(f"成功模式数量: {analysis.get('success_patterns_count', 'N/A')}")
        print(f"当前学习率: {analysis.get('current_learning_rate', 'N/A')}")

        # 显示推荐结果
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n5. 推荐组合:")
            for i, rec in enumerate(recommendations):
                print(f"  组合 {i + 1}:")
                print(f"    前区号码: {rec.get('front_numbers', [])}")
                print(f"    后区号码: {rec.get('back_numbers', [])}")
                print(f"    置信度: {rec.get('confidence', 'N/A')}")
                print(f"    策略来源: {rec.get('strategy_source', 'N/A')}")

        # 模拟反馈学习
        print(f"\n6. 模拟反馈学习过程...")
        if len(history_data) >= 2:
            # 使用最近一期作为模拟的"实际结果"
            latest_record = history_data[-1]

            # 模拟一个预测结果
            simulated_prediction = {
                'recommendations': [{
                    'front_numbers': [1, 5, 10, 15, 20],
                    'back_numbers': [3, 7],
                    'confidence': 0.75
                }]
            }

            print(
                f"  模拟预测: 前区{simulated_prediction['recommendations'][0]['front_numbers']}, 后区{simulated_prediction['recommendations'][0]['back_numbers']}")
            print(f"  实际开奖: 前区{latest_record.front_area}, 后区{latest_record.back_area}")

            # 处理反馈
            try:
                predictor.process_feedback(simulated_prediction, latest_record)
                print("  ✅ 反馈学习完成")

                # 再次预测看是否有变化
                print(f"\n7. 反馈学习后的新预测...")
                new_result = predictor.predict(history_data)
                new_recommendations = new_result.get('recommendations', [])

                if new_recommendations:
                    print(f"  新推荐组合:")
                    for i, rec in enumerate(new_recommendations):
                        print(
                            f"    组合 {i + 1}: 前区{rec.get('front_numbers', [])}, 后区{rec.get('back_numbers', [])}")

            except Exception as e:
                print(f"  ❌ 反馈学习失败: {e}")

        print("\n=== 实时反馈学习器测试完成 ===")

        return result

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_real_time_feedback_learner()