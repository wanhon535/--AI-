# test_dynamic_ensemble_optimizer.py
import sys
import os

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG

# 尝试导入动态集成优化器
try:
    from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer

    ENSEMBLE_AVAILABLE = True
except ImportError as e:
    print(f"❌ 无法导入动态集成优化器: {e}")
    ENSEMBLE_AVAILABLE = False


def test_dynamic_ensemble_optimizer():
    """测试动态集成优化器"""
    print("=== 测试动态集成优化器 ===")

    if not ENSEMBLE_AVAILABLE:
        print("❌ 动态集成优化器不可用，请先实现该算法")
        create_ensemble_demo()
        return

    # 创建预测器实例
    predictor = DynamicEnsembleOptimizer()
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
        print("\n2. 训练集成优化器...")
        train_success = predictor.train(history_data)
        print(f"训练状态: {'✅ 成功' if train_success else '❌ 失败'}")
        print(f"模型已训练: {predictor.is_trained}")

        if not train_success:
            print("❌ 训练失败，退出测试")
            return

        # 测试预测
        print("\n3. 进行集成优化预测...")
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

        print(f"\n5. 前区集成优化评分 (前15个):")
        for i, score_item in enumerate(front_scores[:15]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        print(f"\n6. 后区集成优化评分 (前8个):")
        for i, score_item in enumerate(back_scores[:8]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        # 基本验证
        print(f"\n7. 基本验证:")
        print(f"前区号码数量: {len(front_scores)} (应为35)")
        print(f"后区号码数量: {len(back_scores)} (应为12)")
        print(f"评分范围正常: {all(0 <= item['score'] <= 1 for item in front_scores + back_scores)}")

        # 分析集成特征
        print(f"\n8. 集成优化分析:")
        front_top5 = front_scores[:5]
        back_top3 = back_scores[:3]

        print("   前区最可能号码:")
        for item in front_top5:
            print(f"     号码 {item['number']}: 集成评分 {item['score']:.4f}")

        print("   后区最可能号码:")
        for item in back_top3:
            print(f"     号码 {item['number']}: 集成评分 {item['score']:.4f}")

        # 如果有集成相关信息，显示出来
        analysis = result.get('analysis', {})
        if 'ensemble_info' in analysis:
            ensemble_info = analysis['ensemble_info']
            print(f"\n9. 集成优化信息:")
            print(f"   集成算法数量: {ensemble_info.get('algorithm_count', 'N/A')}")
            print(f"   最优权重分配: {ensemble_info.get('optimal_weights', 'N/A')}")

            # 显示集成的算法
            if 'algorithms_used' in ensemble_info:
                algorithms = ensemble_info['algorithms_used']
                print(f"   使用的算法: {', '.join(algorithms)}")

        print("\n=== 动态集成优化器测试完成 ===")

        return result

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


def create_ensemble_demo():
    """创建集成优化演示"""
    print("\n🔄 创建集成优化演示...")

    try:
        from src.database.database_manager import DatabaseManager
        import numpy as np

        db_manager = DatabaseManager(**DB_CONFIG)
        history_data = db_manager.get_all_lottery_history(limit=100)

        if len(history_data) < 20:
            print("❌ 数据量不足，无法进行集成优化")
            return

        print(f"使用 {len(history_data)} 条记录进行集成优化演示")

        # 模拟多个算法的结果
        algorithm_results = simulate_algorithm_results(history_data)

        # 进行集成优化
        ensemble_result = perform_ensemble_optimization(algorithm_results)

        print("✅ 集成优化完成")
        print(f"   集成算法数量: {len(algorithm_results)}")
        print(f"   最优权重: {ensemble_result['optimal_weights']}")

        # 显示集成结果
        display_ensemble_results(ensemble_result)

    except Exception as e:
        print(f"❌ 集成优化演示失败: {e}")


def simulate_algorithm_results(history_data):
    """模拟多个算法的结果"""
    algorithms = {
        'bayesian': {},
        'time_series': {},
        'markov': {},
        'graph_analysis': {},
        'pattern_recognition': {}
    }

    # 为每个算法生成模拟评分
    for algo_name in algorithms.keys():
        front_scores = []
        back_scores = []

        # 前区模拟评分
        for num in range(1, 36):
            # 基于历史频率生成基础分，加上算法特定的随机性
            base_score = get_base_frequency_score(num, history_data, 'front')
            algo_variation = np.random.normal(0, 0.1)  # 算法特异性
            score = max(0, min(1, base_score + algo_variation))
            front_scores.append({'number': num, 'score': score})

        # 后区模拟评分
        for num in range(1, 13):
            base_score = get_base_frequency_score(num, history_data, 'back')
            algo_variation = np.random.normal(0, 0.15)
            score = max(0, min(1, base_score + algo_variation))
            back_scores.append({'number': num, 'score': score})

        # 排序
        front_scores.sort(key=lambda x: x['score'], reverse=True)
        back_scores.sort(key=lambda x: x['score'], reverse=True)

        algorithms[algo_name] = {
            'front_scores': front_scores,
            'back_scores': back_scores,
            'confidence': np.random.uniform(0.6, 0.9)
        }

    return algorithms


def get_base_frequency_score(number, history_data, area_type):
    """获取基础频率评分"""
    count = 0
    for record in history_data:
        numbers = record.front_area if area_type == 'front' else record.back_area
        if number in numbers:
            count += 1

    return count / len(history_data)


def perform_ensemble_optimization(algorithm_results):
    """执行集成优化"""
    # 基于算法置信度计算权重
    total_confidence = sum(result['confidence'] for result in algorithm_results.values())
    weights = {algo: result['confidence'] / total_confidence for algo, result in algorithm_results.items()}

    # 集成前区评分
    front_ensemble = ensemble_scores(algorithm_results, 'front_scores', weights)
    back_ensemble = ensemble_scores(algorithm_results, 'back_scores', weights)

    return {
        'optimal_weights': weights,
        'front_ensemble': front_ensemble,
        'back_ensemble': back_ensemble,
        'total_algorithms': len(algorithm_results)
    }


def ensemble_scores(algorithm_results, score_type, weights):
    """集成多个算法的评分"""
    ensemble_scores = {}

    # 初始化所有号码的评分
    numbers_range = range(1, 36) if score_type == 'front_scores' else range(1, 13)
    for num in numbers_range:
        ensemble_scores[num] = 0.0

    # 加权平均
    for algo_name, result in algorithm_results.items():
        weight = weights[algo_name]
        for score_item in result[score_type]:
            num = score_item['number']
            if num in ensemble_scores:
                ensemble_scores[num] += score_item['score'] * weight

    # 转换为列表格式
    result_list = [{'number': num, 'score': score} for num, score in ensemble_scores.items()]
    result_list.sort(key=lambda x: x['score'], reverse=True)

    return result_list


def display_ensemble_results(ensemble_result):
    """显示集成结果"""
    print("\n🎯 集成优化预测结果:")

    print("前区集成预测 (前10个):")
    for item in ensemble_result['front_ensemble'][:10]:
        print(f"  号码 {item['number']:2d}: {item['score']:.4f}")

    print("后区集成预测 (前5个):")
    for item in ensemble_result['back_ensemble'][:5]:
        print(f"  号码 {item['number']:2d}: {item['score']:.4f}")

    print("\n算法权重分配:")
    for algo, weight in ensemble_result['optimal_weights'].items():
        print(f"  {algo}: {weight:.3f}")


if __name__ == "__main__":
    test_dynamic_ensemble_optimizer()