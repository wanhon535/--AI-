# G:\wanhong\cp\--AI-/\src\engine\recommendation_engine.py
# (请用此代码完全替换旧文件 - V4.0 协同工作流版)

from typing import List, Dict, Any
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory

# 导入我们全新的、负责融合的优化器
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer


class RecommendationEngine:
    """
    推荐引擎 V4.0 (协同工作流管理器)
    - 职责:
      1. 管理和运行所有基础的“评分器”算法。
      2. 收集所有评分器的确定性输出。
      3. 将结果交给一个指定的“融合器”算法进行智能融合。
      4. 返回最终的、信息量最大的融合报告。
    """

    def __init__(self, base_scorers: List[BaseAlgorithm], fusion_algorithm: DynamicEnsembleOptimizer):
        """
        初始化引擎。

        :param base_scorers: 一个包含所有基础评分器算法实例的列表。
        :param fusion_algorithm: 一个负责融合所有评分结果的算法实例 (我们的新版 DynamicEnsembleOptimizer)。
        """
        self._base_scorers = base_scorers
        self._fusion_algorithm = fusion_algorithm
        print("✅ Recommendation Engine V4.0 (Collaborative Workflow) initialized.")
        print(f"  - 基础评分器数量: {len(self._base_scorers)}")
        print(f"  - 指定融合算法: {self._fusion_algorithm.name} V{self._fusion_algorithm.version}")

    def generate_fused_recommendation(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """
        【核心方法】完整执行“并行计算 -> 智能融合”的工作流。

        :param history_data: 用于所有算法训练和预测的历史数据。
        :return: 来自融合算法的最终预测报告。
        """
        print("\n" + "=" * 50)
        print("🚀 [ENGINE] 开始执行协同推荐工作流...")
        print("=" * 50)

        # --- 1. 训练所有组件 (评分器 + 融合器) ---
        print("\n--- [PHASE 1] 训练所有算法组件 ---")
        for scorer in self._base_scorers:
            try:
                print(f"  - 正在训练评分器: {scorer.name}...")
                scorer.train(history_data)
            except Exception as e:
                print(f"  - ❌ 训练评分器 {scorer.name} 失败: {e}")

        try:
            print(f"  - 正在训练融合器: {self._fusion_algorithm.name}...")
            # 融合器的训练需要知道有哪些基础评分器，以便初始化权重
            self._fusion_algorithm.base_algorithms = self._base_scorers
            self._fusion_algorithm.train(history_data)
        except Exception as e:
            print(f"  - ❌ 训练融合器 {self._fusion_algorithm.name} 失败: {e}")

        # --- 2. 并行计算：收集所有基础评分器的预测结果 ---
        print("\n--- [PHASE 2] 收集所有基础评分器的预测 ---")
        individual_predictions: Dict[str, Any] = {}
        for scorer in self._base_scorers:
            try:
                print(f"  - 正在从 {scorer.name} 获取评分...")
                prediction = scorer.predict(history_data)
                if 'error' in prediction:
                    print(f"  - ⚠️ 评分器 {scorer.name} 返回错误: {prediction['error']}")
                else:
                    individual_predictions[scorer.name] = prediction
                    print(f"  - ✅ 已获取来自 {scorer.name} 的评分。")
            except Exception as e:
                print(f"  - ❌ 评分器 {scorer.name} 预测时发生严重错误: {e}")

        if not individual_predictions:
            print("  - ❌ 严重错误: 未能从任何基础评分器中收集到有效的预测结果。工作流终止。")
            return {"error": "未能收集到任何有效的评分器输出。"}

        # --- 3. 智能融合：将收集到的结果交给融合器处理 ---
        print("\n--- [PHASE 3] 执行智能融合 ---")
        print(f"  - 输入 {len(individual_predictions)} 份评分报告至 {self._fusion_algorithm.name}...")
        try:
            # 调用我们新版 optimizer 的 predict 方法，传入收集到的所有预测
            final_fused_report = self._fusion_algorithm.predict(individual_predictions)

            print(f"  - ✅ {self._fusion_algorithm.name} 已成功生成融合热力图。")
        except Exception as e:
            print(f"  - ❌ 融合算法 {self._fusion_algorithm.name} 执行时发生严重错误: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"融合算法执行失败: {e}"}

        print("\n" + "=" * 50)
        print("🏁 [ENGINE] 协同推荐工作流执行完毕。")
        print("=" * 50)

        # 返回最终的、包含“大师热力图”的报告
        return final_fused_report