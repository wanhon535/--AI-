import numpy as np
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any
import logging


class DynamicEnsembleOptimizer(BaseAlgorithm):
    """动态集成优化器 - 智能整合多个算法的结果"""
    name = "DynamicEnsembleOptimizer"
    version = "1.0"

    def __init__(self):
        super().__init__()
        self.algorithms = {}
        self.algorithm_weights = {}
        self.performance_history = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练集成优化器"""
        if not history_data or len(history_data) < 30:
            logging.error("数据量不足，无法进行集成优化")
            return False

        try:
            # 初始化算法实例
            self._initialize_algorithms()

            # 训练所有子算法
            self._train_all_algorithms(history_data)

            # 计算最优权重
            self._calculate_optimal_weights(history_data)

            self.is_trained = True
            logging.info("动态集成优化器训练完成")
            return True

        except Exception as e:
            logging.error(f"集成优化器训练失败: {e}")
            return False

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于集成优化进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        try:
            # 获取所有算法的预测结果
            all_predictions = self._collect_all_predictions(history_data)

            # 动态集成优化
            ensemble_result = self._dynamic_ensemble(all_predictions)

            # 计算集成置信度
            confidence = self._calculate_ensemble_confidence(all_predictions)

            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{
                    'front_number_scores': ensemble_result['front'],
                    'back_number_scores': ensemble_result['back'],
                    'confidence': confidence,
                    'ensemble_method': 'dynamic_weighted_average'
                }],
                'analysis': {
                    'ensemble_info': self._get_ensemble_info(all_predictions),
                    'algorithm_performance': self.performance_history,
                    'weight_distribution': self.algorithm_weights
                }
            }

        except Exception as e:
            logging.error(f"集成优化预测失败: {e}")
            return {'error': str(e)}

    def _initialize_algorithms(self):
        """初始化所有子算法"""
        try:
            from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
            from src.algorithms.advanced_algorithms.time_series_analyzer import TimeSeriesAnalyzer
            from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
            from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer
            from src.algorithms.intelligent_pattern_recognizer import IntelligentPatternRecognizer

            self.algorithms = {
                'bayesian': BayesianNumberPredictor(),
                'time_series': TimeSeriesAnalyzer(),
                'markov': MarkovTransitionModel(),
                'graph_analysis': NumberGraphAnalyzer(),
                'pattern_recognition': IntelligentPatternRecognizer()
            }

            logging.info(f"初始化了 {len(self.algorithms)} 个子算法")

        except ImportError as e:
            logging.warning(f"某些算法无法导入: {e}")
            # 如果某些算法不可用，继续使用可用的算法

    def _train_all_algorithms(self, history_data: List[LotteryHistory]):
        """训练所有子算法"""
        trained_count = 0
        for algo_name, algorithm in self.algorithms.items():
            try:
                if algorithm.train(history_data):
                    trained_count += 1
                    logging.info(f"算法 {algo_name} 训练成功")
                else:
                    logging.warning(f"算法 {algo_name} 训练失败")
                    # 移除训练失败的算法
                    del self.algorithms[algo_name]
            except Exception as e:
                logging.error(f"算法 {algo_name} 训练异常: {e}")
                del self.algorithms[algo_name]

        logging.info(f"成功训练了 {trained_count} 个算法")

    def _calculate_optimal_weights(self, history_data: List[LotteryHistory]):
        """计算最优权重分配"""
        if not self.algorithms:
            logging.error("没有可用的算法进行权重计算")
            return

        # 模拟历史性能评估（实际应用中应该基于真实的历史预测性能）
        base_weights = {
            'bayesian': 0.25,
            'time_series': 0.20,
            'markov': 0.15,
            'graph_analysis': 0.20,
            'pattern_recognition': 0.20
        }

        # 根据算法可用性调整权重
        total_weight = 0
        for algo_name in self.algorithms.keys():
            if algo_name in base_weights:
                self.algorithm_weights[algo_name] = base_weights[algo_name]
                total_weight += base_weights[algo_name]

        # 归一化权重
        if total_weight > 0:
            for algo_name in self.algorithm_weights:
                self.algorithm_weights[algo_name] /= total_weight

        logging.info(f"权重分配: {self.algorithm_weights}")

    def _collect_all_predictions(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """收集所有算法的预测结果"""
        predictions = {}

        for algo_name, algorithm in self.algorithms.items():
            try:
                result = algorithm.predict(history_data)
                if 'error' not in result:
                    predictions[algo_name] = result
                    # 记录算法置信度
                    algo_confidence = result.get('recommendations', [{}])[0].get('confidence', 0.5)
                    self.performance_history[algo_name] = {
                        'latest_confidence': algo_confidence,
                        'prediction_time': 'current'
                    }
            except Exception as e:
                logging.error(f"算法 {algo_name} 预测失败: {e}")

        return predictions

    def _dynamic_ensemble(self, all_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """动态集成所有算法的预测结果"""
        front_ensemble = self._ensemble_scores(all_predictions, 'front')
        back_ensemble = self._ensemble_scores(all_predictions, 'back')

        return {
            'front': front_ensemble,
            'back': back_ensemble
        }

    def _ensemble_scores(self, all_predictions: Dict[str, Any], area_type: str) -> List[Dict[str, Any]]:
        """集成指定区域的评分"""
        numbers_range = range(1, 36) if area_type == 'front' else range(1, 13)
        ensemble_scores = {num: 0.0 for num in numbers_range}

        for algo_name, prediction in all_predictions.items():
            weight = self.algorithm_weights.get(algo_name, 0)

            # 获取该算法的评分
            algo_scores = prediction.get('recommendations', [{}])[0].get(f'{area_type}_number_scores', [])

            # 转换为字典格式便于查找
            score_dict = {item['number']: item['score'] for item in algo_scores}

            # 加权集成
            for num in numbers_range:
                if num in score_dict:
                    ensemble_scores[num] += score_dict[num] * weight

        # 转换为列表格式并排序
        result = [{'number': num, 'score': score} for num, score in ensemble_scores.items()]
        result.sort(key=lambda x: x['score'], reverse=True)

        return result

    def _calculate_ensemble_confidence(self, all_predictions: Dict[str, Any]) -> float:
        """计算集成置信度"""
        if not all_predictions:
            return 0.5

        # 基于算法数量和一致性计算置信度
        algo_count = len(all_predictions)

        # 计算算法间的一致性
        consistency = self._calculate_consistency(all_predictions)

        # 基础置信度
        base_confidence = 0.6

        # 算法数量加成
        count_bonus = min(0.2, (algo_count - 1) * 0.05)

        # 一致性加成
        consistency_bonus = consistency * 0.2

        confidence = base_confidence + count_bonus + consistency_bonus

        return min(confidence, 0.95)

    def _calculate_consistency(self, all_predictions: Dict[str, Any]) -> float:
        """计算算法间的一致性"""
        if len(all_predictions) < 2:
            return 0.0

        # 比较前区top5的重叠度
        front_top5_sets = []
        for prediction in all_predictions.values():
            front_scores = prediction.get('recommendations', [{}])[0].get('front_number_scores', [])
            top5 = {item['number'] for item in front_scores[:5]}
            front_top5_sets.append(top5)

        # 计算平均重叠度
        total_overlap = 0
        pair_count = 0

        for i in range(len(front_top5_sets)):
            for j in range(i + 1, len(front_top5_sets)):
                overlap = len(front_top5_sets[i] & front_top5_sets[j]) / 5
                total_overlap += overlap
                pair_count += 1

        if pair_count > 0:
            return total_overlap / pair_count
        else:
            return 0.0

    def _get_ensemble_info(self, all_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """获取集成信息"""
        return {
            'algorithm_count': len(all_predictions),
            'algorithms_used': list(all_predictions.keys()),
            'optimal_weights': self.algorithm_weights,
            'ensemble_confidence_factors': {
                'algorithm_count': len(all_predictions),
                'consistency': self._calculate_consistency(all_predictions)
            }
        }