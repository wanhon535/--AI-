# src/algorithms/advanced_algorithms/hit_rate_optimizer.py

from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any
import random
import numpy as np

class HitRateOptimizer(BaseAlgorithm):
    """
    命中率优化算法
    通过遗传搜索和历史回测，找到期望命中率最高的号码组合。
    """

    def __init__(self, sub_models: List[BaseAlgorithm]):
        super().__init__("hit_rate_optimizer", "1.0")
        self.sub_models = sub_models
        self.parameters = {
            'population_size': 30,
            'generations': 50,
            'mutation_rate': 0.15
        }
        self.best_combinations = []

    def _evaluate_hit_score(self, candidate, history_data):
        """计算组合在历史数据中的平均命中率"""
        hits = 0
        total = 0
        for rec in history_data[-30:]:  # 最近30期验证
            hit_count = len(set(candidate).intersection(set(rec.front_area)))
            hits += hit_count
            total += len(rec.front_area)
        return hits / (total or 1)

    def train(self, history_data: List[LotteryHistory]) -> bool:
        if not history_data:
            return False

        # 从子模型收集候选号码
        candidate_pool = set()
        for m in self.sub_models:
            m.train(history_data)
            res = m.predict(history_data)
            for r in res.get('recommendations', []):
                candidate_pool.update(r.get('front_numbers', []))

        candidate_pool = list(candidate_pool)
        if len(candidate_pool) < 10:
            candidate_pool = random.sample(range(1, 36), 15)

        # 初始化种群
        population = [random.sample(candidate_pool, 5) for _ in range(self.parameters['population_size'])]

        for g in range(self.parameters['generations']):
            fitness = [self._evaluate_hit_score(ind, history_data) for ind in population]
            selected = self._select(population, fitness)
            children = self._crossover(selected)
            population = self._mutate(children, candidate_pool)

        # 取前5组作为最佳推荐
        scored = [(p, self._evaluate_hit_score(p, history_data)) for p in population]
        scored.sort(key=lambda x: x[1], reverse=True)
        self.best_combinations = [s[0] for s in scored[:5]]
        self.is_trained = True
        return True

    def _select(self, population, fitness):
        probs = np.array(fitness) / (np.sum(fitness) + 1e-9)
        idx = np.random.choice(len(population), size=len(population)//2, p=probs)
        return [population[i] for i in idx]

    def _crossover(self, parents):
        children = []
        for i in range(0, len(parents)-1, 2):
            p1, p2 = parents[i], parents[i+1]
            cut = random.randint(1, 4)
            child = list(set(p1[:cut] + p2[cut:]))[:5]
            if len(child) < 5:
                child += random.sample(range(1, 36), 5 - len(child))
            children.append(child)
        return children

    def _mutate(self, population, pool):
        for p in population:
            if random.random() < self.parameters['mutation_rate']:
                idx = random.randint(0, len(p)-1)
                p[idx] = random.choice(pool)
        return population

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        if not self.is_trained:
            return {'error': '模型未训练'}

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [
                {'front_numbers': sorted(c), 'confidence': 0.8} for c in self.best_combinations
            ],
            'analysis': {'model_count': len(self.sub_models)}
        }

