# test_intelligent_pattern_recognizer.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG

# 尝试导入智能模式识别器
try:
    from src.algorithms.intelligent_pattern_recognizer import IntelligentPatternRecognizer

    PATTERN_AVAILABLE = True
except ImportError as e:
    print(f"❌ 无法导入智能模式识别器: {e}")
    PATTERN_AVAILABLE = False


def test_intelligent_pattern_recognizer():
    """测试智能模式识别器"""
    print("=== 测试智能模式识别器 ===")

    if not PATTERN_AVAILABLE:
        print("❌ 智能模式识别器不可用，请先实现该算法")
        create_pattern_recognition_demo()
        return

    # 创建预测器实例
    predictor = IntelligentPatternRecognizer()
    print(f"算法名称: {predictor.name}")
    print(f"版本: {predictor.version}")

    try:
        # 从数据库获取真实历史数据
        print("\n1. 连接数据库并获取历史数据...")
        db_manager = DatabaseManager(**DB_CONFIG)

        # 获取历史数据
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
        print("\n2. 训练模式识别模型...")
        train_success = predictor.train(history_data)
        print(f"训练状态: {'✅ 成功' if train_success else '❌ 失败'}")
        print(f"模型已训练: {predictor.is_trained}")

        if not train_success:
            print("❌ 训练失败，退出测试")
            return

        # 测试预测
        print("\n3. 进行模式识别预测...")
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

        print(f"\n5. 前区号码模式识别评分 (前15个):")
        for i, score_item in enumerate(front_scores[:15]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        print(f"\n6. 后区号码模式识别评分 (前8个):")
        for i, score_item in enumerate(back_scores[:8]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        # 基本验证
        print(f"\n7. 基本验证:")
        print(f"前区号码数量: {len(front_scores)} (应为35)")
        print(f"后区号码数量: {len(back_scores)} (应为12)")
        print(f"评分范围正常: {all(0 <= item['score'] <= 1 for item in front_scores + back_scores)}")

        # 分析模式特征
        print(f"\n8. 模式特征分析:")
        front_top5 = front_scores[:5]
        back_top3 = back_scores[:3]

        print("   前区最可能号码:")
        for item in front_top5:
            print(f"     号码 {item['number']}: 模式评分 {item['score']:.4f}")

        print("   后区最可能号码:")
        for item in back_top3:
            print(f"     号码 {item['number']}: 模式评分 {item['score']:.4f}")

        # 如果有模式识别相关信息，显示出来
        analysis = result.get('analysis', {})
        if 'pattern_analysis' in analysis:
            pattern_info = analysis['pattern_analysis']
            print(f"\n9. 模式识别信息:")
            print(f"   发现的模式数量: {pattern_info.get('pattern_count', 'N/A')}")
            print(f"   最强模式置信度: {pattern_info.get('strongest_pattern_confidence', 'N/A')}")

            # 显示一些识别到的模式
            if 'identified_patterns' in pattern_info:
                patterns = pattern_info['identified_patterns'][:3]  # 显示前3个模式
                print(f"   识别到的模式示例:")
                for i, pattern in enumerate(patterns):
                    print(f"     模式{i + 1}: {pattern.get('description', 'N/A')}")

        print("\n=== 智能模式识别器测试完成 ===")

        return result

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


def create_pattern_recognition_demo():
    """创建模式识别演示"""
    print("\n🔍 创建模式识别演示...")

    try:
        from src.database.database_manager import DatabaseManager
        import numpy as np

        db_manager = DatabaseManager(**DB_CONFIG)
        history_data = db_manager.get_all_lottery_history(limit=100)

        if len(history_data) < 20:
            print("❌ 数据量不足，无法进行模式识别")
            return

        print(f"使用 {len(history_data)} 条记录进行模式识别分析")

        # 简单演示：分析奇偶模式、大小模式、和值模式等
        pattern_analysis = analyze_basic_patterns(history_data)

        print("✅ 基础模式分析完成")
        print(f"   常见奇偶比例: {pattern_analysis['common_parity_ratio']}")
        print(f"   常见大小比例: {pattern_analysis['common_size_ratio']}")
        print(f"   和值范围: {pattern_analysis['sum_range']}")

        # 生成基于模式的预测
        simulate_pattern_prediction(history_data, pattern_analysis)

    except Exception as e:
        print(f"❌ 模式识别演示失败: {e}")


def analyze_basic_patterns(history_data):
    """分析基础模式"""
    parity_ratios = []
    size_ratios = []
    sums = []

    for record in history_data:
        # 奇偶比例
        front_odd = sum(1 for num in record.front_area if num % 2 == 1)
        parity_ratios.append(f"{front_odd}:{5 - front_odd}")

        # 大小比例 (以18为界)
        front_big = sum(1 for num in record.front_area if num > 18)
        size_ratios.append(f"{front_big}:{5 - front_big}")

        # 和值
        sums.append(sum(record.front_area))

    return {
        'common_parity_ratio': max(set(parity_ratios), key=parity_ratios.count),
        'common_size_ratio': max(set(size_ratios), key=size_ratios.count),
        'sum_range': (min(sums), max(sums))
    }


def simulate_pattern_prediction(history_data, pattern_analysis):
    """模拟基于模式的预测"""
    print("\n🎯 模拟模式识别预测结果:")

    # 基于常见模式生成预测
    common_parity = pattern_analysis['common_parity_ratio']
    common_size = pattern_analysis['common_size_ratio']

    # 解析常见比例
    odd_count = int(common_parity.split(':')[0])
    big_count = int(common_size.split(':')[0])

    # 根据模式选择号码（这里简化处理）
    front_scores = []
    for num in range(1, 36):
        score = 0.0
        # 如果奇偶比例需要奇数，且当前号码是奇数，则加分
        if odd_count >= 3 and num % 2 == 1:
            score += 0.3
        elif odd_count <= 2 and num % 2 == 0:
            score += 0.3

        # 如果大小比例需要大数，且当前号码>18，则加分
        if big_count >= 3 and num > 18:
            score += 0.3
        elif big_count <= 2 and num <= 18:
            score += 0.3

        # 基础分
        score += 0.1

        front_scores.append({'number': num, 'score': score})

    back_scores = [{'number': i, 'score': 0.5} for i in range(1, 13)]

    front_scores.sort(key=lambda x: x['score'], reverse=True)
    back_scores.sort(key=lambda x: x['score'], reverse=True)

    print("前区模式预测 (前10个):")
    for item in front_scores[:10]:
        print(f"  号码 {item['number']:2d}: {item['score']:.4f}")

    print("后区模式预测 (前5个):")
    for item in back_scores[:5]:
        print(f"  号码 {item['number']:2d}: {item['score']:.4f}")


if __name__ == "__main__":
    test_intelligent_pattern_recognizer()