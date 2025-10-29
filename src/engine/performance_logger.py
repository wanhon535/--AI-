# file: src/engine/performance_logger.py
from typing import Dict, Any
from datetime import datetime
from src.model.lottery_models import LotteryHistory, AlgorithmPerformance
from src.database.crud.algorithm_performance_dao import AlgorithmPerformanceDAO
from .adaptive_weight_updater import AdaptiveWeightUpdater
from src.database.database_manager import DatabaseManager

class PerformanceLogger:
    def __init__(self, db_manager, smoothing_alpha: float = 0.6, hist_window: int = 5):
        """
        初始化时，注入一个 DatabaseManager 实例。
        """
        # 使用 db_manager 来获取正确的 DAO 实例
        self.dao: AlgorithmPerformanceDAO = db_manager.get_dao(AlgorithmPerformanceDAO)
        self.updater = AdaptiveWeightUpdater(alpha=smoothing_alpha)
        self.hist_window = hist_window
        print("[PerformanceLogger] Initialized successfully.")

    def _score_from_predictions(self, prediction, actual_draw):
        """
        prediction: ModelPrediction 或老式 dict
        actual_draw: LotteryHistory 对象
        """
        try:
            # 兼容两种类型
            if isinstance(prediction, dict):
                front_pred = prediction.get('front_numbers', [])
                back_pred = prediction.get('back_numbers', [])
                confidence = prediction.get('confidence', 1.0)
            else:  # ModelPrediction 对象
                front_pred = prediction.front_area
                back_pred = prediction.back_area
                confidence = getattr(prediction, 'confidence', 1.0)

            # 计算命中数
            front_hit = len(set(front_pred) & set(actual_draw.front_area))
            back_hit = len(set(back_pred) & set(actual_draw.back_area))

            # 计算命中率
            hit_rate = (front_hit + back_hit) / (len(actual_draw.front_area) + len(actual_draw.back_area))
            score = hit_rate * confidence

            return {'hit_rate': hit_rate, 'score': score}

        except Exception as e:
            print(f"[PerformanceLogger] ⚠️ _score_from_predictions error: {e}")
            return {'hit_rate': 0.0, 'score': 0.0}

    def evaluate_and_log_performance(self, issue: str, model_outputs: Dict[str, Any], actual_draw: LotteryHistory):
        """对本期所有算法的输出进行评估并写入数据库。"""
        print(f"  - [Logger] Evaluating performance for issue {issue}...")
        for algo_name, prediction in (model_outputs or {}).items():
            try:
                metrics = self._score_from_predictions(prediction, actual_draw)
                self.dao.insert_or_update(
                    issue=issue, algorithm=algo_name,
                    hits=metrics['hits'], hit_rate=metrics['hit_rate'], score=metrics['score']
                )
            except Exception as e:
                print(f"  - [Logger] ⚠️ Error evaluating algorithm '{algo_name}': {e}")
        print(f"  - [Logger] ✅ Performance for issue {issue} has been logged to database.")

    def get_latest_adaptive_weights(self) -> Dict[str, float]:
        """获取最新的自适应权重。"""
        # 1. 从数据库获取最近 hist_window 期的历史平均分
        hist_avg = self.dao.get_average_scores_last_n_issues(self.hist_window)
        # 2. 使用更新器计算新权重 (这里简单使用历史平均分作为当前分进行平滑)
        new_weights = self.updater.update_weights(hist_avg, historical_avg=hist_avg)
        return new_weights


    def _get_historical_avg(self) -> Dict[str, float]:
        """
        获取最近 hist_window 期的算法平均分 {algorithm_version: avg_score}
        """
        performances = self.dao.get_algorithm_performance()
        algo_hist = {}
        for p in performances:
            algo_hist.setdefault(p.algorithm_version, []).append(p.current_weight or 0.0)

        hist_avg = {}
        for algo, scores in algo_hist.items():
            last_scores = scores[-self.hist_window:] if len(scores) >= self.hist_window else scores
            hist_avg[algo] = sum(last_scores) / len(last_scores) if last_scores else 0.0
        return hist_avg

    def evaluate_and_update(self, issue: str, model_outputs: Dict[str, Any], actual_draw: LotteryHistory) -> Dict[
        str, float]:
        """
        对本期算法输出进行评估并写入数据库，同时更新自适应权重。
        返回结构：
            {
                "FrequencyAnalysisAlgorithm": 0.73,
                "HotColdNumberAlgorithm": 0.62,
                ...
            }
        方便上层 run_backtest_simulation 进行统计与动态加权。
        """

        algo_scores = {}  # 存储算法得分详情，如 {'algo_name': {'hit_rate': 0.6, 'score': 0.7}}
        new_weights = {}  # 存储更新后的权重
        simple_accuracy_dict = {}  # 最终返回的简化结构 {algo_name: float_score}

        for algo_name, prediction in (model_outputs or {}).items():
            try:
                # === 1️⃣ 计算本期算法的评分指标 ===
                metrics = self._score_from_predictions(prediction, actual_draw)
                algo_scores[algo_name] = metrics

                # === 2️⃣ 写入数据库 AlgorithmPerformance ===
                performance = AlgorithmPerformance(
                    algorithm_version=algo_name,
                    total_recommendations=1,
                    total_periods_analyzed=1,
                    avg_front_hit_rate=metrics.get('hit_rate', 0.0),
                    avg_back_hit_rate=metrics.get('hit_rate', 0.0),
                    hit_distribution=None,
                    confidence_accuracy=metrics.get('score', 0.0),
                    risk_adjusted_return=0.0,
                    stability_score=0.0,
                    consistency_rate=0.0,
                    current_weight=metrics.get('score', 0.0),
                    weight_history=[{
                        'issue': issue,
                        'score': metrics.get('score', 0.0),
                        'timestamp': str(datetime.now())
                    }],
                    performance_trend=""
                )

                self.dao.update_algorithm_performance(performance)

                # === 3️⃣ 同时记录简化准确率结果供外层使用 ===
                simple_accuracy_dict[algo_name] = round(metrics.get('hit_rate', 0.0), 4)

            except Exception as e:
                print(f"[PerformanceLogger] ⚠️ Error evaluating {algo_name}: {e}")
                continue

        # === 4️⃣ 获取历史平均权重（跨期平滑）===
        try:
            hist_avg = self._get_historical_avg()  # {algo_name: avg_score}
        except Exception as e:
            print(f"[PerformanceLogger] ⚠️ Failed to get historical average: {e}")
            hist_avg = {}

        # === 5️⃣ 当前分数更新权重 ===
        current_scores = {k: v.get('score', 0.0) for k, v in algo_scores.items()}
        try:
            new_weights = self.updater.update_weights(current_scores, historical_avg=hist_avg)
        except Exception as e:
            print(f"[PerformanceLogger] ⚠️ Weight updater error: {e}")
            new_weights = current_scores

        # === 6️⃣ 写回数据库最新权重 ===
        for algo, weight in new_weights.items():
            try:
                perf_list = self.dao.get_algorithm_performance(algo)
                if perf_list:
                    perf = perf_list[-1]
                    perf.current_weight = float(weight)
                    perf.weight_history.append({
                        'issue': issue,
                        'score': float(weight),
                        'timestamp': str(datetime.now())
                    })
                    self.dao.update_algorithm_performance(perf)
            except Exception as e:
                print(f"[PerformanceLogger] ⚠️ Failed to update weight for {algo}: {e}")

        # === ✅ 7️⃣ 返回“简化准确率结果”，供 run_backtest_simulation 使用 ===
        return simple_accuracy_dict


# 调试
if __name__ == "__main__":
    from src.model.lottery_models import LotteryHistory
    logger = PerformanceLogger(smoothing_alpha=0.6, hist_window=3)

    # 模拟开奖结果和模型输出
    actual_draw = LotteryHistory(front_area=[1,2,3,4,5], back_area=[1,2])
    model_outputs = {
        "algo1": {"recommendations":[{"front_numbers":[1,2,3,6,7], "back_numbers":[1,3], "confidence":0.8}]},
        "algo2": {"front_probs": {1:0.3,2:0.2,3:0.1,4:0.4,5:0.5}, "back_probs": {1:0.6,2:0.4}}
    }

    new_weights = logger.evaluate_and_update("20251028", model_outputs, actual_draw)
    print("[TEST] New Weights:", new_weights)
