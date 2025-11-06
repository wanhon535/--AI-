# test_intelligent_neural.py
import sys
import os
# 神经网络预测器测试脚本
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.advanced_algorithms.neural_lottery_predictor import NeuralLotteryPredictor
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG


def test_intelligent_neural():
    """测试智能推理神经网络"""
    print("=== 测试智能推理神经网络预测器 ===")

    # 创建预测器实例
    predictor = NeuralLotteryPredictor()
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
        print("\n2. 训练智能神经网络模型...")
        train_success = predictor.train(history_data)
        print(f"训练状态: {'✅ 成功' if train_success else '❌ 失败'}")
        print(f"模型已训练: {predictor.is_trained}")

        if not train_success:
            print("❌ 训练失败，退出测试")
            return

        # 测试预测
        print("\n3. 进行智能推理预测...")
        result = predictor.predict(history_data)

        if 'error' in result:
            print(f"❌ 预测失败: {result['error']}")
            return

        # 检查结果结构
        print("\n4. 检查预测结果:")
        print(f"算法名称: {result.get('algorithm')}")
        print(f"版本: {result.get('version')}")
        print(f"置信度: {result.get('recommendations', [{}])[0].get('confidence', 'N/A')}")

        # 显示推理摘要
        reasoning_summary = result.get('recommendations', [{}])[0].get('reasoning_summary', '')
        print(f"推理摘要: {reasoning_summary}")

        # 显示前区号码评分和推理
        recommendations = result.get('recommendations', [{}])[0]
        front_scores = recommendations.get('front_number_scores', [])
        back_scores = recommendations.get('back_number_scores', [])

        print(f"\n5. 前区号码智能评分 (前10个):")
        for i, score_item in enumerate(front_scores[:10]):
            reasoning = " | ".join(score_item.get('reasoning', []))
            factors = ", ".join(score_item.get('confidence_factors', []))
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")
            print(f"      推理: {reasoning}")
            print(f"      因素: {factors}")
            print()

        print(f"\n6. 后区号码智能评分 (前5个):")
        for i, score_item in enumerate(back_scores[:5]):
            reasoning = " | ".join(score_item.get('reasoning', []))
            factors = ", ".join(score_item.get('confidence_factors', []))
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")
            print(f"      推理: {reasoning}")
            print(f"      因素: {factors}")
            print()

        # 显示分析详情
        analysis = result.get('analysis', {})
        print(f"\n7. 多维度分析详情:")

        multi_analysis = analysis.get('multi_dimensional_analysis', {})
        if 'hot_cold' in multi_analysis:
            hc = multi_analysis['hot_cold']
            print(
                f"   热号分析: 前区{len(hc['front']['hot'])}热/{len(hc['front']['warm'])}温/{len(hc['front']['cold'])}冷")
            print(f"           后区{len(hc['back']['hot'])}热/{len(hc['back']['warm'])}温/{len(hc['back']['cold'])}冷")

        if 'omission' in multi_analysis:
            om = multi_analysis['omission']
            print(f"   遗漏分析: 前区平均遗漏{om['avg_omission']['front']:.1f}期")
            print(f"           后区平均遗漏{om['avg_omission']['back']:.1f}期")

        # 显示预测备注
        notes = analysis.get('prediction_notes', [])
        if notes:
            print(f"\n8. 预测备注:")
            for note in notes:
                print(f"   💡 {note}")

        # 显示特征重要性
        feature_importance = analysis.get('feature_importance', {})
        if feature_importance:
            print(f"\n9. 特征重要性:")
            for feature, importance in feature_importance.items():
                print(f"   {feature}: {importance:.2f}")

        print("\n=== 智能推理神经网络测试完成 ===")

        return result

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_intelligent_neural()