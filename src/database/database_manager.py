# database/database_manager.py
import mysql.connector
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from src.model.lottery_models import (
    LotteryHistory, NumberStatistics, AlgorithmConfig,
    AlgorithmPerformance, AlgorithmRecommendation,
    PersonalBetting, RewardPenaltyRecord, ABTestConfig
)

class DatabaseManager:
    """数据库管理类"""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3309):
        self.connection_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'charset': 'utf8mb4'
        }
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.connection_config)
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False

    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询语句"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"查询执行失败: {e}")
            return []

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """执行更新语句"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"更新执行失败: {e}")
            self.connection.rollback()
            return False

    def _convert_to_lottery_history_list(self, results):
        """
        将数据库查询结果转换为彩票历史记录列表
        :param results: 数据库查询结果
        :return: 彩票历史记录列表
        """
        history_list = []
        for row in results:
            history = LotteryHistory(
                id=row['id'],
                period_number=row['period_number'],
                draw_date=row['draw_date'],
                draw_time=row['draw_time'],
                front_area=[row['front_area_1'], row['front_area_2'], row['front_area_3'],
                           row['front_area_4'], row['front_area_5']],
                back_area=[row['back_area_1'], row['back_area_2']],
                sum_value=row['sum_value'],
                span_value=row['span_value'],
                ac_value=row['ac_value'],
                odd_even_ratio=row['odd_even_ratio'],
                size_ratio=row['size_ratio'],
                prime_composite_ratio=row['prime_composite_ratio'],
                consecutive_numbers=json.loads(row['consecutive_numbers']) if row['consecutive_numbers'] else None,
                consecutive_count=row['consecutive_count'],
                tail_numbers=json.loads(row['tail_numbers']) if row['tail_numbers'] else None,
                data_source=row['data_source'],
                data_quality=row['data_quality']
            )
            history_list.append(history)
        return history_list

    def get_latest_lottery_history(self, limit: int = 50) -> List[LotteryHistory]:
        """获取最新的历史开奖数据（按日期倒序）"""
        query = """
        SELECT * FROM lottery_history 
        ORDER BY draw_date DESC 
        LIMIT %s
        """
        results = self.execute_query(query, (limit,))
        return self._convert_to_lottery_history_list(results)

    def get_user_bets(self, user_id: str = 'default', limit: int = 20) -> List[PersonalBetting]:
        """获取用户历史投注记录"""
        query = """
        SELECT * FROM personal_betting 
        WHERE user_id = %s
        ORDER BY bet_time DESC 
        LIMIT %s
        """
        results = self.execute_query(query, (user_id, limit))
        betting_list = []
        for row in results:
            betting = PersonalBetting(
                id=row['id'],
                user_id=row['user_id'],
                period_number=row['period_number'],
                bet_time=row['bet_time'],
                bet_type=row['bet_type'],
                front_numbers=json.loads(row['front_numbers']) if isinstance(row['front_numbers'], str) else row['front_numbers'],
                front_count=row['front_count'],
                back_numbers=json.loads(row['back_numbers']) if isinstance(row['back_numbers'], str) else row['back_numbers'],
                back_count=row['back_count'],
                bet_amount=float(row['bet_amount']),
                multiple=row['multiple'],
                is_winning=bool(row['is_winning']) if row['is_winning'] is not None else False,
                winning_level=row['winning_level'],
                winning_amount=float(row['winning_amount']) if row['winning_amount'] else 0.0,
                strategy_type=row['strategy_type'],
                confidence_level=row['confidence_level'],
                analysis_notes=row['analysis_notes']
            )
            betting_list.append(betting)
        return betting_list

    def insert_algorithm_recommendation(self, recommendation: AlgorithmRecommendation) -> bool:
        """插入算法推荐记录"""
        query = """
        INSERT INTO algorithm_recommendation (
            period_number, recommend_time, algorithm_version, recommendation_combinations,
            confidence_score, risk_level, recommend_type, algorithm_parameters, model_weights,
            analysis_basis, key_patterns
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            recommendation.period_number,
            recommendation.recommend_time,
            recommendation.algorithm_version,
            json.dumps(recommendation.recommendation_combinations),
            recommendation.confidence_score,
            recommendation.risk_level,
            recommendation.recommend_type,
            json.dumps(recommendation.algorithm_parameters) if recommendation.algorithm_parameters else None,
            json.dumps(recommendation.model_weights) if recommendation.model_weights else None,
            json.dumps(recommendation.analysis_basis) if recommendation.analysis_basis else None,
            json.dumps(recommendation.key_patterns) if recommendation.key_patterns else None
        )
        return self.execute_update(query, params)

    def get_next_period_number(self) -> str:
        """获取下一期期号"""
        query = """
        SELECT period_number FROM lottery_history 
        ORDER BY period_number DESC 
        LIMIT 1
        """
        result = self.execute_query(query)
        if result:
            latest_period = result[0]['period_number']
            # 确保期号格式正确
            if isinstance(latest_period, str) and latest_period.isdigit():
                next_period = int(latest_period) + 1
                return str(next_period)
            elif isinstance(latest_period, int):
                return str(latest_period + 1)
        return ""

    # 历史开奖数据操作
    def get_lottery_history(self, limit: int = 100, offset: int = 0) -> List[LotteryHistory]:
        """获取历史开奖数据"""
        query = """
        SELECT * FROM lottery_history 
        ORDER BY draw_date DESC 
        LIMIT %s OFFSET %s
        """
        results = self.execute_query(query, (limit, offset))
        return self._convert_to_lottery_history_list(results)

    def insert_lottery_history(self, history: LotteryHistory) -> bool:
        """插入历史开奖数据"""
        query = """
        INSERT INTO lottery_history (
            period_number, draw_date, draw_time, front_area_1, front_area_2, 
            front_area_3, front_area_4, front_area_5, back_area_1, back_area_2,
            sum_value, span_value, ac_value, odd_even_ratio, size_ratio,
            prime_composite_ratio, consecutive_numbers, consecutive_count,
            tail_numbers, data_source, data_quality
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        params = (
            history.period_number, history.draw_date, history.draw_time,
            history.front_area[0], history.front_area[1], history.front_area[2],
            history.front_area[3], history.front_area[4],
            history.back_area[0], history.back_area[1],
            history.sum_value, history.span_value, history.ac_value,
            history.odd_even_ratio, history.size_ratio,
            history.prime_composite_ratio,
            json.dumps(history.consecutive_numbers) if history.consecutive_numbers else None,
            history.consecutive_count,
            json.dumps(history.tail_numbers) if history.tail_numbers else None,
            history.data_source, history.data_quality
        )
        return self.execute_update(query, params)

    # 算法配置操作
    def get_algorithm_configs(self, is_active: bool = True) -> List[AlgorithmConfig]:
        """获取算法配置"""
        query = "SELECT * FROM algorithm_configs"
        if is_active:
            query += " WHERE is_active = 1"

        results = self.execute_query(query)
        config_list = []
        for row in results:
            config = AlgorithmConfig(
                id=row['id'],
                algorithm_name=row['algorithm_name'],
                algorithm_type=row['algorithm_type'],
                parameters=json.loads(row['parameters']),
                description=row['description'],
                version=row['version'],
                is_active=bool(row['is_active']),
                is_default=bool(row['is_default']),
                min_data_required=row['min_data_required'],
                expected_accuracy=float(row['expected_accuracy']) if row['expected_accuracy'] else None,
                computation_complexity=row['computation_complexity'],
                memory_requirements=row['memory_requirements']
            )
            config_list.append(config)
        return config_list

    # 算法性能操作
    def get_algorithm_performance(self, algorithm_version: str = None) -> List[AlgorithmPerformance]:
        """获取算法性能数据"""
        query = "SELECT * FROM algorithm_performance"
        params = ()
        if algorithm_version:
            query += " WHERE algorithm_version = %s"
            params = (algorithm_version,)

        results = self.execute_query(query, params)
        performance_list = []
        for row in results:
            performance = AlgorithmPerformance(
                id=row['id'],
                algorithm_version=row['algorithm_version'],
                total_recommendations=row['total_recommendations'],
                total_periods_analyzed=row['total_periods_analyzed'],
                avg_front_hit_rate=float(row['avg_front_hit_rate']),
                avg_back_hit_rate=float(row['avg_back_hit_rate']),
                hit_distribution=json.loads(row['hit_distribution']) if row['hit_distribution'] else None,
                confidence_accuracy=float(row['confidence_accuracy']),
                risk_adjusted_return=float(row['risk_adjusted_return']),
                stability_score=float(row['stability_score']),
                consistency_rate=float(row['consistency_rate']),
                current_weight=float(row['current_weight']),
                weight_history=json.loads(row['weight_history']) if row['weight_history'] else None,
                performance_trend=row['performance_trend']
            )
            performance_list.append(performance)
        return performance_list

    def update_algorithm_performance(self, performance: AlgorithmPerformance) -> bool:
        """更新算法性能数据"""
        query = """
        INSERT INTO algorithm_performance (
            algorithm_version, total_recommendations, total_periods_analyzed,
            avg_front_hit_rate, avg_back_hit_rate, hit_distribution,
            confidence_accuracy, risk_adjusted_return, stability_score,
            consistency_rate, current_weight, weight_history, performance_trend
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_recommendations = VALUES(total_recommendations),
            total_periods_analyzed = VALUES(total_periods_analyzed),
            avg_front_hit_rate = VALUES(avg_front_hit_rate),
            avg_back_hit_rate = VALUES(avg_back_hit_rate),
            hit_distribution = VALUES(hit_distribution),
            confidence_accuracy = VALUES(confidence_accuracy),
            risk_adjusted_return = VALUES(risk_adjusted_return),
            stability_score = VALUES(stability_score),
            consistency_rate = VALUES(consistency_rate),
            current_weight = VALUES(current_weight),
            weight_history = VALUES(weight_history),
            performance_trend = VALUES(performance_trend)
        """
        params = (
            performance.algorithm_version,
            performance.total_recommendations,
            performance.total_periods_analyzed,
            performance.avg_front_hit_rate,
            performance.avg_back_hit_rate,
            json.dumps(performance.hit_distribution) if performance.hit_distribution else None,
            performance.confidence_accuracy,
            performance.risk_adjusted_return,
            performance.stability_score,
            performance.consistency_rate,
            performance.current_weight,
            json.dumps(performance.weight_history) if performance.weight_history else None,
            performance.performance_trend
        )
        return self.execute_update(query, params)

    # 号码统计操作
    def get_number_statistics(self, number: int = None, number_type: str = None) -> List[NumberStatistics]:
        """获取号码统计数据"""
        query = "SELECT * FROM number_statistics"
        conditions = []
        params = []

        if number is not None:
            conditions.append("number = %s")
            params.append(number)

        if number_type:
            conditions.append("number_type = %s")
            params.append(number_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        results = self.execute_query(query, tuple(params))
        stats_list = []
        for row in results:
            stats = NumberStatistics(
                number=row['number'],
                number_type=row['number_type'],
                total_appearances=row['total_appearances'],
                appearance_rate=float(row['appearance_rate']),
                recent_10_appearances=row['recent_10_appearances'],
                recent_20_appearances=row['recent_20_appearances'],
                recent_50_appearances=row['recent_50_appearances'],
                current_omission=row['current_omission'],
                max_omission=row['max_omission'],
                avg_omission=float(row['avg_omission']),
                heat_status=row['heat_status'],
                heat_score=float(row['heat_score']),
                strong_followers=json.loads(row['strong_followers']) if row['strong_followers'] else None,
                strong_precursors=json.loads(row['strong_precursors']) if row['strong_precursors'] else None,
                position_preference=json.loads(row['position_preference']) if row['position_preference'] else None
            )
            stats_list.append(stats)
        return stats_list

    def update_number_statistics(self, stats: NumberStatistics) -> bool:
        """更新号码统计数据"""
        query = """
        INSERT INTO number_statistics (
            number, number_type, total_appearances, appearance_rate,
            recent_10_appearances, recent_20_appearances, recent_50_appearances,
            current_omission, max_omission, avg_omission, heat_status,
            heat_score, strong_followers, strong_precursors, position_preference
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_appearances = VALUES(total_appearances),
            appearance_rate = VALUES(appearance_rate),
            recent_10_appearances = VALUES(recent_10_appearances),
            recent_20_appearances = VALUES(recent_20_appearances),
            recent_50_appearances = VALUES(recent_50_appearances),
            current_omission = VALUES(current_omission),
            max_omission = VALUES(max_omission),
            avg_omission = VALUES(avg_omission),
            heat_status = VALUES(heat_status),
            heat_score = VALUES(heat_score),
            strong_followers = VALUES(strong_followers),
            strong_precursors = VALUES(strong_precursors),
            position_preference = VALUES(position_preference)
        """
        params = (
            stats.number, stats.number_type, stats.total_appearances, stats.appearance_rate,
            stats.recent_10_appearances, stats.recent_20_appearances, stats.recent_50_appearances,
            stats.current_omission, stats.max_omission, stats.avg_omission, stats.heat_status,
            stats.heat_score,
            json.dumps(stats.strong_followers) if stats.strong_followers else None,
            json.dumps(stats.strong_precursors) if stats.strong_precursors else None,
            json.dumps(stats.position_preference) if stats.position_preference else None
        )
        return self.execute_update(query, params)
