# src/algorithms/advanced_algorithms/real_time_feedback_learner.py
import numpy as np
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any, Tuple
import logging
from collections import defaultdict, deque
import sqlite3
from datetime import datetime


class RealTimeFeedbackLearner(BaseAlgorithm):
    """实时反馈学习器 - 基于近期表现动态调整预测策略"""
    name = "RealTimeFeedbackLearner"
    version = "1.0"

    def __init__(self, feedback_window: int = 50):
        super().__init__()
        self.feedback_window = feedback_window  # 反馈窗口大小
        self.performance_history = deque(maxlen=feedback_window)
        self.recent_predictions = deque(maxlen=20)
        self.adaptation_weights = {'frequency': 0.3, 'recency': 0.4, 'performance': 0.3}
        self.number_trends = {}
        self.is_trained = False

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练实时反馈模型"""
        if not history_data or len(history_data) < 30:
            logging.error("数据量不足，无法训练实时反馈模型")
            return False

        try:
            # 分析号码趋势
            self._analyze_number_trends(history_data)

            # 初始化性能历史
            self._initialize_performance_history(history_data)

            self.is_trained = True
            logging.info(f"实时反馈学习器训练完成，反馈窗口: {self.feedback_window}")
            return True

        except Exception as e:
            logging.error(f"实时反馈学习器训练失败: {e}")
            return False

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于实时反馈进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        try:
            # 获取最新数据用于分析
            recent_data = history_data[-min(100, len(history_data)):]

            # 生成基于反馈的预测
            front_predictions = self._feedback_based_prediction(recent_data, 'front')
            back_predictions = self._feedback_based_prediction(recent_data, 'back')

            # 计算动态置信度
            confidence = self._calculate_dynamic_confidence()

            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{
                    'front_number_scores': front_predictions,
                    'back_number_scores': back_predictions,
                    'confidence': confidence,
                    'feedback_metrics': self._get_feedback_metrics()
                }],
                'analysis': {
                    'performance_history': list(self.performance_history)[-10:],  # 最近10次表现
                    'current_trends': self._get_current_trends(recent_data),
                    'adaptation_strategy': self.adaptation_weights
                }
            }

        except Exception as e:
            logging.error(f"实时反馈预测失败: {e}")
            return {'error': str(e)}

    def update_feedback(self, prediction_result: Dict[str, Any], actual_numbers) -> bool:
        """更新预测反馈"""
        try:
            # 计算预测准确率
            accuracy = self._calculate_prediction_accuracy(prediction_result, actual_numbers)

            # 记录性能历史
            self.performance_history.append({
                'timestamp': datetime.now(),
                'accuracy': accuracy,
                'prediction_type': 'combined'
            })

            # 记录预测
            self.recent_predictions.append({
                'prediction': prediction_result,
                'actual': actual_numbers,
                'accuracy': accuracy
            })

            # 动态调整权重
            self._adapt_weights_based_on_performance()

            logging.info(f"反馈更新完成，准确率: {accuracy:.4f}")
            return True

        except Exception as e:
            logging.error(f"反馈更新失败: {e}")
            return False

    def process_feedback(self, prediction_result: Dict[str, Any], actual_numbers) -> bool:
        """处理预测反馈（update_feedback的别名方法）"""
        return self.update_feedback(prediction_result, actual_numbers)

    def _analyze_number_trends(self, history_data: List[LotteryHistory]):
        """分析号码趋势"""
        self.number_trends = {
            'front': defaultdict(list),
            'back': defaultdict(list)
        }

        for i, record in enumerate(history_data):
            # 前区号码趋势
            for number in record.front_area:
                self.number_trends['front'][number].append({
                    'draw_index': i,
                    'timestamp': record.draw_time,
                    'occurred': True
                })

            # 后区号码趋势
            for number in record.back_area:
                self.number_trends['back'][number].append({
                    'draw_index': i,
                    'timestamp': record.draw_time,
                    'occurred': True
                })

    def _initialize_performance_history(self, history_data: List[LotteryHistory]):
        """初始化性能历史"""
        # 模拟历史性能数据
        for i in range(min(self.feedback_window, len(history_data) - 10)):
            # 使用随机准确率初始化，实际应用中可以根据历史预测计算
            base_accuracy = 0.3 + 0.4 * (i / min(self.feedback_window, len(history_data)))
            self.performance_history.append({
                'timestamp': history_data[i].draw_time if i < len(history_data) else datetime.now(),
                'accuracy': base_accuracy,
                'prediction_type': 'historical'
            })

    def _feedback_based_prediction(self, recent_data: List[LotteryHistory], area_type: str) -> List[Dict[str, Any]]:
        """基于反馈的预测"""
        predictions = []
        number_range = range(1, 36) if area_type == 'front' else range(1, 13)

        for number in number_range:
            # 计算基于频率的得分
            freq_score = self._calculate_frequency_score(number, area_type, recent_data)

            # 计算基于近期表现的得分
            recency_score = self._calculate_recency_score(number, area_type, recent_data)

            # 计算基于趋势的得分
            trend_score = self._calculate_trend_score(number, area_type)

            # 综合得分
            composite_score = (
                    self.adaptation_weights['frequency'] * freq_score +
                    self.adaptation_weights['recency'] * recency_score +
                    self.adaptation_weights['performance'] * trend_score
            )

            predictions.append({
                'number': number,
                'score': round(composite_score, 4),
                'score_breakdown': {
                    'frequency': round(freq_score, 4),
                    'recency': round(recency_score, 4),
                    'trend': round(trend_score, 4)
                },
                'recent_performance': self._get_number_recent_performance(number, area_type)
            })

        # 按得分排序
        predictions.sort(key=lambda x: x['score'], reverse=True)
        return predictions

    def _calculate_frequency_score(self, number: int, area_type: str, recent_data: List[LotteryHistory]) -> float:
        """计算频率得分"""
        if area_type == 'front':
            occurrences = sum(1 for record in recent_data if number in record.front_area)
        else:
            occurrences = sum(1 for record in recent_data if number in record.back_area)

        max_possible = len(recent_data)
        return occurrences / max_possible if max_possible > 0 else 0.1

    def _calculate_recency_score(self, number: int, area_type: str, recent_data: List[LotteryHistory]) -> float:
        """计算近期表现得分"""
        # 查看最近20期表现
        recent_window = min(20, len(recent_data))
        recent_occurrences = 0

        for i in range(1, recent_window + 1):
            record = recent_data[-i]
            if area_type == 'front':
                if number in record.front_area:
                    recent_occurrences += (recent_window - i + 1)  # 越近权重越高
            else:
                if number in record.back_area:
                    recent_occurrences += (recent_window - i + 1)

        max_score = sum(range(1, recent_window + 1))
        return recent_occurrences / max_score if max_score > 0 else 0.1

    def _calculate_trend_score(self, number: int, area_type: str) -> float:
        """计算趋势得分"""
        trends = self.number_trends[area_type].get(number, [])
        if len(trends) < 3:
            return 0.1

        # 分析最近出现模式
        recent_trends = trends[-10:]  # 最近10次出现
        if not recent_trends:
            return 0.1

        # 简单趋势分析：如果近期频繁出现则得分高
        return min(len(recent_trends) / 10.0, 1.0)

    def _calculate_dynamic_confidence(self) -> float:
        """计算动态置信度"""
        if not self.performance_history:
            return 0.5

        # 基于近期表现计算置信度
        recent_performance = list(self.performance_history)[-10:]
        if not recent_performance:
            return 0.5

        avg_accuracy = np.mean([p['accuracy'] for p in recent_performance])

        # 稳定性因子
        stability = 1.0 - np.std([p['accuracy'] for p in recent_performance])

        confidence = avg_accuracy * 0.7 + stability * 0.3
        return min(max(confidence, 0.1), 0.95)

    def _calculate_prediction_accuracy(self, prediction: Dict[str, Any], actual_numbers) -> float:
        """计算预测准确率"""
        try:
            if 'recommendations' not in prediction or not prediction['recommendations']:
                return 0.0

            rec = prediction['recommendations'][0]

            # 确保我们获取的是前区号码得分列表和后区号码得分列表
            front_scores = rec.get('front_number_scores', [])
            back_scores = rec.get('back_number_scores', [])

            # 提取号码而不是整个对象
            predicted_front = []
            if front_scores and isinstance(front_scores, list):
                for item in front_scores[:5]:  # 取前5个推荐号码
                    if isinstance(item, dict) and 'number' in item:
                        predicted_front.append(item['number'])
                    elif isinstance(item, (int, float)):
                        predicted_front.append(int(item))

            predicted_back = []
            if back_scores and isinstance(back_scores, list):
                for item in back_scores[:2]:  # 取前2个推荐号码
                    if isinstance(item, dict) and 'number' in item:
                        predicted_back.append(item['number'])
                    elif isinstance(item, (int, float)):
                        predicted_back.append(int(item))

            # 确保actual_numbers是列表格式
            if hasattr(actual_numbers, 'front_area') and hasattr(actual_numbers, 'back_area'):
                # 如果传入的是LotteryHistory对象
                actual_front = actual_numbers.front_area
                actual_back = actual_numbers.back_area
            else:
                # 如果传入的是列表
                actual_front = actual_numbers[:5] if len(actual_numbers) >= 5 else []
                actual_back = actual_numbers[5:7] if len(actual_numbers) >= 7 else []

            # 计算前区匹配数
            front_match = len(set(predicted_front) & set(actual_front)) if predicted_front and actual_front else 0
            back_match = len(set(predicted_back) & set(actual_back)) if predicted_back and actual_back else 0

            # 综合准确率（前区权重0.7，后区权重0.3）
            accuracy = (front_match / 5 * 0.7) + (back_match / 2 * 0.3) if front_match + back_match > 0 else 0.0
            return accuracy

        except Exception as e:
            logging.error(f"准确率计算失败: {e}")
            return 0.0

    def _adapt_weights_based_on_performance(self):
        """根据性能动态调整权重"""
        if len(self.performance_history) < 10:
            return

        recent_performance = list(self.performance_history)[-10:]
        recent_accuracies = [p['accuracy'] for p in recent_performance]

        avg_accuracy = np.mean(recent_accuracies)

        # 根据平均准确率调整权重
        if avg_accuracy < 0.3:
            # 表现不佳，增加频率权重
            self.adaptation_weights = {'frequency': 0.5, 'recency': 0.3, 'performance': 0.2}
        elif avg_accuracy > 0.6:
            # 表现良好，保持当前策略
            self.adaptation_weights = {'frequency': 0.3, 'recency': 0.4, 'performance': 0.3}
        else:
            # 中等表现，平衡策略
            self.adaptation_weights = {'frequency': 0.4, 'recency': 0.35, 'performance': 0.25}

    def _get_feedback_metrics(self) -> Dict[str, Any]:
        """获取反馈指标"""
        if not self.performance_history:
            return {}

        recent_performance = list(self.performance_history)[-10:]
        accuracies = [p['accuracy'] for p in recent_performance]

        return {
            'recent_accuracy_avg': round(np.mean(accuracies), 4),
            'recent_accuracy_std': round(np.std(accuracies), 4),
            'performance_trend': 'improving' if len(accuracies) > 1 and accuracies[-1] > accuracies[0] else 'declining',
            'feedback_count': len(self.performance_history),
            'current_weights': self.adaptation_weights
        }

    def _get_current_trends(self, recent_data: List[LotteryHistory]) -> Dict[str, Any]:
        """获取当前趋势"""
        if not recent_data:
            return {}

        # 分析最近10期的热门号码
        recent_window = min(10, len(recent_data))
        recent_records = recent_data[-recent_window:]

        front_counts = defaultdict(int)
        back_counts = defaultdict(int)

        for record in recent_records:
            for num in record.front_area:
                front_counts[num] += 1
            for num in record.back_area:
                back_counts[num] += 1

        return {
            'hot_front_numbers': sorted(front_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'hot_back_numbers': sorted(back_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'cold_front_numbers': sorted(front_counts.items(), key=lambda x: x[1])[:5],
            'cold_back_numbers': sorted(back_counts.items(), key=lambda x: x[1])[:3]
        }

    def _get_number_recent_performance(self, number: int, area_type: str) -> Dict[str, Any]:
        """获取号码近期表现"""
        trends = self.number_trends[area_type].get(number, [])
        if not trends:
            return {'occurrence_count': 0, 'last_occurrence': None, 'trend': 'cold'}

        recent_trends = trends[-10:]
        return {
            'occurrence_count': len(trends),
            'recent_occurrence_count': len(recent_trends),
            'last_occurrence': trends[-1]['timestamp'] if trends else None,
            'trend': 'hot' if len(recent_trends) >= 3 else 'warm' if len(recent_trends) >= 1 else 'cold'
        }

    def test_with_database_data(self, db_path: str) -> Dict[str, Any]:
        """使用数据库中的真实数据进行测试"""
        try:
            # 连接数据库获取数据
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 获取最新的100条历史数据
            cursor.execute("""
                SELECT draw_time, front_area, back_area 
                FROM lottery_history 
                ORDER BY draw_time DESC 
                LIMIT 100
            """)

            results = cursor.fetchall()
            history_data = []

            for row in results:
                history_data.append(LotteryHistory(
                    draw_time=datetime.fromisoformat(row[0]),
                    front_area=eval(row[1]),  # 假设存储为字符串形式的列表
                    back_area=eval(row[2])
                ))

            history_data.reverse()  # 按时间正序排列
            conn.close()

            if not history_data:
                return {'error': '数据库中没有数据'}

            # 使用前80%的数据训练
            train_size = int(len(history_data) * 0.8)
            train_data = history_data[:train_size]
            test_data = history_data[train_size:]

            # 训练模型
            if not self.train(train_data):
                return {'error': '模型训练失败'}

            # 在测试集上进行预测和评估
            test_results = []

            for i, record in enumerate(test_data):
                # 使用截至当前记录的历史数据进行预测
                current_history = history_data[:train_size + i]
                prediction = self.predict(current_history)

                if 'error' not in prediction:
                    # 记录实际开奖号码 - 直接使用LotteryHistory对象
                    actual_numbers = record

                    # 更新反馈
                    self.update_feedback(prediction, actual_numbers)

                    test_results.append({
                        'draw_time': record.draw_time,
                        'prediction': prediction,
                        'actual_numbers': actual_numbers
                    })

            # 计算整体测试指标
            test_metrics = self._calculate_test_metrics(test_results)

            return {
                'test_summary': {
                    'train_size': len(train_data),
                    'test_size': len(test_data),
                    'successful_predictions': len(test_results),
                    'overall_accuracy': test_metrics['overall_accuracy']
                },
                'detailed_results': test_results[:5],  # 返回前5个详细结果
                'performance_metrics': test_metrics,
                'final_feedback_metrics': self._get_feedback_metrics()
            }

        except Exception as e:
            logging.error(f"数据库测试失败: {e}")
            return {'error': f'测试失败: {str(e)}'}

    def _calculate_test_metrics(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算测试指标"""
        if not test_results:
            return {'overall_accuracy': 0.0}

        accuracies = []
        front_accuracies = []
        back_accuracies = []

        for result in test_results:
            prediction = result['prediction']
            actual_numbers = result['actual_numbers']

            if 'recommendations' in prediction and prediction['recommendations']:
                rec = prediction['recommendations'][0]

                # 获取预测的号码
                front_scores = rec.get('front_number_scores', [])
                back_scores = rec.get('back_number_scores', [])

                pred_front = []
                if front_scores and isinstance(front_scores, list):
                    for item in front_scores[:5]:
                        if isinstance(item, dict) and 'number' in item:
                            pred_front.append(item['number'])

                pred_back = []
                if back_scores and isinstance(back_scores, list):
                    for item in back_scores[:2]:
                        if isinstance(item, dict) and 'number' in item:
                            pred_back.append(item['number'])

                # 获取实际号码
                if hasattr(actual_numbers, 'front_area') and hasattr(actual_numbers, 'back_area'):
                    actual_front = actual_numbers.front_area
                    actual_back = actual_numbers.back_area
                else:
                    actual_front = actual_numbers[:5] if len(actual_numbers) >= 5 else []
                    actual_back = actual_numbers[5:7] if len(actual_numbers) >= 7 else []

                # 计算匹配数
                front_match = len(set(pred_front) & set(actual_front)) if pred_front and actual_front else 0
                back_match = len(set(pred_back) & set(actual_back)) if pred_back and actual_back else 0

                # 计算准确率
                front_accuracy = front_match / 5
                back_accuracy = back_match / 2
                overall_accuracy = front_accuracy * 0.7 + back_accuracy * 0.3

                accuracies.append(overall_accuracy)
                front_accuracies.append(front_accuracy)
                back_accuracies.append(back_accuracy)

        return {
            'overall_accuracy': round(np.mean(accuracies), 4) if accuracies else 0.0,
            'front_accuracy': round(np.mean(front_accuracies), 4) if front_accuracies else 0.0,
            'back_accuracy': round(np.mean(back_accuracies), 4) if back_accuracies else 0.0,
            'accuracy_std': round(np.std(accuracies), 4) if accuracies else 0.0,
            'min_accuracy': round(min(accuracies), 4) if accuracies else 0.0,
            'max_accuracy': round(max(accuracies), 4) if accuracies else 0.0
        }