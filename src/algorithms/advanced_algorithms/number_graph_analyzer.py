# src/algorithms/advanced_algorithms/number_graph_analyzer.py
import numpy as np
import networkx as nx
from src.algorithms.base_algorithm import BaseAlgorithm
from src.model.lottery_models import LotteryHistory
from typing import List, Dict, Any, Tuple
import logging
from collections import defaultdict

from src.utils.log_predictor import log_prediction


class NumberGraphAnalyzer(BaseAlgorithm):
    """号码图分析器 - 基于图论分析号码关联关系"""
    name = "NumberGraphAnalyzer"
    version = "1.0"

    def __init__(self):
        super().__init__()
        self.front_graph = None
        self.back_graph = None
        self.centrality_measures = {}

    def train(self, history_data: List[LotteryHistory]) -> bool:
        """构建号码关系图"""
        if not history_data or len(history_data) < 20:
            logging.error("数据量不足，无法构建关系图")
            return False

        try:
            # 构建前区号码图
            self.front_graph = self._build_number_graph(history_data, 'front', 35)

            # 构建后区号码图
            self.back_graph = self._build_number_graph(history_data, 'back', 12)

            # 计算中心性指标
            self._calculate_centrality_measures()

            self.is_trained = True
            logging.info("号码关系图构建完成")
            return True

        except Exception as e:
            logging.error(f"号码图分析器训练失败: {e}")
            return False
    @log_prediction
    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """基于图分析进行预测"""
        if not self.is_trained:
            return {'error': '模型未训练'}

        try:
            # 基于图中心性生成预测
            front_recommendations = self._graph_based_prediction('front')
            back_recommendations = self._graph_based_prediction('back')

            # 计算置信度
            confidence = self._calculate_graph_confidence()

            return {
                'algorithm': self.name,
                'version': self.version,
                'recommendations': [{
                    'front_number_scores': front_recommendations,
                    'back_number_scores': back_recommendations,
                    'confidence': confidence,
                    'graph_characteristics': self._get_graph_characteristics()
                }],
                'analysis': {
                    'graph_analysis': self._get_graph_analysis(),
                    'centrality_measures': self.centrality_measures,
                    'strong_connections': self._get_strong_connections()
                }
            }

        except Exception as e:
            logging.error(f"图分析预测失败: {e}")
            return {'error': str(e)}

    def _build_number_graph(self, history_data: List[LotteryHistory], area_type: str, num_count: int) -> nx.Graph:
        """构建号码关系图"""
        graph = nx.Graph()

        # 添加所有节点
        for i in range(1, num_count + 1):
            graph.add_node(i)

        # 构建共现关系
        cooccurrence_counts = defaultdict(int)

        for record in history_data:
            numbers = record.front_area if area_type == 'front' else record.back_area

            # 记录每对号码的共现次数
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    num1, num2 = numbers[i], numbers[j]
                    if 1 <= num1 <= num_count and 1 <= num2 <= num_count:
                        pair = tuple(sorted([num1, num2]))
                        cooccurrence_counts[pair] += 1

        # 添加边（权重为共现次数）
        for (num1, num2), count in cooccurrence_counts.items():
            if count > 0:
                graph.add_edge(num1, num2, weight=count)

        logging.info(f"构建了{area_type}区号码图: {graph.number_of_nodes()}节点, {graph.number_of_edges()}边")
        return graph

    def _calculate_centrality_measures(self):
        """计算各种中心性指标"""
        self.centrality_measures = {
            'front': {},
            'back': {}
        }

        if self.front_graph:
            # 度数中心性
            self.centrality_measures['front']['degree'] = nx.degree_centrality(self.front_graph)

            # 介数中心性
            self.centrality_measures['front']['betweenness'] = nx.betweenness_centrality(self.front_graph,
                                                                                         weight='weight')

            # 接近中心性
            self.centrality_measures['front']['closeness'] = nx.closeness_centrality(self.front_graph)

            # 特征向量中心性
            try:
                self.centrality_measures['front']['eigenvector'] = nx.eigenvector_centrality(self.front_graph,
                                                                                             weight='weight',
                                                                                             max_iter=1000)
            except:
                self.centrality_measures['front']['eigenvector'] = {}

        if self.back_graph:
            self.centrality_measures['back']['degree'] = nx.degree_centrality(self.back_graph)
            self.centrality_measures['back']['betweenness'] = nx.betweenness_centrality(self.back_graph,
                                                                                        weight='weight')
            self.centrality_measures['back']['closeness'] = nx.closeness_centrality(self.back_graph)
            try:
                self.centrality_measures['back']['eigenvector'] = nx.eigenvector_centrality(self.back_graph,
                                                                                            weight='weight',
                                                                                            max_iter=1000)
            except:
                self.centrality_measures['back']['eigenvector'] = {}

    def _graph_based_prediction(self, area_type: str) -> List[Dict[str, Any]]:
        """基于图中心性生成预测"""
        graph = self.front_graph if area_type == 'front' else self.back_graph
        centrality = self.centrality_measures[area_type]

        if not graph or not centrality:
            return []

        recommendations = []
        numbers_range = range(1, 36) if area_type == 'front' else range(1, 13)

        for number in numbers_range:
            if number in graph.nodes():
                # 综合中心性评分
                score = self._calculate_composite_centrality(number, centrality)

                recommendations.append({
                    'number': number,
                    'score': round(score, 4),
                    'centrality_breakdown': {
                        'degree': round(centrality['degree'].get(number, 0), 4),
                        'betweenness': round(centrality['betweenness'].get(number, 0), 4),
                        'closeness': round(centrality['closeness'].get(number, 0), 4),
                        'eigenvector': round(centrality['eigenvector'].get(number, 0), 4)
                    },
                    'neighbors': list(graph.neighbors(number))[:5]  # 显示前5个邻居
                })
            else:
                # 孤立节点，给基础分
                recommendations.append({
                    'number': number,
                    'score': 0.1,
                    'centrality_breakdown': {'degree': 0, 'betweenness': 0, 'closeness': 0, 'eigenvector': 0},
                    'neighbors': []
                })

        # 按综合评分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations

    def _calculate_composite_centrality(self, number: int, centrality: Dict[str, Any]) -> float:
        """计算综合中心性评分"""
        weights = {
            'degree': 0.4,  # 度数中心性最重要
            'betweenness': 0.3,  # 介数中心性次重要
            'closeness': 0.2,  # 接近中心性
            'eigenvector': 0.1  # 特征向量中心性
        }

        composite_score = 0.0
        for measure, weight in weights.items():
            score = centrality[measure].get(number, 0)
            composite_score += score * weight

        return composite_score

    def _calculate_graph_confidence(self) -> float:
        """计算图分析置信度"""
        confidence = 0.7  # 基础置信度

        if self.front_graph and self.back_graph:
            # 基于图密度调整置信度
            front_density = nx.density(self.front_graph)
            back_density = nx.density(self.back_graph)

            # 适中的图密度通常表示更好的关系结构
            if 0.1 <= front_density <= 0.3 and 0.2 <= back_density <= 0.5:
                confidence += 0.2
            elif front_density > 0 and back_density > 0:
                confidence += 0.1

        return min(confidence, 0.9)

    def _get_graph_characteristics(self) -> Dict[str, Any]:
        """获取图特征"""
        characteristics = {}

        if self.front_graph:
            characteristics['front'] = {
                'nodes': self.front_graph.number_of_nodes(),
                'edges': self.front_graph.number_of_edges(),
                'density': round(nx.density(self.front_graph), 4),
                'average_degree': round(np.mean([d for n, d in self.front_graph.degree()]), 2)
            }

        if self.back_graph:
            characteristics['back'] = {
                'nodes': self.back_graph.number_of_nodes(),
                'edges': self.back_graph.number_of_edges(),
                'density': round(nx.density(self.back_graph), 4),
                'average_degree': round(np.mean([d for n, d in self.back_graph.degree()]), 2)
            }

        return characteristics

    def _get_graph_analysis(self) -> Dict[str, Any]:
        """获取图分析信息"""
        analysis = {}

        if self.front_graph:
            analysis['front'] = {
                'node_count': self.front_graph.number_of_nodes(),
                'edge_count': self.front_graph.number_of_edges(),
                'graph_density': round(nx.density(self.front_graph), 4),
                'connected_components': nx.number_connected_components(self.front_graph)
            }

        if self.back_graph:
            analysis['back'] = {
                'node_count': self.back_graph.number_of_nodes(),
                'edge_count': self.back_graph.number_of_edges(),
                'graph_density': round(nx.density(self.back_graph), 4),
                'connected_components': nx.number_connected_components(self.back_graph)
            }

        return analysis

    def _get_strong_connections(self) -> Dict[str, List[Tuple]]:
        """获取最强关联号码对"""
        strong_connections = {'front': [], 'back': []}

        if self.front_graph:
            front_edges = sorted(self.front_graph.edges(data=True),
                                 key=lambda x: x[2].get('weight', 0), reverse=True)
            strong_connections['front'] = [(u, v, data['weight']) for u, v, data in front_edges[:10]]

        if self.back_graph:
            back_edges = sorted(self.back_graph.edges(data=True),
                                key=lambda x: x[2].get('weight', 0), reverse=True)
            strong_connections['back'] = [(u, v, data['weight']) for u, v, data in back_edges[:5]]

        return strong_connections