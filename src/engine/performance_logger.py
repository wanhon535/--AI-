# file: src/engine/performance_logger.py
from typing import Dict, Any
from datetime import datetime
from src.model.lottery_models import LotteryHistory, AlgorithmPerformance
from src.database.crud.algorithm_performance_dao import AlgorithmPerformanceDAO
from .adaptive_weight_updater import AdaptiveWeightUpdater
from src.database.database_manager import DatabaseManager

class PerformanceLogger:
    def __init__(self, db_manager: DatabaseManager = None, dao=None, smoothing_alpha: float = 0.6,
                 hist_window: int = 3):
        """
        :param db_manager: 传入一个已经配置好的 DatabaseManager 实例。
        :param dao: 可选。传入一个DAO实例，用于测试。如果为None，则自己创建真实的DAO。
        :param smoothing_alpha: 平滑系数。
        :param hist_window: 历史窗口大小。
        """
        if dao:
            # 在测试环境中，使用传入的假 dao
            self.dao = dao
            print("[PerformanceLogger] Initialized in TEST mode with a mock DAO.")
        elif db_manager:
            # 在真实环境中 (如 main.py)，使用传入的 db_manager 创建真 dao
            self.dao = AlgorithmPerformanceDAO(db_manager)
            print("[PerformanceLogger] Initialized in PRODUCTION mode with a real DAO.")
        else:
            # 如果两者都未提供，则抛出错误，避免隐患
            raise ValueError("PerformanceLogger requires either a 'db_manager' or a 'dao' instance.")

        self.updater = AdaptiveWeightUpdater(alpha=smoothing_alpha)
        self.hist_window = hist_window

    def _score_from_predictions(self, prediction: Dict[str, Any], actual_draw: LotteryHistory) -> Dict[str, float]:
        """
        计算命中、命中率和分数
        支持两类 prediction:
          1) recommendation list: {'recommendations':[{'front_numbers':[...],'back_numbers':[...],'confidence':0.8},...] }
          2) probability map: {'front_probs': {num:prob,...}, 'back_probs': {...}}
        """
        front_actual = set(actual_draw.front_area)
        back_actual = set(actual_draw.back_area)
        total_numbers = len(front_actual) + len(back_actual)

        # Case 1: explicit combinations
        if isinstance(prediction, dict) and 'recommendations' in prediction and prediction['recommendations']:
            recs = prediction['recommendations']
            hit_counts = []
            rates = []
            for r in recs:
                fnums = set(r.get('front_numbers', []))
                bnums = set(r.get('back_numbers', []))
                hits = len(fnums & front_actual) + len(bnums & back_actual)
                hit_counts.append(hits)
                rates.append(hits / total_numbers if total_numbers else 0.0)
            avg_hits = sum(hit_counts) / len(hit_counts)
            avg_rate = sum(rates) / len(rates)
            score = round(avg_rate * (1 + avg_hits / 10), 6)
            return {'hits': avg_hits, 'hit_rate': avg_rate, 'score': score}

        # Case 2: per-number probability
        if isinstance(prediction, dict) and ('front_probs' in prediction or 'back_probs' in prediction):
            front_probs = prediction.get('front_probs', {})
            back_probs = prediction.get('back_probs', {})
            expected_hits = 0.0
            for n in front_actual:
                expected_hits += float(front_probs.get(int(n), 0.0) or front_probs.get(str(n), 0.0) or 0.0)
            for n in back_actual:
                expected_hits += float(back_probs.get(int(n), 0.0) or back_probs.get(str(n), 0.0) or 0.0)
            avg_hits = expected_hits
            avg_rate = expected_hits / total_numbers if total_numbers else 0.0
            score = round(avg_rate * (1 + avg_hits / 10), 6)
            return {'hits': avg_hits, 'hit_rate': avg_rate, 'score': score}

        return {'hits': 0.0, 'hit_rate': 0.0, 'score': 0.0}

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

    def evaluate_and_update(self, issue: str, model_outputs: Dict[str, Any], actual_draw: LotteryHistory) -> Dict[str, float]:
        """
        对本期算法输出进行评估并写入数据库，同时更新自适应权重
        :return: new_weights {algorithm_version: weight}
        """
        algo_scores = {}

        for algo_name, prediction in (model_outputs or {}).items():
            try:
                metrics = self._score_from_predictions(prediction, actual_draw)
                algo_scores[algo_name] = metrics

                # 构建 AlgorithmPerformance 对象写入数据库
                performance = AlgorithmPerformance(
                    algorithm_version=algo_name,
                    total_recommendations=1,
                    total_periods_analyzed=1,
                    avg_front_hit_rate=metrics['hit_rate'],
                    avg_back_hit_rate=metrics['hit_rate'],
                    hit_distribution=None,
                    confidence_accuracy=metrics['score'],
                    risk_adjusted_return=0.0,
                    stability_score=0.0,
                    consistency_rate=0.0,
                    current_weight=metrics['score'],
                    weight_history=[{'issue': issue, 'score': metrics['score'], 'timestamp': str(datetime.now())}],
                    performance_trend=""
                )
                self.dao.update_algorithm_performance(performance)
            except Exception as e:
                print(f"[PerformanceLogger] Error evaluating {algo_name}: {e}")
                continue

        # 获取历史平均权重
        hist_avg = self._get_historical_avg()  # {algo: avg_score}

        # 当前分数用于更新权重
        current_scores = {k: v.get('score', 0.0) for k, v in algo_scores.items()}
        new_weights = self.updater.update_weights(current_scores, historical_avg=hist_avg)

        # 写回数据库 current_weight
        for algo, weight in new_weights.items():
            perf_list = self.dao.get_algorithm_performance(algo)
            if perf_list:
                perf = perf_list[-1]
                perf.current_weight = weight
                perf.weight_history.append({'issue': issue, 'score': weight, 'timestamp': str(datetime.now())})
                self.dao.update_algorithm_performance(perf)

        return new_weights

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
