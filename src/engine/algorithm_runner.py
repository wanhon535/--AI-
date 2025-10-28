# file: src/engine/algorithm_runner.py
# 算法运行器模块，负责加载和运行各种预测算法

from typing import Dict, Any, List
from src.model.lottery_models import LotteryHistory
from src.engine.recommendation_engine import RecommendationEngine

# 导入你的算法类
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.neural_lottery_predictor import NeuralLotteryPredictor
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer
from src.algorithms.advanced_algorithms.hit_rate_optimizer import HitRateOptimizer


def run_algorithm_layer(history_data: List[LotteryHistory]) -> Dict[str, Any]:
    """
    运行算法层（Bayesian / Markov / Neural / Graph / HitOptimizer 等）
    返回统一格式的 model_outputs 供 LLM 融合使用。
    
    参数:
        history_data (List[LotteryHistory]): 历史开奖数据列表
        
    返回:
        Dict[str, Any]: 包含各算法预测结果的字典，键为算法名称，值为预测结果
    """
    # 初始化推荐引擎
    engine = RecommendationEngine()

    # 注册算法并分配权重
    # 贝叶斯预测器：基于历史频率和贝叶斯更新的概率预测模型
    engine.add_algorithm(BayesianNumberPredictor(), weight=0.25)
    # 马尔可夫转移模型：基于号码间转移概率的预测模型
    engine.add_algorithm(MarkovTransitionModel(), weight=0.2)
    # 神经网络预测器：使用LSTM神经网络进行预测
    engine.add_algorithm(NeuralLotteryPredictor(), weight=0.25)
    # 号码图分析器：基于共现图和PageRank算法分析号码关系
    engine.add_algorithm(NumberGraphAnalyzer(), weight=0.15)
    # 命中率优化器：通过遗传算法优化号码组合的命中率
    engine.add_algorithm(HitRateOptimizer(), weight=0.15)

    # 训练所有注册的算法
    engine.train_all_algorithms(history_data)

    # 生成推荐结果（单独保存算法预测的原始数据）
    model_outputs = {}

    # 遍历所有已训练的算法，获取它们的预测结果
    for algo in engine.algorithms:
        if algo.is_trained:
            prediction = algo.predict(history_data)
            model_outputs[algo.name] = prediction

    return model_outputs