# debug_markov_model.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
import numpy as np


def debug_markov_model():
    """调试马尔可夫模型"""
    print("=== 调试马尔可夫转移模型 ===")

    # 创建预测器实例
    predictor = MarkovTransitionModel()

    # 获取历史数据
    db_manager = DatabaseManager(**DB_CONFIG)
    history_data = db_manager.get_all_lottery_history(limit=200)
    print(f"使用 {len(history_data)} 条历史记录")

    # 训练模型
    predictor.train(history_data)

    # 检查转移矩阵
    print("\n🔍 转移矩阵诊断:")

    if predictor.front_transition_matrix is not None:
        print("\n前区转移矩阵统计:")
        print(f"形状: {predictor.front_transition_matrix.shape}")
        print(f"最小值: {np.min(predictor.front_transition_matrix):.6f}")
        print(f"最大值: {np.max(predictor.front_transition_matrix):.6f}")
        print(f"平均值: {np.mean(predictor.front_transition_matrix):.6f}")
        print(f"标准差: {np.std(predictor.front_transition_matrix):.6f}")

        # 检查每行的和（应该为1）
        row_sums = np.sum(predictor.front_transition_matrix, axis=1)
        print(f"行和检查 - 最小值: {np.min(row_sums):.6f}, 最大值: {np.max(row_sums):.6f}")

        # 显示一些示例转移概率
        print("\n前区转移概率示例:")
        for i in range(5):
            row = predictor.front_transition_matrix[i]
            top_3_indices = np.argsort(row)[-3:][::-1]
            print(f"从号码{i + 1} -> 最可能转移到: ", end="")
            for idx in top_3_indices:
                print(f"{idx + 1}({row[idx]:.4f}) ", end="")
            print()

    if predictor.back_transition_matrix is not None:
        print("\n后区转移矩阵统计:")
        print(f"形状: {predictor.back_transition_matrix.shape}")
        print(f"最小值: {np.min(predictor.back_transition_matrix):.6f}")
        print(f"最大值: {np.max(predictor.back_transition_matrix):.6f}")
        print(f"平均值: {np.mean(predictor.back_transition_matrix):.6f}")
        print(f"标准差: {np.std(predictor.back_transition_matrix):.6f}")

        # 检查每行的和
        row_sums = np.sum(predictor.back_transition_matrix, axis=1)
        print(f"行和检查 - 最小值: {np.min(row_sums):.6f}, 最大值: {np.max(row_sums):.6f}")

        print("\n后区转移概率示例:")
        for i in range(3):
            row = predictor.back_transition_matrix[i]
            top_3_indices = np.argsort(row)[-3:][::-1]
            print(f"从号码{i + 1} -> 最可能转移到: ", end="")
            for idx in top_3_indices:
                print(f"{idx + 1}({row[idx]:.4f}) ", end="")
            print()

    # 检查平稳分布
    if predictor.stationary_distribution:
        print("\n📊 平稳分布分析:")
        front_stationary = predictor.stationary_distribution['front']
        back_stationary = predictor.stationary_distribution['back']

        print(f"前区平稳分布 - 最小值: {min(front_stationary):.6f}, 最大值: {max(front_stationary):.6f}")
        print(f"后区平稳分布 - 最小值: {min(back_stationary):.6f}, 最大值: {max(back_stationary):.6f}")

        # 显示平稳分布中最可能的号码
        front_top5 = sorted(range(len(front_stationary)), key=lambda i: front_stationary[i], reverse=True)[:5]
        back_top3 = sorted(range(len(back_stationary)), key=lambda i: back_stationary[i], reverse=True)[:3]

        print("前区平稳分布最可能号码:")
        for idx in front_top5:
            print(f"  号码{idx + 1}: {front_stationary[idx]:.4f}")

        print("后区平稳分布最可能号码:")
        for idx in back_top3:
            print(f"  号码{idx + 1}: {back_stationary[idx]:.4f}")


def check_data_quality():
    """检查数据质量"""
    print("\n=== 数据质量检查 ===")

    db_manager = DatabaseManager(**DB_CONFIG)
    history_data = db_manager.get_all_lottery_history(limit=200)

    print(f"总记录数: {len(history_data)}")

    if not history_data:
        return

    # 检查号码分布
    front_counts = {i: 0 for i in range(1, 36)}
    back_counts = {i: 0 for i in range(1, 13)}

    for record in history_data:
        for num in record.front_area:
            if 1 <= num <= 35:
                front_counts[num] += 1
        for num in record.back_area:
            if 1 <= num <= 12:
                back_counts[num] += 1

    print("\n前区号码出现次数统计:")
    front_sorted = sorted(front_counts.items(), key=lambda x: x[1], reverse=True)
    for num, count in front_sorted[:10]:
        print(f"  号码{num}: 出现{count}次 ({count / len(history_data) * 100:.1f}%)")

    print("\n后区号码出现次数统计:")
    back_sorted = sorted(back_counts.items(), key=lambda x: x[1], reverse=True)
    for num, count in back_sorted[:5]:
        print(f"  号码{num}: 出现{count}次 ({count / len(history_data) * 100:.1f}%)")


if __name__ == "__main__":
    debug_markov_model()
    check_data_quality()