# =================================================================================================
# --- FILE: src/algorithms/advanced_algorithms/number_graph_analyzer.py (COMPLETE REPLACEMENT V2.1 - Bug Fixed) ---
# =================================================================================================
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


class NumberGraphAnalyzer(BaseAlgorithm):
    """基于共现图的号码关系分析 (V2.1 - 修复版)"""
    name = "NumberGraphAnalyzer"
    version = "2.1"

    def __init__(self):
        super().__init__()
        if not NETWORKX_AVAILABLE:
            raise ImportError("此算法需要 `networkx` 库。请运行: pip install networkx")
        self.G = nx.Graph()

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """
        核心修复: 分别为前区和后区构建图，或者构建一个统一的图但只关注前区。
        这里我们选择只为前区构建一个更专注的图。
        """
        if not history_data:
            return False

        self.G.clear()
        # 只为前区号码添加节点
        front_numbers_range = range(1, 36)
        self.G.add_nodes_from(front_numbers_range)

        for rec in history_data:
            nums = rec.front_area
            # 在同一期出现的号码之间添加或加强边
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    if self.G.has_edge(nums[i], nums[j]):
                        self.G[nums[i]][nums[j]]['weight'] += 1
                    else:
                        self.G.add_edge(nums[i], nums[j], weight=1)
        self.is_trained = True
        return True

    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """核心修复: 确保即使图中没有边，也能返回一个有效的、空的推荐结构。"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        # 如果训练后图中没有边（例如历史数据太少或没有共现），则返回一个中性的评分
        if self.G.number_of_edges() == 0:
            print(f"  - ⚠️ 警告 [{self.name}]: 训练后图中没有边，将返回中性评分。")
            front_scores = [{'number': n, 'score': 0.5} for n in range(1, 36)]
            back_scores = [{'number': n, 'score': 0.5} for n in range(1, 13)]
        else:
            # 使用 PageRank 算法计算节点（号码）的重要性
            pagerank_scores = nx.pagerank(self.G, weight='weight')

            # 归一化 PageRank 得分
            max_pr = max(pagerank_scores.values()) if pagerank_scores else 1.0
            front_scores = [{'number': n, 'score': round(pagerank_scores.get(n, 0) / max_pr, 4)} for n in range(1, 36)]
            # (后区逻辑简化，因为我们的图只分析了前区)
            back_scores = [{'number': n, 'score': 0.5} for n in range(1, 13)]

        recommendation = {
            'front_number_scores': sorted(front_scores, key=lambda x: x['score'], reverse=True),
            'back_number_scores': sorted(back_scores, key=lambda x: x['score'], reverse=True),
            'confidence': 0.75
        }

        return {
            'algorithm': self.name,
            'version': self.version,
            'recommendations': [recommendation],
            'analysis': {'pagerank_top': front_scores[:5]}
        }