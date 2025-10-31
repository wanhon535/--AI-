# algorithms/dynamic_ensemble_optimizer.py
from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
import numpy as np
from collections import defaultdict

from src.model.lottery_models import LotteryHistory


class DynamicEnsembleOptimizer(BaseAlgorithm):
    """动态权重集成优化器 - 实时调整算法权重"""

    def __init__(self, base_algorithms: List[BaseAlgorithm]):
        super().__init__("dynamic_ensemble_optimizer", "2.0")
        self.base_algorithms = base_algorithms
        self.performance_history = defaultdict(list)
        self.current_weights = {}
        self.parameters = {
            'evaluation_window': 20,
            'min_performance_threshold': 0.1,
            'weight_decay_factor': 0.95
        }

    def predict_with_individuals(self, history_data: List[LotteryHistory],
                                 individual_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用已经计算好的基础算法预测结果，进行动态集成。
        这是为了优化性能，避免在 RecommendationEngine 中重复计算。
        """
        if not self.is_trained:
            # 即使没有被显式训练，也尝试用默认权重进行预测
            print("  - [Optimizer] 警告: 模型未标记为已训练，但仍尝试使用当前权重进行预测。")

        # 准备用于投票的数据结构
        all_predictions_for_voting = {}

        # 遍历传入的、已计算好的预测结果
        for algo_name, prediction in individual_predictions.items():
            # 确保这个算法是我们的基础算法之一
            if algo_name in [a.name for a in self.base_algorithms]:

                # 兼容 prediction 可能是单个推荐字典，也可能是包含 recommendations 列表的完整输出
                if 'recommendations' in prediction:
                    recommendations = prediction['recommendations']
                else:
                    # 如果只是一个推荐字典，将其包装成列表以兼容投票逻辑
                    recommendations = [prediction]

                all_predictions_for_voting[algo_name] = {
                    'predictions': recommendations,
                    'weight': self.current_weights.get(algo_name, 1.0 / len(self.base_algorithms))
                }

        # 调用已有的动态集成投票方法
        final_prediction = self._dynamic_ensemble_voting(all_predictions_for_voting)

        # 构建并返回最终的报告
        return {
            'algorithm': self.name,
            'version': self.version,
            'individual_predictions': individual_predictions,  # 将原始输入也包含在内，便于追溯
            'recommendations': [final_prediction],
            'analysis': {
                'current_weights': self.current_weights,
                'algorithms_used': list(all_predictions_for_voting.keys()),
                'ensemble_method': 'dynamic_weighted_with_precomputed'  # 标记来源
            }
        }

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练集成优化器"""
        if len(history_data) < 30:
            return False

        # 初始化训练所有基础算法
        for algorithm in self.base_algorithms:
            algorithm.train(history_data)

        # 基于历史表现初始化权重
        self._initialize_weights(history_data)

        self.is_trained = True
        return True

    def _initialize_weights(self, history_data: List[LotteryHistory]):
        """基于历史表现初始化算法权重"""
        performance_scores = {}

        # 使用滑动窗口评估每个算法
        window_size = min(self.parameters['evaluation_window'], len(history_data) - 10)

        for algorithm in self.base_algorithms:
            algorithm_performance = []

            for start_idx in range(10, len(history_data) - window_size, 5):
                train_subset = history_data[:start_idx]
                test_subset = history_data[start_idx:start_idx + window_size]

                algorithm.train(train_subset)
                accuracy = self._evaluate_algorithm(algorithm, train_subset, test_subset)
                algorithm_performance.append(accuracy)

            # 计算平均表现
            if algorithm_performance:
                performance_scores[algorithm.name] = np.mean(algorithm_performance)
            else:
                performance_scores[algorithm.name] = 0.1  # 默认值

        # 归一化权重
        total_performance = sum(performance_scores.values())
        if total_performance > 0:
            self.current_weights = {
                name: score / total_performance
                for name, score in performance_scores.items()
            }
        else:
            # 等权重回退
            self.current_weights = {
                algorithm.name: 1.0 / len(self.base_algorithms)
                for algorithm in self.base_algorithms
            }

    def _evaluate_algorithm(self, algorithm: BaseAlgorithm,
                            train_data: List[LotteryHistory],
                            test_data: List[LotteryHistory]) -> float:
        """评估算法在测试集上的表现"""
        correct_predictions = 0
        total_evaluations = 0

        for i in range(len(test_data) - 1):
            try:
                result = algorithm.predict(train_data + test_data[:i])
                if 'recommendations' in result:
                    actual_next = test_data[i + 1]

                    for rec in result['recommendations'][:2]:  # 评估前2个推荐
                        front_hits = len(set(rec.get('front_numbers', [])) & set(actual_next.front_area))
                        back_hits = len(set(rec.get('back_numbers', [])) & set(actual_next.back_area))

                        # 综合评分标准
                        if front_hits >= 3 or (front_hits >= 2 and back_hits >= 1):
                            correct_predictions += 1
                        total_evaluations += 1
            except:
                continue

        return correct_predictions / total_evaluations if total_evaluations > 0 else 0

    def update_weights(self, latest_result: LotteryHistory, predictions: Dict):
        """根据最新开奖结果更新权重"""
        for algo_name, algo_predictions in predictions.items():
            if algo_name in self.current_weights:
                # 计算该算法的最新表现
                accuracy = self._calculate_single_accuracy(algo_predictions, latest_result)
                self.performance_history[algo_name].append(accuracy)

                # 限制历史记录长度
                if len(self.performance_history[algo_name]) > self.parameters['evaluation_window']:
                    self.performance_history[algo_name].pop(0)

                # 更新权重（考虑衰减）
                recent_performance = np.mean(self.performance_history[algo_name][-5:])  # 最近5次
                decayed_weight = self.current_weights[algo_name] * self.parameters['weight_decay_factor']
                new_weight = decayed_weight + (1 - self.parameters['weight_decay_factor']) * recent_performance

                self.current_weights[algo_name] = max(0.01, new_weight)  # 最小权重1%

        # 重新归一化权重
        self._normalize_weights()

    def _calculate_single_accuracy(self, predictions: List[Dict], actual: LotteryHistory) -> float:
        """计算单次预测准确度"""
        if not predictions:
            return 0.0

        best_pred = predictions[0]
        front_hits = len(set(best_pred.get('front_numbers', [])) & set(actual.front_area))
        back_hits = len(set(best_pred.get('back_numbers', [])) & set(actual.back_area))

        # 综合命中评分
        front_score = front_hits / 5.0
        back_score = back_hits / 2.0
        return 0.7 * front_score + 0.3 * back_score

    def _normalize_weights(self):
        """归一化权重"""
        total_weight = sum(self.current_weights.values())
        if total_weight > 0:
            self.current_weights = {
                k: v / total_weight
                for k, v in self.current_weights.items()
            }

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """动态集成预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 收集所有算法预测
        all_predictions = {}
        for algorithm in self.base_algorithms:
            try:
                result = algorithm.predict(history_data)
                if 'recommendations' in result:
                    all_predictions[algorithm.name] = {
                        'predictions': result['recommendations'],
                        'weight': self.current_weights.get(algorithm.name, 0.1)
                    }
            except Exception as e:
                print(f"算法 {algorithm.name} 预测失败: {e}")
                continue

        # 动态集成投票
        final_prediction = self._dynamic_ensemble_voting(all_predictions)

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [final_prediction],
            'analysis': {
                'current_weights': self.current_weights,
                'algorithms_used': list(all_predictions.keys()),
                'ensemble_method': 'dynamic_weighted'
            }
        }

    def _dynamic_ensemble_voting(self, all_predictions: Dict) -> Dict[str, Any]:
        """动态加权投票"""
        front_votes = defaultdict(float)
        back_votes = defaultdict(float)

        for algo_name, algo_data in all_predictions.items():
            weight = algo_data['weight']

            for pred in algo_data['predictions'][:3]:  # 考虑前3个推荐
                confidence = pred.get('confidence', 0.5)

                # 前区投票
                for num in pred.get('front_numbers', []):
                    front_votes[num] += weight * confidence

                # 后区投票
                for num in pred.get('back_numbers', []):
                    back_votes[num] += weight * confidence

        # 选择得票最高的号码
        front_selection = [num for num, _ in sorted(
            front_votes.items(), key=lambda x: x[1], reverse=True
        )[:7]]  # 多选2个用于优化

        back_selection = [num for num, _ in sorted(
            back_votes.items(), key=lambda x: x[1], reverse=True
        )[:3]]  # 多选1个用于优化

        # 号码组合优化
        optimized_front = self._optimize_number_selection(front_selection, 'front')
        optimized_back = self._optimize_number_selection(back_selection, 'back')

        # 计算综合置信度
        total_confidence = sum(
            pred.get('confidence', 0.5) * algo_data['weight']
            for algo_data in all_predictions.values()
            for pred in algo_data['predictions'][:1]
        )

        return {
            'front_numbers': sorted(optimized_front),
            'back_numbers': sorted(optimized_back),
            'confidence': min(0.95, total_confidence),
            'dynamic_weights_applied': True
        }

    def _optimize_number_selection(self, candidates: List[int], area: str) -> List[int]:
        """优化号码选择（考虑间距分布）"""
        if area == 'front':
            target_count = 5
            if len(candidates) <= target_count:
                return candidates

            # 使用贪心算法选择间距最优的组合
            best_combo = None
            best_score = -1

            from itertools import combinations
            for combo in combinations(candidates, target_count):
                sorted_combo = sorted(combo)
                # 计算间距均匀度得分
                gaps = [sorted_combo[i + 1] - sorted_combo[i] for i in range(target_count - 1)]
                gap_variance = np.var(gaps)
                score = 1.0 / (1.0 + gap_variance)  # 方差越小得分越高

                # 考虑奇偶平衡
                odd_count = sum(1 for num in sorted_combo if num % 2 == 1)
                parity_balance = 1.0 - abs(odd_count - target_count / 2) / (target_count / 2)
                score *= (0.7 + 0.3 * parity_balance)  # 奇偶平衡权重30%

                if score > best_score:
                    best_score = score
                    best_combo = sorted_combo

            return list(best_combo) if best_combo else candidates[:target_count]

        else:  # 后区
            target_count = 2
            if len(candidates) <= target_count:
                return candidates

            # 选择差异最大的两个号码
            best_pair = None
            max_diff = -1

            for i in range(len(candidates)):
                for j in range(i + 1, len(candidates)):
                    diff = abs(candidates[i] - candidates[j])
                    if diff > max_diff:
                        max_diff = diff
                        best_pair = [candidates[i], candidates[j]]

            return sorted(best_pair) if best_pair else candidates[:target_count]