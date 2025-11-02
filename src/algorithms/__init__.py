# ======================================================================
# --- FILE: src/algorithms/__init__.py (COMPLETE REPLACEMENT - CLEANED) ---
# ======================================================================

# --- 核心思想 ---
# 只注册那些 (1) 已完全实现 和 (2) 遵循“评分器”模式的算法。
# “评分器”模式：predict方法返回包含 'front_number_scores' 和 'back_number_scores' 的字典。
# 这样，它们才能被 DynamicEnsembleOptimizer 正确地融合。

# 1. 导入所有稳定且兼容的算法“类”
from .statistical_algorithms import FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, OmissionValueAlgorithm
from .advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from .advanced_algorithms.markov_transition_model import MarkovTransitionModel
from .advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer
# 导入融合器本身
from .dynamic_ensemble_optimizer import DynamicEnsembleOptimizer

# 2. 创建一个干净、可运行的“算法注册表”
AVAILABLE_ALGORITHMS = {
    # --- 基础统计评分器 (已验证) ---
    "FrequencyAnalysisScorer": FrequencyAnalysisAlgorithm,
    "HotColdScorer": HotColdNumberAlgorithm,
    "OmissionValueScorer": OmissionValueAlgorithm,

    # --- 高级评分器 (已升级改造) ---
    "BayesianNumberPredictor": BayesianNumberPredictor,
    "MarkovTransitionModel": MarkovTransitionModel,
    "NumberGraphAnalyzer": NumberGraphAnalyzer,

    # --- 融合器 (系统核心) ---
    "DynamicEnsembleOptimizer": DynamicEnsembleOptimizer,

    # --- 已被暂时移除的算法 (原因：未实现、不兼容或需要重构) ---
    # "NumberFrequencyAnalyzer": (未实现)
    # "TimeSeriesPredictor": (未实现)
    # "LotteryRLAgent": (不兼容评分模式)
    # "NeuralLotteryPredictor": (依赖PyTorch，且模式不兼容)
    # "IntelligentPatternRecognizer": (模式不兼容)
    # "GeneticOptimizer": (未实现)
    # "EnsembleLearner": (未实现)
    # "RiskAssessmentAlgorithm": (非号码预测类算法)
    # "PortfolioOptimizationAlgorithm": (非号码预测类算法)
    # "StopLossAlgorithm": (非号码预测类算法)
    # "RealTimeFeedbackLearner": (元学习器，需在更高层面集成)
}