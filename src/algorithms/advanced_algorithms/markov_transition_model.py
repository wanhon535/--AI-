# src/algorithms/advanced_algorithms/markov_transition_model.py
import numpy as np
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any
import logging


class MarkovTransitionModel(BaseAlgorithm):
    """马尔可夫转移模型 - 基于号码转移概率的预测"""
    name = "MarkovTransitionModel"
    version = "1.0"

    def __init__(self):
        super().__init__()
        self.front_transition_matrix = None  # 前区转移矩阵 35x35
        self.back_transition_matrix = None  # 后区转移矩阵 12x12
        self.stationary_distribution = None  # 平稳分布

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练马尔可夫模型 - 构建转移概率矩阵"""
        if not history_data or len(history_data) < 2:
            return False

        try:
            # 准备数据
            sorted_data = sorted(history_data, key=lambda x: x.period_number)

            # 构建前区转移矩阵
            self.front_transition_matrix = self._build_transition_matrix(sorted_data, 'front', 35)

            # 构建后区转移矩阵
            self.back_transition_matrix = self._build_transition_matrix(sorted_data, 'back', 12)

            # 计算平稳分布
            self._calculate_stationary_distribution()

            self.is_trained = True
            logging.info(f"马尔可夫模型训练完成，转移矩阵构建成功")
            return True

        except Exception as e:
            logging.error(f"马尔可夫模型训练失败: {e}")
            return False

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于马尔可夫转移概率进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        try:
            # 获取最近一期号码作为当前状态
            if not history_data:
                return {'error': '没有历史数据'}

            latest_record = sorted(history_data, key=lambda x: x.period_number)[-1]

            # 基于当前状态预测下一期
            front_recommendations = self._predict_next_numbers(latest_record.front_area, 'front')
            back_recommendations = self._predict_next_numbers(latest_record.back_area, 'back')

            # 计算置信度
            confidence = self._calculate_markov_confidence()

            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{
                    'front_number_scores': front_recommendations,
                    'back_number_scores': back_recommendations,
                    'confidence': confidence,
                    'current_state': {
                        'front': latest_record.front_area,
                        'back': latest_record.back_area
                    }
                }],
                'analysis': {
                    'transition_matrix_info': self._get_matrix_info(),
                    'stationary_distribution': self.stationary_distribution
                }
            }

        except Exception as e:
            logging.error(f"马尔可夫预测失败: {e}")
            return {'error': str(e)}

    def _build_transition_matrix(self, history_data: List[LotteryHistory], area_type: str,
                                 num_count: int) -> np.ndarray:
        """构建转移概率矩阵"""
        # 初始化转移计数矩阵
        transition_counts = np.zeros((num_count, num_count))

        for i in range(len(history_data) - 1):
            current_record = history_data[i]
            next_record = history_data[i + 1]

            # 获取当前期和下一期的号码
            current_numbers = current_record.front_area if area_type == 'front' else current_record.back_area
            next_numbers = next_record.front_area if area_type == 'front' else next_record.back_area

            # 更新转移计数
            for curr_num in current_numbers:
                for next_num in next_numbers:
                    transition_counts[curr_num - 1][next_num - 1] += 1

        # 转换为概率矩阵（添加拉普拉斯平滑）
        transition_matrix = self._normalize_with_smoothing(transition_counts)

        logging.info(f"构建了{area_type}区{num_count}x{num_count}转移矩阵")
        return transition_matrix

    def _normalize_with_smoothing(self, counts: np.ndarray, alpha: float = 0.01) -> np.ndarray:
        """归一化转移计数矩阵（带拉普拉斯平滑）"""
        # 减小平滑参数，从0.1改为0.01
        smoothed = counts + alpha
        row_sums = smoothed.sum(axis=1, keepdims=True)

        # 避免除以零
        row_sums[row_sums == 0] = 1

        return smoothed / row_sums

    def _calculate_stationary_distribution(self):
        """计算马尔可夫链的平稳分布"""
        try:
            # 使用幂迭代法计算平稳分布
            if self.front_transition_matrix is not None:
                front_stationary = self._power_iteration(self.front_transition_matrix.T)
                back_stationary = self._power_iteration(self.back_transition_matrix.T)

                self.stationary_distribution = {
                    'front': front_stationary.tolist(),
                    'back': back_stationary.tolist()
                }
        except Exception as e:
            logging.warning(f"计算平稳分布失败: {e}")

    def _power_iteration(self, matrix: np.ndarray, max_iter: int = 1000, tol: float = 1e-8) -> np.ndarray:
        """幂迭代法计算矩阵的主特征向量（平稳分布）"""
        n = matrix.shape[0]
        x = np.ones(n) / n  # 初始分布

        for _ in range(max_iter):
            x_new = matrix @ x
            x_new = x_new / np.sum(x_new)  # 归一化

            if np.linalg.norm(x_new - x) < tol:
                break
            x = x_new

        return x

    def _predict_next_numbers(self, current_numbers: List[int], area_type: str) -> List[Dict[str, Any]]:
        """预测下一期号码的概率"""
        transition_matrix = self.front_transition_matrix if area_type == 'front' else self.back_transition_matrix
        num_count = 35 if area_type == 'front' else 12

        # 计算每个号码的转移概率得分
        scores = []
        for next_num in range(1, num_count + 1):
            score = 0.0

            # 基于当前号码的转移概率
            for curr_num in current_numbers:
                if curr_num <= num_count:  # 确保号码在有效范围内
                    score += transition_matrix[curr_num - 1][next_num - 1]

            # 平均转移概率
            if current_numbers:
                score /= len(current_numbers)

            # 结合平稳分布
            if self.stationary_distribution:
                stationary_prob = self.stationary_distribution[area_type][next_num - 1]
                score = 0.7 * score + 0.3 * stationary_prob

            scores.append({
                'number': next_num,
                'score': float(score),
                'transition_from': current_numbers
            })

        # 按评分排序
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores

    def _calculate_markov_confidence(self) -> float:
        """计算马尔可夫模型的置信度"""
        confidence = 0.7  # 基础置信度

        # 基于转移矩阵的质量调整置信度
        if self.front_transition_matrix is not None and self.back_transition_matrix is not None:
            # 检查矩阵的稀疏度
            front_sparsity = np.mean(self.front_transition_matrix == 0)
            back_sparsity = np.mean(self.back_transition_matrix == 0)

            # 较低的稀疏度通常意味着更好的模型
            if front_sparsity < 0.8 and back_sparsity < 0.8:
                confidence += 0.2

        return min(confidence, 0.9)

    def _get_matrix_info(self) -> Dict[str, Any]:
        """获取转移矩阵信息"""
        if self.front_transition_matrix is None or self.back_transition_matrix is None:
            return {}

        return {
            'dimensions': {
                'front': f"{self.front_transition_matrix.shape[0]}x{self.front_transition_matrix.shape[1]}",
                'back': f"{self.back_transition_matrix.shape[0]}x{self.back_transition_matrix.shape[1]}"
            },
            'sparsity': {
                'front': float(np.mean(self.front_transition_matrix == 0)),
                'back': float(np.mean(self.back_transition_matrix == 0))
            },
            'avg_transition_prob': {
                'front': float(np.mean(self.front_transition_matrix)),
                'back': float(np.mean(self.back_transition_matrix))
            }
        }