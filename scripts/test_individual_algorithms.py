# 算法出现问题测试点：

import os
import importlib
import inspect
import traceback
import random
import json
from datetime import datetime, timedelta
from typing import List, Type

# --- 关键：确保脚本能找到 src 目录 ---
# 通过以模块方式运行 `python -m scripts.test...`，Python 会自动将根目录加入 sys.path
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory


# --- 模拟数据生成模块 ---
def generate_mock_history(records: int = 150) -> List[LotteryHistory]:
    """生成符合您项目模型的、用于测试的模拟彩票历史数据"""
    history = []
    # 从一个固定的种子开始，确保每次测试的数据都一样，便于复现问题
    random.seed(42)
    start_date = datetime.now() - timedelta(days=records * 2)
    for i in range(records):
        history.append(
            LotteryHistory(
                issue=f"2025{str(i + 1).zfill(3)}",
                date=start_date + timedelta(days=i * 2),
                front_area=sorted(random.sample(range(1, 36), 5)),
                back_area=sorted(random.sample(range(1, 13), 2)),
            )
        )
    return history


def pretty_print_dict(data: dict):
    """美化JSON输出，便于阅读"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


# --- 动态算法发现模块 ---
def discover_algorithms() -> List[Type[BaseAlgorithm]]:
    """动态扫描 src/algorithms 目录并返回所有 BaseAlgorithm 的子类"""
    algorithms_found = []
    base_dir = os.path.join('src', 'algorithms')

    print(f"[*] 正在从 '{base_dir}' 目录中扫描算法...")

    for root, _, files in os.walk(base_dir):
        for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
                # 构建模块导入路径，例如: src.algorithms.advanced_algorithms.bayesian_number_predictor
                module_path = os.path.join(root, filename[:-3]).replace(os.path.sep, '.')

                try:
                    module = importlib.import_module(module_path)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # 检查是否是 BaseAlgorithm 的子类，并且不是 BaseAlgorithm 本身
                        if issubclass(obj, BaseAlgorithm) and obj is not BaseAlgorithm:
                            # 避免重复添加
                            if obj not in algorithms_found:
                                algorithms_found.append(obj)
                                print(f"  [发现] -> {obj.name} (来自: {filename})")

                except (ImportError, RuntimeError, NameError, AttributeError) as e:
                    print(f"  [警告] 无法从 '{filename}' 加载算法。")
                    print(f"         错误: {e}")
                    print(f"         请检查该文件是否缺少依赖 (如: torch, networkx) 或存在语法错误。")

    return algorithms_found


# --- 测试主函数 ---
def main():
    """主执行函数"""
    print("=" * 70)
    print("           启动独立算法健康诊断程序")
    print("=" * 70)

    # 1. 发现所有可用的算法
    algorithms_to_test = discover_algorithms()
    if not algorithms_to_test:
        print("\n[错误] 未发现任何算法。请检查 /src/algorithms 目录结构。")
        return

    # 2. 生成一份通用的模拟数据
    print("\n[*] 正在生成 150 条高质量模拟历史数据用于测试...")
    mock_data = generate_mock_history()
    print(
        f"    -> 数据生成完毕。最新一期: {mock_data[-1].issue}, 号码: {mock_data[-1].front_area} + {mock_data[-1].back_area}")

    # 3. 逐个对发现的算法进行诊断
    print("\n[*] 开始对每个算法进行健康检查...")
    total_algorithms = len(algorithms_to_test)
    success_count = 0

    for i, AlgoClass in enumerate(algorithms_to_test):
        algo_name = AlgoClass.name if hasattr(AlgoClass, 'name') else AlgoClass.__name__
        print("\n" + "-" * 60)
        print(f"  [诊断中 {i + 1}/{total_algorithms}] -> {algo_name}")
        print("-" * 60)

        # 特殊情况处理：跳过需要其他模型作为输入的算法
        init_params = inspect.signature(AlgoClass.__init__).parameters
        if len(init_params) > 1:  # >1 表示除了 self 之外还需要其他参数
            print("  [跳过] -> 此算法的构造函数需要额外参数，不适用于本独立测试脚本。请为其编写专门的测试。")
            continue

        try:
            # 3.1 实例化
            instance = AlgoClass()
            print("  [1/3] 实例化: [成功]")

            # 3.2 训练
            is_trained = instance.train(mock_data)
            if not isinstance(is_trained, bool):
                print(f"  [2/3] 训练 (train): [注意] -> 'train' 方法应返回布尔值，但返回了 {type(is_trained)} 类型。")
            else:
                print(f"  [2/3] 训练 (train): [成功] -> 返回值: {is_trained}")

            # 3.3 预测
            # 对于需要特殊输入的 predict 方法，这里仅使用通用历史数据
            prediction_result = instance.predict(mock_data)
            print("  [3/3] 预测 (predict): [成功] -> 完整输出如下:")
            pretty_print_dict(prediction_result)

            print(f"\n  [诊断结果] -> {algo_name}: [健康]")
            success_count += 1

        except Exception as e:
            print(f"\n  !!!!!! [诊断结果] -> {algo_name}: [故障] !!!!!!")
            print(f"  在测试过程中发生严重错误: {e}")
            print("\n" + "=" * 15 + " 错误追溯 " + "=" * 15)
            traceback.print_exc()
            print("=" * 42)

    # 4. 输出最终总结报告
    print("\n" + "=" * 70)
    print("           所有算法健康诊断已完成！")
    print("\n[最终报告]")
    print(f"  - 总共诊断算法数: {total_algorithms}")
    print(f"  - 健康 (通过测试): {success_count}")
    print(f"  - 故障 (需要修复): {total_algorithms - success_count}")
    print("=" * 70)
    print("请检查上面标记为 [故障] 的算法，并根据错误追溯信息进行修复。")


if __name__ == "__main__":
    main()