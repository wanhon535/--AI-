# algorithm_recommendation_service.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG
from datetime import datetime
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [AlgorithmService] %(message)s',
    handlers=[
        logging.FileHandler('algorithm_service.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class AlgorithmRecommendationService:
    """独立的算法推荐服务 - 专门处理算法推荐逻辑"""

    def __init__(self):
        self.db_manager = DatabaseManager(**DB_CONFIG)
        self.algorithms = {
            'bayesian': BayesianNumberPredictor(),
            # 未来可以添加更多算法
            # 'neural_network': NeuralLotteryPredictor(),
            # 'markov': MarkovTransitionModel(),
        }
        logging.info("算法推荐服务初始化完成")

    def generate_recommendations(self, target_period: str, algorithm_names: list = None, history_limit: int = 100):
        """
        为目标期号生成算法推荐

        Args:
            target_period: 目标期号
            algorithm_names: 使用的算法列表，None表示使用所有算法
            history_limit: 使用的历史数据数量

        Returns:
            推荐结果字典
        """
        logging.info(f"开始为 {target_period} 期生成推荐")

        if algorithm_names is None:
            algorithm_names = list(self.algorithms.keys())

        results = {}

        for algo_name in algorithm_names:
            if algo_name not in self.algorithms:
                logging.warning(f"算法 {algo_name} 不存在，跳过")
                continue

            try:
                logging.info(f"运行 {algo_name} 算法...")
                algorithm_result = self._run_single_algorithm(
                    algo_name, target_period, history_limit
                )

                if algorithm_result:
                    results[algo_name] = algorithm_result
                    logging.info(f"{algo_name} 算法推荐生成成功")
                else:
                    logging.error(f"{algo_name} 算法推荐生成失败")

            except Exception as e:
                logging.error(f"{algo_name} 算法执行异常: {str(e)}")
                import traceback
                traceback.print_exc()

        # 汇总结果
        summary = {
            'target_period': target_period,
            'generated_at': datetime.now(),
            'algorithms_used': list(results.keys()),
            'results': results
        }

        logging.info(f"推荐生成完成，共 {len(results)} 个算法成功")
        return summary

    def _run_single_algorithm(self, algorithm_name: str, target_period: str, history_limit: int):
        """运行单个算法并返回结果"""
        algorithm = self.algorithms[algorithm_name]

        # 获取历史数据
        history_data = self.db_manager.get_all_lottery_history(limit=history_limit)
        if not history_data:
            raise Exception("没有获取到历史数据")

        # 训练模型
        if not algorithm.train(history_data):
            raise Exception("模型训练失败")

        # 生成预测
        raw_result = algorithm.predict(history_data)

        # 处理结果格式
        processed_result = self._process_algorithm_result(raw_result, algorithm_name)

        # 存储到数据库
        recommendation_id = self._store_algorithm_recommendation(
            processed_result, target_period, algorithm_name
        )

        processed_result['recommendation_id'] = recommendation_id
        return processed_result

    def _process_algorithm_result(self, raw_result: dict, algorithm_name: str):
        """处理算法原始结果，统一格式"""
        if algorithm_name == 'bayesian':
            return self._process_bayesian_result(raw_result)
        # 其他算法的处理逻辑可以在这里添加
        else:
            return raw_result

    def _process_bayesian_result(self, raw_result: dict):
        """处理贝叶斯算法结果"""
        recommendations = raw_result['recommendations'][0]
        front_scores = recommendations['front_number_scores']
        back_scores = recommendations['back_number_scores']

        # 生成推荐组合
        combinations = self._generate_recommendation_combinations(front_scores, back_scores)

        processed = {
            'algorithm': raw_result['algorithm'],
            'version': raw_result['version'],
            'confidence': recommendations['confidence'],
            'all_scores': {
                'front': front_scores,
                'back': back_scores
            },
            'recommendation_combinations': combinations,
            'analysis': raw_result.get('analysis', {})
        }

        return processed

    def _generate_recommendation_combinations(self, front_scores: list, back_scores: list):
        """基于评分生成多种推荐组合"""
        combinations = []

        # 组合1: 标准推荐 (5+2)
        front_standard = [item['number'] for item in front_scores[:5]]
        back_standard = [item['number'] for item in back_scores[:2]]
        prob_standard = self._calculate_combination_probability(front_scores[:5], back_scores[:2])

        combinations.append({
            'type': '标准推荐',
            'description': '前区评分最高的5个号码 + 后区评分最高的2个号码',
            'front_numbers': front_standard,
            'back_numbers': back_standard,
            'probability': prob_standard,
            'bet_type': 'single'
        })

        # 组合2: 复式推荐 (7+3)
        front_composite = [item['number'] for item in front_scores[:7]]
        back_composite = [item['number'] for item in back_scores[:3]]
        prob_composite = self._calculate_combination_probability(front_scores[:7], back_scores[:3])

        combinations.append({
            'type': '复式推荐',
            'description': '前区评分最高的7个号码 + 后区评分最高的3个号码',
            'front_numbers': front_composite,
            'back_numbers': back_composite,
            'probability': prob_composite,
            'bet_type': 'composite'
        })

        # 组合3: 热号精选 (评分>0.8)
        front_hot = [item['number'] for item in front_scores if item['score'] > 0.8][:6]
        back_hot = [item['number'] for item in back_scores if item['score'] > 0.8][:2]

        if len(front_hot) >= 5 and len(back_hot) >= 2:
            front_hot_scores = [item for item in front_scores if item['number'] in front_hot]
            back_hot_scores = [item for item in back_scores if item['number'] in back_hot]
            prob_hot = self._calculate_combination_probability(front_hot_scores, back_hot_scores)

            combinations.append({
                'type': '热号精选',
                'description': '选择评分高于0.8的热门号码',
                'front_numbers': front_hot[:5],  # 取前5个
                'back_numbers': back_hot[:2],  # 取前2个
                'probability': prob_hot,
                'bet_type': 'single'
            })

        return combinations

    def _calculate_combination_probability(self, front_items: list, back_items: list):
        """计算组合的概率评分"""
        if not front_items or not back_items:
            return 0.0

        front_avg = sum(item['score'] for item in front_items) / len(front_items)
        back_avg = sum(item['score'] for item in back_items) / len(back_items)

        return round(front_avg * back_avg, 4)

    def _store_algorithm_recommendation(self, result: dict, target_period: str, algorithm_name: str):
        """存储算法推荐到数据库"""
        try:
            # 存储到 algorithm_recommendation 表
            recommendation_data = {
                'period_number': target_period,
                'recommend_time': datetime.now(),
                'algorithm_version': f"{result['algorithm']}_{result['version']}",
                'confidence_score': result['confidence'],
                'risk_level': 'medium',
                'analysis_basis': json.dumps({
                    'algorithm': algorithm_name,
                    'description': '独立算法推荐服务生成',
                    'combinations_count': len(result['recommendation_combinations'])
                }, ensure_ascii=False),
                'key_patterns': json.dumps(result.get('analysis', {}), ensure_ascii=False),
                'models': algorithm_name
            }

            recommendation_id = self.db_manager.execute_insert(
                'algorithm_recommendation',
                recommendation_data
            )

            if not recommendation_id:
                recommendation_id = self.db_manager.get_last_insert_id()

            if recommendation_id:
                # 存储推荐详情
                self._store_recommendation_details(recommendation_id, result['recommendation_combinations'])
                logging.info(f"推荐存储成功，ID: {recommendation_id}")
            else:
                logging.error("推荐存储失败，无法获取推荐ID")

            return recommendation_id

        except Exception as e:
            logging.error(f"存储推荐失败: {str(e)}")
            return None

    def _store_recommendation_details(self, recommendation_id: int, combinations: list):
        """存储推荐详情"""
        try:
            for combo in combinations:
                detail_data = {
                    'recommendation_metadata_id': recommendation_id,
                    'recommend_type': combo['type'],
                    'strategy_logic': combo['description'],
                    'front_numbers': ','.join(map(str, combo['front_numbers'])),
                    'back_numbers': ','.join(map(str, combo['back_numbers'])),
                    'win_probability': combo['probability']
                }
                self.db_manager.execute_insert('recommendation_details', detail_data)

            logging.info(f"存储了 {len(combinations)} 个推荐组合")

        except Exception as e:
            logging.error(f"存储推荐详情失败: {str(e)}")

    def get_latest_recommendations(self, algorithm_name: str = None, limit: int = 5):
        """获取最新的推荐结果"""
        try:
            if algorithm_name:
                query = """
                SELECT * FROM algorithm_recommendation 
                WHERE models = %s 
                ORDER BY recommend_time DESC 
                LIMIT %s
                """
                params = (algorithm_name, limit)
            else:
                query = "SELECT * FROM algorithm_recommendation ORDER BY recommend_time DESC LIMIT %s"
                params = (limit,)

            recommendations = self.db_manager.execute_query(query, params)

            # 获取每个推荐的详情
            for rec in recommendations:
                details_query = """
                SELECT * FROM recommendation_details 
                WHERE recommendation_metadata_id = %s
                """
                rec['details'] = self.db_manager.execute_query(details_query, (rec['id'],))

            return recommendations

        except Exception as e:
            logging.error(f"获取推荐结果失败: {str(e)}")
            return []