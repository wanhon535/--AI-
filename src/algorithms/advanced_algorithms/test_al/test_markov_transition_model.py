# test_markov_transition_model.py
import sys
import os
# 马尔代夫模型测试脚本
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG

# 导入马尔可夫模型
try:
    from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel

    MARKOV_AVAILABLE = True
except ImportError as e:
    print(f"❌ 无法导入马尔可夫模型: {e}")
    MARKOV_AVAILABLE = False


def test_markov_transition_model():
    """测试马尔可夫转移模型"""
    print("=== 测试马尔可夫转移模型 ===")

    if not MARKOV_AVAILABLE:
        print("❌ 马尔可夫模型不可用，请先实现该算法")
        return

    # 创建预测器实例
    predictor = MarkovTransitionModel()
    print(f"算法名称: {predictor.name}")
    print(f"版本: {predictor.version}")

    try:
        # 从数据库获取真实历史数据
        print("\n1. 连接数据库并获取历史数据...")
        db_manager = DatabaseManager(**DB_CONFIG)

        # 获取历史数据 - 马尔可夫模型需要足够的数据来建立转移矩阵
        history_data = db_manager.get_all_lottery_history(limit=200)
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
        print("\n2. 训练马尔可夫模型...")
        train_success = predictor.train(history_data)
        print(f"训练状态: {'✅ 成功' if train_success else '❌ 失败'}")
        print(f"模型已训练: {predictor.is_trained}")

        if not train_success:
            print("❌ 训练失败，退出测试")
            return

        # 测试预测
        print("\n3. 进行马尔可夫预测...")
        result = predictor.predict(history_data)

        if 'error' in result:
            print(f"❌ 预测失败: {result['error']}")
            return

        # 检查结果结构
        print("\n4. 检查预测结果:")
        print(f"算法名称: {result.get('algorithm')}")
        print(f"版本: {result.get('version')}")
        print(f"置信度: {result.get('recommendations', [{}])[0].get('confidence', 'N/A')}")

        # 显示前区号码评分
        recommendations = result.get('recommendations', [{}])[0]
        front_scores = recommendations.get('front_number_scores', [])
        back_scores = recommendations.get('back_number_scores', [])

        print(f"\n5. 前区号码马尔可夫评分 (前15个):")
        for i, score_item in enumerate(front_scores[:15]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        print(f"\n6. 后区号码马尔可夫评分 (前8个):")
        for i, score_item in enumerate(back_scores[:8]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        # 基本验证
        print(f"\n7. 基本验证:")
        print(f"前区号码数量: {len(front_scores)} (应为35)")
        print(f"后区号码数量: {len(back_scores)} (应为12)")
        print(f"评分范围正常: {all(0 <= item['score'] <= 1 for item in front_scores + back_scores)}")

        # 分析转移概率特征
        print(f"\n8. 马尔可夫特征分析:")
        front_top5 = front_scores[:5]
        back_top3 = back_scores[:3]

        print("   前区最可能号码:")
        for item in front_top5:
            print(f"     号码 {item['number']}: 转移概率评分 {item['score']:.4f}")

        print("   后区最可能号码:")
        for item in back_top3:
            print(f"     号码 {item['number']}: 转移概率评分 {item['score']:.4f}")

        # 如果有转移矩阵分析信息，显示出来
        analysis = result.get('analysis', {})
        if 'transition_matrix_info' in analysis:
            matrix_info = analysis['transition_matrix_info']
            print(f"\n9. 转移矩阵信息:")
            print(f"   矩阵维度: {matrix_info.get('dimensions', 'N/A')}")
            print(f"   稀疏度: {matrix_info.get('sparsity', 'N/A')}")
            print(f"   平均转移概率: {matrix_info.get('avg_transition_prob', 'N/A')}")

        print("\n=== 马尔可夫转移模型测试完成 ===")

        return result

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_markov_transition_model()