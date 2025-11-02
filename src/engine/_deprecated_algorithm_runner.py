# file: src/engine/_deprecated_algorithm_runner.py (Upgraded to accept weights)
from typing import Dict, Any, List, Optional
from src.model.lottery_models import LotteryHistory

# 导入所有算法
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.algorithms.statistical_algorithms import *
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer


def run_algorithm_layer(
        history_data: List[LotteryHistory],
        weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    运行算法层，并使用一个元算法 (DynamicEnsembleOptimizer) 来整合结果。

    :param history_data: 历史开奖数据列表
    :param weights: 从数据库学习到的动态权重
    :return: 一个包含单一键 (优化器名称) 和其综合预测结果的字典
    """
    print("  - [Algorithm Runner] 正在组建基础算法团队...")
    base_algorithms = [
        FrequencyAnalysisAlgorithm(), HotColdNumberAlgorithm(), OmissionValueAlgorithm(),
        BayesianNumberPredictor(), MarkovTransitionModel(), NumberGraphAnalyzer(),
    ]

    print("  - [Algorithm Runner] 正在初始化动态集成优化器...")
    optimizer = DynamicEnsembleOptimizer(base_algorithms)

    # 关键一步：注入从 main.py 传递过来的、学习到的权重
    if weights:
        optimizer.current_weights = weights
        print(f"  - [Algorithm Runner] ✅ 已成功注入学习到的权重。")
    else:
        print(f"  - [Algorithm Runner] ⚠️ 未提供权重，优化器将使用默认权重。")

    print("  - [Algorithm Runner] 优化器开始训练和预测...")
    optimizer.train(history_data)
    final_report = optimizer.predict(history_data)

    # 返回以优化器名为键的单一报告，这正是LLM需要的
    return {optimizer.name: final_report}