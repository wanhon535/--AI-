# test_time_series_analyzer_fixed.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.advanced_algorithms.time_series_analyzer import TimeSeriesAnalyzer
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG

# 时序脚本测试
def test_time_series_analyzer():
    """测试修复后的时序分析器"""
    print("=== 测试时序分析器 (修复版) ===")

    # 创建预测器实例
    predictor = TimeSeriesAnalyzer()
    print(f"算法名称: {predictor.name}")
    print(f"版本: {predictor.version}")

    try:
        print("\n1. 连接数据库并获取历史数据...")
        db_manager = DatabaseManager(**DB_CONFIG)

        # 获取足够的历史数据进行时序分析
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
        print("\n2. 训练时序模型...")
        train_success = predictor.train(history_data)
        print(f"训练状态: {'✅ 成功' if train_success else '❌ 失败'}")
        print(f"模型已训练: {predictor.is_trained}")

        if not train_success:
            print("❌ 训练失败，退出测试")
            return

        # 测试预测
        print("\n3. 进行时序预测...")
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

        print(f"\n5. 前区号码时序评分 (前15个):")
        for i, score_item in enumerate(front_scores[:15]):
            trend_symbol = "↑" if score_item['trend_direction'] == 1 else "↓" if score_item[
                                                                                     'trend_direction'] == -1 else "→"
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f} {trend_symbol} "
                  f"(遗漏{score_item['omission']}期, 动量{score_item['momentum']:.3f})")

        print(f"\n6. 后区号码时序评分 (前8个):")
        for i, score_item in enumerate(back_scores[:8]):
            trend_symbol = "↑" if score_item['trend_direction'] == 1 else "↓" if score_item[
                                                                                     'trend_direction'] == -1 else "→"
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f} {trend_symbol} "
                  f"(遗漏{score_item['omission']}期, 动量{score_item['momentum']:.3f})")

        # 基本验证
        print(f"\n7. 基本验证:")
        print(f"前区号码数量: {len(front_scores)} (应为35)")
        print(f"后区号码数量: {len(back_scores)} (应为12)")
        print(f"评分范围正常: {all(0 <= item['score'] <= 1 for item in front_scores + back_scores)}")

        # 分析热门号码特征
        print(f"\n8. 时序特征分析:")
        front_top5 = front_scores[:5]
        back_top3 = back_scores[:3]

        print("   前区最热门号码特征:")
        for item in front_top5:
            status = "热号↑" if item['trend_direction'] == 1 else "冷号↓" if item['trend_direction'] == -1 else "温号→"
            print(f"     号码 {item['number']}: {status}, 遗漏{item['omission']}期, 评分{item['score']:.4f}")

        print("   后区最热门号码特征:")
        for item in back_top3:
            status = "热号↑" if item['trend_direction'] == 1 else "冷号↓" if item['trend_direction'] == -1 else "温号→"
            print(f"     号码 {item['number']}: {status}, 遗漏{item['omission']}期, 评分{item['score']:.4f}")

        # 时序分析参数
        print(f"\n9. 时序分析参数:")
        analysis = result.get('analysis', {})
        params = analysis.get('parameters_used', {})
        print(f"   短期窗口: {params.get('short_term_window')}期")
        print(f"   中期窗口: {params.get('medium_term_window')}期")
        print(f"   长期窗口: {params.get('long_term_window')}期")

        print("\n=== 时序分析器测试完成 ===")

        return result

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_time_series_analyzer()