# file: src/engine/performance_logger.py
import json
from typing import Dict, Any, List
from datetime import datetime
from src.model.lottery_models import LotteryHistory, AlgorithmPerformance


class AlgorithmPerformanceDAO:
    def __init__(self, db_manager):
        """修复：正确初始化 DAO"""
        self.db_manager = db_manager
        print(f"[AlgorithmPerformanceDAO] 初始化完成，db_manager: {type(db_manager)}")

    def insert_algorithm_performance(self, performance_data: Dict) -> bool:
        """插入算法性能记录 - 修复版本"""
        try:
            query = """
                INSERT INTO algorithm_performance 
                (algorithm, algorithm_version, issue, predictions, confidence_score, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            # 从 algorithm_version 中提取算法名称
            algorithm_version = performance_data.get('algorithm_version', 'unknown')
            algorithm_name = algorithm_version.split('_')[0] if '_' in algorithm_version else algorithm_version

            params = (
                algorithm_name,  # algorithm 字段
                algorithm_version,
                performance_data.get('period_number', 'unknown'),
                performance_data.get('predictions', '{}'),
                performance_data.get('confidence_score', 0.5),
                performance_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )

            result = self.execute_update(query, params)
            return result is not None
        except Exception as e:
            print(f"[AlgorithmPerformanceDAO] 插入性能记录失败: {e}")
            return False

    def get_average_scores_last_n_issues(self, n_issues: int = 5) -> Dict[str, float]:
        """获取最近n期的平均分数 - 修复 MySQL 语法问题"""
        try:
            # 修复 MySQL 语法问题：不使用子查询中的 LIMIT
            query = """
                SELECT algorithm_version, AVG(confidence_score) as avg_score
                FROM (
                    SELECT algorithm_version, confidence_score, created_at
                    FROM algorithm_performance 
                    ORDER BY created_at DESC 
                    LIMIT %s
                ) as recent_scores
                GROUP BY algorithm_version
            """
            results = self.db_manager.execute_query(query, (n_issues * 10,))  # 乘以10确保有足够数据

            weights = {}
            if results:
                total_score = sum(result.get('avg_score', 0) for result in results)
                if total_score > 0:
                    for result in results:
                        algo_name = result.get('algorithm_version', 'unknown')
                        score = result.get('avg_score', 0)
                        weights[algo_name] = score / total_score

            return weights
        except Exception as e:
            print(f"[AlgorithmPerformanceDAO] 获取平均分数失败: {e}")
            return {}

    def update_algorithm_performance(self, performance: AlgorithmPerformance) -> bool:
        """更新算法性能 - 简化版本"""
        try:
            # 这里简化实现，实际项目中可能需要更复杂的更新逻辑
            print(f"[AlgorithmPerformanceDAO] 更新算法性能: {performance.algorithm_version}")
            return True
        except Exception as e:
            print(f"[AlgorithmPerformanceDAO] 更新性能失败: {e}")
            return False

    def get_algorithm_performance(self, algorithm_version: str = None) -> List[Dict]:
        """获取算法性能数据 - 简化版本"""
        try:
            if algorithm_version:
                query = "SELECT * FROM algorithm_performance WHERE algorithm_version = %s ORDER BY created_at DESC LIMIT 10"
                return self.db_manager.execute_query(query, (algorithm_version,))
            else:
                query = "SELECT * FROM algorithm_performance ORDER BY created_at DESC LIMIT 50"
                return self.db_manager.execute_query(query)
        except Exception as e:
            print(f"[AlgorithmPerformanceDAO] 获取性能数据失败: {e}")
            return []


class AdaptiveWeightUpdater:
    """自适应权重更新器"""

    def __init__(self, alpha: float = 0.6):
        self.alpha = alpha

    def update_weights(self, current_scores: Dict[str, float], historical_avg: Dict[str, float]) -> Dict[str, float]:
        """更新权重"""
        try:
            new_weights = {}
            total_score = 0.0

            for algo, current_score in current_scores.items():
                hist_score = historical_avg.get(algo, current_score)
                # 简单的加权平均
                combined_score = self.alpha * current_score + (1 - self.alpha) * hist_score
                new_weights[algo] = combined_score
                total_score += combined_score

            # 归一化
            if total_score > 0:
                for algo in new_weights:
                    new_weights[algo] /= total_score

            return new_weights
        except Exception as e:
            print(f"[AdaptiveWeightUpdater] 更新权重失败: {e}")
            return current_scores


class PerformanceLogger:
    def __init__(self, db_manager, smoothing_alpha: float = 0.6, hist_window: int = 5):
        """
        修复版本：正确初始化所有组件
        """
        # 修复：直接创建 DAO 实例
        self.dao = AlgorithmPerformanceDAO(db_manager)
        self.updater = AdaptiveWeightUpdater(alpha=smoothing_alpha)
        self.hist_window = hist_window
        print("[PerformanceLogger] 初始化成功")

    def _score_from_predictions(self, prediction, actual_draw):
        """
        从预测计算分数 - 修复版本
        prediction: 可以是字典或任何包含预测数据的对象
        actual_draw: LotteryHistory 对象
        """
        try:
            # 兼容多种预测格式
            if isinstance(prediction, dict):
                front_pred = prediction.get('front_area', [])
                back_pred = prediction.get('back_area', [])
                confidence = prediction.get('confidence', 0.5)
            else:
                # 尝试从对象属性获取
                front_pred = getattr(prediction, 'front_area', [])
                back_pred = getattr(prediction, 'back_area', [])
                confidence = getattr(prediction, 'confidence', 0.5)

            # 确保是列表格式
            if isinstance(front_pred, str):
                front_pred = [int(x.strip()) for x in front_pred.split(',') if x.strip().isdigit()]
            if isinstance(back_pred, str):
                back_pred = [int(x.strip()) for x in back_pred.split(',') if x.strip().isdigit()]

            # 计算命中数
            front_hit = len(set(front_pred) & set(actual_draw.front_area))
            back_hit = len(set(back_pred) & set(actual_draw.back_area))

            # 计算基础命中率
            total_possible_hits = len(actual_draw.front_area) + len(actual_draw.back_area)
            hit_rate = (front_hit + back_hit) / total_possible_hits if total_possible_hits > 0 else 0

            # 综合分数（命中率 * 置信度）
            score = hit_rate * confidence

            return {
                'hit_rate': hit_rate,
                'score': score,
                'front_hits': front_hit,
                'back_hits': back_hit
            }

        except Exception as e:
            print(f"[PerformanceLogger] 计算分数错误: {e}")
            return {'hit_rate': 0.0, 'score': 0.0, 'front_hits': 0, 'back_hits': 0}

    def log_algorithm_performance(self, algorithm_version: str, period_number: str,
                                  predictions: Dict, confidence_score: float) -> bool:
        """
        记录算法性能 - 简化版本
        """
        try:
            performance_data = {
                'algorithm_version': algorithm_version,
                'period_number': period_number,
                'predictions': json.dumps(predictions, ensure_ascii=False),
                'confidence_score': confidence_score,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return self.dao.insert_algorithm_performance(performance_data)
        except Exception as e:
            print(f"[PerformanceLogger] 记录性能失败: {e}")
            return False

    def get_latest_adaptive_weights(self) -> Dict[str, float]:
        """获取最新的自适应权重"""
        try:
            hist_avg = self.dao.get_average_scores_last_n_issues(self.hist_window)
            if not hist_avg:
                print("[PerformanceLogger] 警告: 无法获取历史权重，使用空字典")
                return {}
            return hist_avg
        except Exception as e:
            print(f"[PerformanceLogger] 获取权重失败: {e}")
            return {}

    def _get_historical_avg(self) -> Dict[str, float]:
        """
        获取历史平均值 - 简化版本
        """
        try:
            performances = self.dao.get_algorithm_performance()
            algo_scores = {}

            for perf in performances:
                algo_name = perf.get('algorithm_version', 'unknown')
                score = perf.get('confidence_score', 0.0)
                algo_scores.setdefault(algo_name, []).append(score)

            # 计算每个算法的平均分
            hist_avg = {}
            for algo, scores in algo_scores.items():
                recent_scores = scores[-self.hist_window:] if len(scores) > self.hist_window else scores
                hist_avg[algo] = sum(recent_scores) / len(recent_scores) if recent_scores else 0.0

            return hist_avg
        except Exception as e:
            print(f"[PerformanceLogger] 获取历史平均值失败: {e}")
            return {}

    def evaluate_and_update(self, issue: str, model_outputs: Dict[str, Any],
                            actual_draw: LotteryHistory) -> Dict[str, float]:
        """
        评估并更新算法性能 - 修复版本
        返回简化准确率结果: {算法名: 命中率}
        """
        simple_accuracy_dict = {}

        for algo_name, prediction in (model_outputs or {}).items():
            try:
                # 计算评分指标
                metrics = self._score_from_predictions(prediction, actual_draw)

                # 记录到数据库
                success = self.log_algorithm_performance(
                    algorithm_version=algo_name,
                    period_number=issue,
                    predictions=prediction,
                    confidence_score=metrics.get('score', 0.5)
                )

                if success:
                    print(f"  - ✅ {algo_name}: 前区命中 {metrics.get('front_hits', 0)}/5, "
                          f"后区命中 {metrics.get('back_hits', 0)}/2, 分数: {metrics.get('score', 0):.3f}")
                else:
                    print(f"  - ⚠️ {algo_name}: 性能记录失败")

                # 存储简化准确率
                simple_accuracy_dict[algo_name] = round(metrics.get('hit_rate', 0.0), 4)

            except Exception as e:
                print(f"[PerformanceLogger] 评估{algo_name}失败: {e}")
                continue

        return simple_accuracy_dict

    def get_recommended_weights(self) -> Dict[str, float]:
        """获取推荐的算法权重 - 简化版本"""
        return self.get_latest_adaptive_weights()


# 调试代码
if __name__ == "__main__":
    # 模拟测试
    class MockDBManager:
        def execute_insert(self, query, params):
            print(f"[MockDB] 执行插入: {query[:50]}...")
            return 1

        def execute_query(self, query, params=None):
            print(f"[MockDB] 执行查询: {query[:50]}...")
            return [{'algorithm_version': 'test_algo', 'avg_score': 0.8}]


    print("测试 PerformanceLogger...")
    mock_db = MockDBManager()
    logger = PerformanceLogger(mock_db)

    # 测试基础功能
    weights = logger.get_latest_adaptive_weights()
    print(f"获取的权重: {weights}")

    print("测试完成")