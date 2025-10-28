from typing import Dict
from math import isfinite


class AdaptiveWeightUpdater:
    """
    自适应权重更新器 (纯逻辑版本)
    - 它只负责数学计算，不接触数据库。
    """

    def __init__(self, alpha: float = 0.6):
        """
        :param alpha: 新得分的权重（0..1）。alpha越大越依赖当前得分；越小越平滑。
        """
        self.alpha = alpha

    def update_weights(self, current_scores: Dict[str, float], historical_avg: Dict[str, float] = None) -> Dict[
        str, float]:
        if not current_scores:
            return {}

        algos = set(current_scores.keys())
        if historical_avg:
            algos.update(historical_avg.keys())

        # 规范化当前得分
        cur_sum = sum(v for v in current_scores.values() if isfinite(v) and v >= 0) or 1.0
        cur_norm = {k: max(0.0, current_scores.get(k, 0.0)) / cur_sum for k in algos}

        # 规范化历史平均分
        hist_norm = {}
        if historical_avg:
            hist_sum = sum(v for v in historical_avg.values() if isfinite(v) and v >= 0) or 1.0
            hist_norm = {k: max(0.0, historical_avg.get(k, 0.0)) / hist_sum for k in algos}
        else:
            hist_norm = {k: 1.0 / len(algos) for k in algos} if algos else {}

        # 计算融合得分
        fused = {}
        for k in algos:
            fused_score = self.alpha * cur_norm.get(k, 0.0) + (1 - self.alpha) * hist_norm.get(k, 0.0)
            fused[k] = fused_score if isfinite(fused_score) else 0.0

        # 最后归一化 weights
        total_fused_score = sum(fused.values()) or 1.0
        weights = {k: round(v / total_fused_score, 4) for k, v in fused.items()}

        return weights