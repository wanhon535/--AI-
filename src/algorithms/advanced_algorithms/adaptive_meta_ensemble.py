# src/algorithms/advanced_algorithms/adaptive_meta_ensemble.py
from src.algorithms.base_algorithm import BaseAlgorithm
from typing import List, Dict, Any
import math
import numpy as np

class AdaptiveMetaEnsemble(BaseAlgorithm):
    """自适应加权集成器"""

    def __init__(self, models: List[BaseAlgorithm]):
        super().__init__("adaptive_meta_ensemble", "1.0")
        self.models = models
        self.weights = {m.name: 1.0 for m in models}

    def train(self, history_data) -> bool:
        for m in self.models:
            m.train(history_data)
        self.is_trained = True
        return True

    def predict(self, history_data) -> Dict[str, Any]:
        combined = {}
        for m in self.models:
            res = m.predict(history_data)
            for r in res.get('recommendations', []):
                key = tuple(r.get('front_numbers', []))
                combined[key] = combined.get(key, 0) + self.weights[m.name]

        sorted_combos = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:5]
        recs = [{'front_numbers': list(k), 'score': v} for k, v in sorted_combos]
        return {'algorithm': self.name, 'version': self.version, 'recommendations': recs}

