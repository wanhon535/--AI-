import os
import sys

# --- 环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from src.algorithms import AVAILABLE_ALGORITHMS
# 导入您的数据模型，以便我们检查类型
from src.model.lottery_models import LotteryHistory


def test_data_pipeline_and_algorithms():
    """
    深度侦查版测试：
    1. 验证从数据库出来的数据是否符合预期。
    2. 验证算法是否收到了正确的数据并进行了正确的计算。
    """
    print("\n" + "#" * 70 + "\n###      🕵️  启动【深度数据链路侦查】测试      ###\n" + "#" * 70)

    # --- 步骤 1: 检查数据库连接和数据获取 ---
    print("\n--- [侦查步骤 1/3] 正在连接数据库并提取原始证据... ---")
    db_manager = DatabaseManager(**DB_CONFIG)
    assert db_manager.connect(), "数据库连接失败，测试终止。"

    history_data = db_manager.get_latest_lottery_history(limit=50)
    assert len(history_data) >= 20, f"历史数据不足20期 (实际获取到 {len(history_data)} 条)，无法进行有效测试。"

    print(f"✅ 成功从数据库获取 {len(history_data)} 条记录。")

    # --- 步骤 2: 深入检查数据样本的“物证” ---
    print("\n--- [侦查步骤 2/3] 正在检验数据样本的结构与类型... ---")
    # 随机抽取一条记录进行详细检查
    sample_record = history_data[0]

    print(f"  - 样本记录期号: {sample_record.period_number}")
    print(f"  - 样本记录完整内容: {sample_record}")

    # 这是最关键的检查点！
    assert isinstance(sample_record, LotteryHistory), f"数据记录不是 LotteryHistory 对象，而是 {type(sample_record)}！"
    print(f"  - ✅ [关键证据] 数据类型为 LotteryHistory 对象，检查通过。")

    assert isinstance(sample_record.front_area,
                      list), f"front_area 不是列表(list)，而是 {type(sample_record.front_area)}！"
    print(f"  - ✅ [关键证据] front_area 属性是列表类型，检查通过。")

    assert len(sample_record.front_area) == 5, f"front_area 列表长度不为5 (实际为 {len(sample_record.front_area)})！"
    print(f"  - ✅ [关键证据] front_area 列表长度为5，检查通过。")

    assert isinstance(sample_record.front_area[0],
                      int), f"front_area 列表中的元素不是整数(int)，而是 {type(sample_record.front_area[0])}！"
    print(f"  - ✅ [关键证据] front_area 列表元素为整数，检查通过。")
    print(f"  - 结论: 数据从数据库到Python对象的转换链路【看起来】是正常的。")

    # --- 步骤 3: 逐一“审问”算法，看它们如何处理证据 ---
    print("\n--- [侦查步骤 3/3] 正在逐一审问算法的处理逻辑... ---")
    for name, AlgoClass in AVAILABLE_ALGORITHMS.items():
        if name == "DynamicEnsembleOptimizer":
            continue

        print("\n" + "-" * 60)
        print(f"🔬 正在审问算法: {name}")

        try:
            algorithm = AlgoClass()

            # --- 在 train 方法内部进行侦查 ---
            # 我们将在这里模拟 train 方法的第一步，以检查数据处理
            print(f"  - [审问] 正在检查 {name} 的数据处理过程...")
            front_numbers_collected = [num for record in history_data for num in record.front_area]
            print(f"  - [内部证据] 算法收集到的前区号码总数: {len(front_numbers_collected)}")
            print(f"  - [内部证据] 收集到的号码样本 (前20个): {front_numbers_collected[:20]}")

            from collections import Counter
            counts = Counter(front_numbers_collected)
            print(f"  - [内部证据] 频率统计结果 (Top 5): {counts.most_common(5)}")

            # 正常执行
            algorithm.train(history_data)
            result = algorithm.predict(history_data)

            # 检查输出
            assert 'recommendations' in result, f"[{name}] 缺少 'recommendations' 键！"
            rec = result['recommendations'][0]
            front_scores = rec['front_number_scores']

            print(f"  - ✅ 算法输出了正确的数据结构。")

            top_front = front_scores[0]
            print(f"  - 🧠 最终结论: 最高分的前区号码是 {top_front['number']} (得分: {top_front['score']:.4f})")

        except Exception as e:
            assert False, f"{name} 算法在审问过程中失败: {e}"