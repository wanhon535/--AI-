# test_number_graph_analyzer.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 号码图分析器测试脚本
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG

# 尝试导入号码图分析器
try:
    from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer

    GRAPH_AVAILABLE = True
except ImportError as e:
    print(f"❌ 无法导入号码图分析器: {e}")
    GRAPH_AVAILABLE = False


def test_number_graph_analyzer():
    """测试号码图分析器"""
    print("=== 测试号码图分析器 ===")

    if not GRAPH_AVAILABLE:
        print("❌ 号码图分析器不可用，请先实现该算法")
        create_graph_analysis_demo()
        return

    # 创建预测器实例
    predictor = NumberGraphAnalyzer()
    print(f"算法名称: {predictor.name}")
    print(f"版本: {predictor.version}")

    try:
        # 从数据库获取真实历史数据
        print("\n1. 连接数据库并获取历史数据...")
        db_manager = DatabaseManager(**DB_CONFIG)

        # 获取历史数据 - 图分析需要足够的数据来建立关系
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
        print("\n2. 构建号码关系图...")
        train_success = predictor.train(history_data)
        print(f"训练状态: {'✅ 成功' if train_success else '❌ 失败'}")
        print(f"模型已训练: {predictor.is_trained}")

        if not train_success:
            print("❌ 训练失败，退出测试")
            return

        # 测试预测
        print("\n3. 进行图分析预测...")
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

        print(f"\n5. 前区号码图分析评分 (前15个):")
        for i, score_item in enumerate(front_scores[:15]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        print(f"\n6. 后区号码图分析评分 (前8个):")
        for i, score_item in enumerate(back_scores[:8]):
            print(f"  号码 {score_item['number']:2d}: 评分 {score_item['score']:.4f}")

        # 基本验证
        print(f"\n7. 基本验证:")
        print(f"前区号码数量: {len(front_scores)} (应为35)")
        print(f"后区号码数量: {len(back_scores)} (应为12)")
        print(f"评分范围正常: {all(0 <= item['score'] <= 1 for item in front_scores + back_scores)}")

        # 分析图关系特征
        print(f"\n8. 图关系特征分析:")
        front_top5 = front_scores[:5]
        back_top3 = back_scores[:3]

        print("   前区中心性最高号码:")
        for item in front_top5:
            print(f"     号码 {item['number']}: 图中心性评分 {item['score']:.4f}")

        print("   后区中心性最高号码:")
        for item in back_top3:
            print(f"     号码 {item['number']}: 图中心性评分 {item['score']:.4f}")

        # 如果有图分析相关信息，显示出来
        analysis = result.get('analysis', {})
        if 'graph_analysis' in analysis:
            graph_info = analysis['graph_analysis']
            print(f"\n9. 号码图分析信息:")
            print(f"   图节点数: {graph_info.get('node_count', 'N/A')}")
            print(f"   图边数: {graph_info.get('edge_count', 'N/A')}")
            print(f"   图密度: {graph_info.get('graph_density', 'N/A')}")

            # 显示强关联号码对
            if 'strong_connections' in graph_info:
                print(f"   最强关联号码对:")
                connections = graph_info['strong_connections'][:5]  # 显示前5个
                for conn in connections:
                    print(f"     {conn[0]} ↔ {conn[1]}: {conn[2]:.4f}")

        print("\n=== 号码图分析器测试完成 ===")

        return result

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


def create_graph_analysis_demo():
    """创建号码图分析演示"""
    print("\n🕸️ 创建号码图分析演示...")

    try:
        from src.database.database_manager import DatabaseManager
        import numpy as np
        from collections import defaultdict

        db_manager = DatabaseManager(**DB_CONFIG)
        history_data = db_manager.get_all_lottery_history(limit=100)

        if len(history_data) < 20:
            print("❌ 数据量不足，无法进行图分析")
            return

        print(f"使用 {len(history_data)} 条记录进行号码关系图分析")

        # 构建共现矩阵
        front_cooccurrence = build_cooccurrence_matrix(history_data, 'front')
        back_cooccurrence = build_cooccurrence_matrix(history_data, 'back')

        # 分析强关联
        front_strong_pairs = find_strong_connections(front_cooccurrence, 'front')
        back_strong_pairs = find_strong_connections(back_cooccurrence, 'back')

        print("✅ 号码关系图分析完成")
        print(f"   前区关系对: {len(front_strong_pairs)} 个强关联")
        print(f"   后区关系对: {len(back_strong_pairs)} 个强关联")

        # 显示结果
        print("\n🔗 前区最强关联号码对:")
        for pair in front_strong_pairs[:10]:
            print(f"   {pair[0]} ↔ {pair[1]}: 共现{pair[2]}次")

        print("\n🔗 后区最强关联号码对:")
        for pair in back_strong_pairs[:5]:
            print(f"   {pair[0]} ↔ {pair[1]}: 共现{pair[2]}次")

        # 生成基于图中心性的预测
        simulate_graph_prediction(history_data, front_cooccurrence, back_cooccurrence)

    except Exception as e:
        print(f"❌ 号码图分析演示失败: {e}")


def build_cooccurrence_matrix(history_data, area_type):
    """构建号码共现矩阵"""
    size = 35 if area_type == 'front' else 12
    cooccurrence = np.zeros((size, size))

    for record in history_data:
        numbers = record.front_area if area_type == 'front' else record.back_area

        # 更新共现计数
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                num1 = numbers[i] - 1
                num2 = numbers[j] - 1
                if 0 <= num1 < size and 0 <= num2 < size:
                    cooccurrence[num1][num2] += 1
                    cooccurrence[num2][num1] += 1

    return cooccurrence


def find_strong_connections(cooccurrence_matrix, area_type):
    """找出强关联号码对"""
    size = cooccurrence_matrix.shape[0]
    connections = []

    # 计算平均共现次数
    avg_cooccurrence = np.mean(cooccurrence_matrix)

    for i in range(size):
        for j in range(i + 1, size):
            if cooccurrence_matrix[i][j] > avg_cooccurrence * 1.5:
                connections.append((i + 1, j + 1, cooccurrence_matrix[i][j]))

    # 按共现次数排序
    connections.sort(key=lambda x: x[2], reverse=True)
    return connections


def simulate_graph_prediction(history_data, front_cooccurrence, back_cooccurrence):
    """模拟基于图分析的预测"""
    print("\n🎯 模拟图分析预测结果:")

    # 计算度数中心性
    front_degree_centrality = calculate_degree_centrality(front_cooccurrence)
    back_degree_centrality = calculate_degree_centrality(back_cooccurrence)

    # 归一化
    front_max = max(front_degree_centrality.values()) if front_degree_centrality else 1
    back_max = max(back_degree_centrality.values()) if back_degree_centrality else 1

    front_scores = [{'number': num, 'score': score / front_max}
                    for num, score in front_degree_centrality.items()]
    back_scores = [{'number': num, 'score': score / back_max}
                   for num, score in back_degree_centrality.items()]

    front_scores.sort(key=lambda x: x['score'], reverse=True)
    back_scores.sort(key=lambda x: x['score'], reverse=True)

    print("前区图中心性预测 (前10个):")
    for item in front_scores[:10]:
        print(f"  号码 {item['number']:2d}: 中心性 {item['score']:.4f}")

    print("后区图中心性预测 (前5个):")
    for item in back_scores[:5]:
        print(f"  号码 {item['number']:2d}: 中心性 {item['score']:.4f}")


def calculate_degree_centrality(cooccurrence_matrix):
    """计算度数中心性"""
    centrality = {}
    size = cooccurrence_matrix.shape[0]

    for i in range(size):
        # 度数中心性 = 与该节点相连的边的权重和
        centrality[i + 1] = np.sum(cooccurrence_matrix[i])

    return centrality


if __name__ == "__main__":
    test_number_graph_analyzer()