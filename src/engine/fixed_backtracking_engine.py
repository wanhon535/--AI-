# src/engine/fixed_backtracking_engine.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import re
from decimal import Decimal


class FixedBacktrackingEngine:
    """修复版回溯引擎 - 解决所有已知问题"""

    def __init__(self, db_config=None):
        if db_config is None:
            try:
                from src.config.database_config import DB_CONFIG
                self.db_config = DB_CONFIG
            except ImportError:
                # 默认配置
                self.db_config = {
                    'host': 'localhost',
                    'user': 'root',
                    'password': '',
                    'database': 'lottery_analysis',
                    'port': 3306
                }
        else:
            self.db_config = db_config

    def _get_connection(self):
        """获取数据库连接"""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"数据库连接失败: {e}")
            return None

    def _execute_query(self, query, params=None):
        """执行查询"""
        connection = self._get_connection()
        if connection is None:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"查询执行失败: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                connection.close()

    def _execute_update(self, query, params=None):
        """执行更新"""
        connection = self._get_connection()
        if connection is None:
            return 0

        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"更新执行失败: {e}")
            if connection:
                connection.rollback()
            return 0
        finally:
            if connection and connection.is_connected():
                connection.close()

    def _clean_numbers_string(self, numbers_str: str) -> List[int]:
        """清理号码字符串，提取纯数字"""
        if not numbers_str:
            return []

        # 移除所有非数字字符（除了逗号）
        cleaned = re.sub(r'[^\d,]', '', numbers_str)

        # 分割并转换为整数
        numbers = []
        for num_str in cleaned.split(','):
            if num_str.strip() and num_str.strip().isdigit():
                try:
                    num = int(num_str.strip())
                    if 1 <= num <= 35:  # 大乐透号码范围
                        numbers.append(num)
                except ValueError:
                    continue

        return numbers

    def run_algorithm_backtracking(self, period_count: int = 50) -> Dict[str, Any]:
        """
        运行算法回溯分析
        Args:
            period_count: 回溯期数
        Returns:
            回溯分析结果
        """
        print(f"🚀 开始算法回溯分析，回溯期数: {period_count}")

        try:
            # 获取历史开奖数据
            history_query = """
            SELECT period_number, front_area_1, front_area_2, front_area_3, 
                   front_area_4, front_area_5, back_area_1, back_area_2
            FROM lottery_history 
            ORDER BY draw_date DESC 
            LIMIT %s
            """
            history_data = self._execute_query(history_query, (period_count,))

            if not history_data:
                return {"status": "error", "message": "没有找到历史开奖数据"}

            print(f"📊 获取到 {len(history_data)} 期历史数据")

            backtrack_results = []
            analyzed_periods = 0

            for period_data in history_data:
                period_number = period_data['period_number']
                actual_numbers = self._extract_actual_numbers(period_data)

                # 获取该期号的算法推荐
                recommendation_query = """
                SELECT ar.id, ar.algorithm_version, ar.period_number,
                       rd.front_numbers, rd.back_numbers
                FROM algorithm_recommendation ar
                LEFT JOIN recommendation_details rd ON ar.id = rd.recommendation_metadata_id
                WHERE ar.period_number = %s AND rd.front_numbers IS NOT NULL
                """
                recommendations = self._execute_query(recommendation_query, (period_number,))

                if recommendations:
                    period_result = self._analyze_period_performance(
                        period_number, actual_numbers, recommendations
                    )
                    backtrack_results.append(period_result)
                    analyzed_periods += 1

                    # 保存奖罚记录
                    self._save_reward_penalty_records(period_result)

            print(f"✅ 成功分析 {analyzed_periods} 期数据")

            # 更新算法性能统计
            if backtrack_results:
                self._update_algorithm_performance(backtrack_results)

            # 转换Decimal为float以便JSON序列化
            summary_metrics = self._calculate_summary_metrics(backtrack_results)
            summary_metrics = self._convert_decimals_to_float(summary_metrics)

            return {
                'status': 'success',
                'total_periods_analyzed': analyzed_periods,
                'backtrack_results': self._convert_decimals_to_float(backtrack_results),
                'summary_metrics': summary_metrics
            }

        except Exception as e:
            print(f"❌ 算法回溯分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def _extract_actual_numbers(self, period_data: Dict) -> Dict[str, List[int]]:
        """从开奖数据中提取实际号码"""
        return {
            'front_numbers': [
                period_data['front_area_1'],
                period_data['front_area_2'],
                period_data['front_area_3'],
                period_data['front_area_4'],
                period_data['front_area_5']
            ],
            'back_numbers': [
                period_data['back_area_1'],
                period_data['back_area_2']
            ]
        }

    def _analyze_period_performance(self, period_number: str, actual_numbers: Dict,
                                    recommendations: List) -> Dict[str, Any]:
        """分析单期算法表现"""
        period_results = []

        for recommendation in recommendations:
            performance = self._calculate_hit_performance(recommendation, actual_numbers)

            period_results.append({
                'period_number': period_number,
                'recommendation_id': recommendation.get('id'),
                'algorithm_version': recommendation.get('algorithm_version', 'unknown'),
                'performance': performance
            })

        return {
            'period_number': period_number,
            'actual_numbers': actual_numbers,
            'recommendation_results': period_results
        }

    def _calculate_hit_performance(self, recommendation: Dict,
                                   actual_numbers: Dict) -> Dict[str, Any]:
        """计算命中表现"""
        try:
            front_numbers_str = recommendation.get('front_numbers', '')
            back_numbers_str = recommendation.get('back_numbers', '')

            if not front_numbers_str or not back_numbers_str:
                return {
                    'front_hits': 0,
                    'back_hits': 0,
                    'hit_score': 0,
                    'is_winning': False
                }

            # 使用清理函数处理号码
            recommended_front = self._clean_numbers_string(front_numbers_str)
            recommended_back = self._clean_numbers_string(back_numbers_str)

            if not recommended_front or not recommended_back:
                return {
                    'front_hits': 0,
                    'back_hits': 0,
                    'hit_score': 0,
                    'is_winning': False
                }

            actual_front = actual_numbers['front_numbers']
            actual_back = actual_numbers['back_numbers']

            # 计算命中数
            front_hits = len(set(recommended_front) & set(actual_front))
            back_hits = len(set(recommended_back) & set(actual_back))

            # 计算命中得分
            hit_score = self._calculate_hit_score(front_hits, back_hits)

            return {
                'front_hits': front_hits,
                'back_hits': back_hits,
                'hit_score': hit_score,
                'is_winning': hit_score > 0
            }
        except Exception as e:
            print(f"⚠️ 计算命中表现失败: {e}")
            return {
                'front_hits': 0,
                'back_hits': 0,
                'hit_score': 0,
                'is_winning': False
            }

    def _calculate_hit_score(self, front_hits: int, back_hits: int) -> float:
        """计算命中得分 - 基于大乐透中奖规则"""
        score_map = {
            (5, 2): 100.0,  # 一等奖
            (5, 1): 50.0,  # 二等奖
            (5, 0): 10.0,  # 三等奖
            (4, 2): 8.0,  # 四等奖
            (4, 1): 5.0,  # 五等奖
            (3, 2): 5.0,  # 六等奖
            (4, 0): 3.0,  # 七等奖
            (3, 1): 2.0,  # 八等奖
            (2, 2): 2.0,  # 八等奖
            (3, 0): 1.0,  # 九等奖
            (1, 2): 1.0,  # 九等奖
            (2, 1): 1.0,  # 九等奖
            (0, 2): 1.0,  # 九等奖
        }

        return float(score_map.get((front_hits, back_hits), 0.0))

    def _save_reward_penalty_records(self, period_result: Dict):
        """保存奖罚记录"""
        for rec_result in period_result['recommendation_results']:
            try:
                performance = rec_result['performance']
                period_number = period_result['period_number']
                recommendation_id = rec_result['recommendation_id']

                # 检查是否已存在记录
                check_query = """
                SELECT id FROM reward_penalty_records 
                WHERE period_number = %s AND recommendation_id = %s
                """
                existing = self._execute_query(check_query, (period_number, recommendation_id))

                if existing:
                    print(f"⏭️ 期号 {period_number} 的奖罚记录已存在，跳过")
                    continue

                # 插入新记录
                insert_query = """
                INSERT INTO reward_penalty_records 
                (period_number, algorithm_version, recommendation_id, front_hit_count, 
                 back_hit_count, hit_score, reward_points, penalty_points, net_points,
                 performance_rating, hit_details, evaluation_time) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                reward_points = float(performance['hit_score']) * 10
                penalty_points = 0.0 if performance['hit_score'] > 0 else 2.0
                net_points = reward_points - penalty_points

                params = (
                    period_number,
                    rec_result['algorithm_version'],
                    recommendation_id,
                    performance['front_hits'],
                    performance['back_hits'],
                    float(performance['hit_score']),
                    float(reward_points),
                    float(penalty_points),
                    float(net_points),
                    self._calculate_performance_rating(performance['hit_score']),
                    json.dumps(performance, ensure_ascii=False),
                    datetime.now()
                )

                rows_affected = self._execute_update(insert_query, params)
                if rows_affected > 0:
                    print(f"✅ 保存奖罚记录: 期号 {period_number}, 算法 {rec_result['algorithm_version']}")
                else:
                    print(f"❌ 保存奖罚记录失败: 期号 {period_number}")

            except Exception as e:
                print(f"❌ 保存奖罚记录异常: {e}")
                continue

    def _calculate_performance_rating(self, hit_score: float) -> int:
        """计算表现评级"""
        if hit_score >= 50:
            return 5
        elif hit_score >= 10:
            return 4
        elif hit_score >= 5:
            return 3
        elif hit_score >= 1:
            return 2
        else:
            return 1

    def _update_algorithm_performance(self, backtrack_results: List[Dict]):
        """更新算法性能统计 - 修复版"""
        algorithm_stats = {}

        for period_result in backtrack_results:
            for rec_result in period_result['recommendation_results']:
                algo_version = rec_result['algorithm_version']
                performance = rec_result['performance']

                if algo_version not in algorithm_stats:
                    algorithm_stats[algo_version] = {
                        'total_recommendations': 0,
                        'total_hit_score': 0.0,
                        'winning_count': 0
                    }

                stats = algorithm_stats[algo_version]
                stats['total_recommendations'] += 1
                stats['total_hit_score'] += float(performance['hit_score'])
                if performance['is_winning']:
                    stats['winning_count'] += 1

        # 更新数据库 - 修复版，检查表结构
        for algo_version, stats in algorithm_stats.items():
            try:
                if stats['total_recommendations'] > 0:
                    avg_hit_score = stats['total_hit_score'] / stats['total_recommendations']
                    win_rate = stats['winning_count'] / stats['total_recommendations']

                    # 检查表是否存在必要字段
                    check_table_query = """
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'algorithm_performance' 
                    AND COLUMN_NAME IN ('total_recommendations', 'confidence_accuracy')
                    """
                    table_columns = self._execute_query(check_table_query)
                    available_columns = [col['COLUMN_NAME'] for col in table_columns]

                    # 检查是否已存在记录
                    check_query = "SELECT id FROM algorithm_performance WHERE algorithm_version = %s"
                    existing = self._execute_query(check_query, (algo_version,))

                    if existing:
                        # 更新 - 只更新存在的字段
                        update_fields = []
                        update_params = []

                        if 'total_recommendations' in available_columns:
                            update_fields.append("total_recommendations = %s")
                            update_params.append(stats['total_recommendations'])

                        if 'total_periods_analyzed' in available_columns:
                            update_fields.append("total_periods_analyzed = %s")
                            update_params.append(len(backtrack_results))

                        if 'confidence_accuracy' in available_columns:
                            update_fields.append("confidence_accuracy = %s")
                            update_params.append(float(win_rate))

                        update_fields.append("last_updated = %s")
                        update_params.append(datetime.now())

                        if update_fields:
                            update_query = f"""
                            UPDATE algorithm_performance 
                            SET {', '.join(update_fields)}
                            WHERE algorithm_version = %s
                            """
                            update_params.append(algo_version)
                            self._execute_update(update_query, update_params)
                    else:
                        # 插入 - 只插入存在的字段
                        insert_fields = ['algorithm_version']
                        insert_placeholders = ['%s']
                        insert_params = [algo_version]

                        if 'total_recommendations' in available_columns:
                            insert_fields.append('total_recommendations')
                            insert_placeholders.append('%s')
                            insert_params.append(stats['total_recommendations'])

                        if 'total_periods_analyzed' in available_columns:
                            insert_fields.append('total_periods_analyzed')
                            insert_placeholders.append('%s')
                            insert_params.append(len(backtrack_results))

                        if 'confidence_accuracy' in available_columns:
                            insert_fields.append('confidence_accuracy')
                            insert_placeholders.append('%s')
                            insert_params.append(float(win_rate))

                        insert_fields.append('last_updated')
                        insert_placeholders.append('%s')
                        insert_params.append(datetime.now())

                        insert_query = f"""
                        INSERT INTO algorithm_performance 
                        ({', '.join(insert_fields)}) 
                        VALUES ({', '.join(insert_placeholders)})
                        """
                        self._execute_update(insert_query, insert_params)

                    print(f"📈 更新算法性能: {algo_version} (胜率: {win_rate:.2%})")

            except Exception as e:
                print(f"❌ 更新算法 {algo_version} 性能失败: {e}")
                continue

    def _calculate_summary_metrics(self, backtrack_results: List[Dict]) -> Dict[str, float]:
        """计算回溯总结指标"""
        if not backtrack_results:
            return {}

        total_periods = len(backtrack_results)
        total_recommendations = 0
        total_hit_score = 0.0
        winning_recommendations = 0

        for period_result in backtrack_results:
            total_recommendations += len(period_result['recommendation_results'])
            for rec_result in period_result['recommendation_results']:
                total_hit_score += float(rec_result['performance']['hit_score'])
                if rec_result['performance']['is_winning']:
                    winning_recommendations += 1

        avg_hit_score = total_hit_score / total_recommendations if total_recommendations > 0 else 0.0
        win_rate = winning_recommendations / total_recommendations if total_recommendations > 0 else 0.0

        return {
            'avg_hit_score_per_recommendation': float(round(avg_hit_score, 2)),
            'win_rate': float(round(win_rate, 4)),
            'total_recommendations_analyzed': total_recommendations,
            'avg_recommendations_per_period': float(
                round(total_recommendations / total_periods, 2)) if total_periods > 0 else 0.0
        }

    def _convert_decimals_to_float(self, obj):
        """递归地将Decimal转换为float以便JSON序列化"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimals_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimals_to_float(item) for item in obj]
        else:
            return obj

    def get_backtracking_summary(self) -> Dict[str, Any]:
        """获取回溯分析摘要"""
        try:
            # 获取最近的算法性能
            performance_query = """
            SELECT algorithm_version, 
                   COALESCE(total_recommendations, 0) as total_recommendations,
                   COALESCE(confidence_accuracy, 0) as confidence_accuracy,
                   last_updated 
            FROM algorithm_performance 
            ORDER BY last_updated DESC 
            LIMIT 10
            """
            recent_performance = self._execute_query(performance_query)

            # 获取奖罚记录统计
            reward_query = """
            SELECT 
                COUNT(*) as total_records,
                COALESCE(AVG(hit_score), 0) as avg_hit_score,
                COALESCE(SUM(CASE WHEN hit_score > 0 THEN 1 ELSE 0 END), 0) as winning_records,
                COALESCE(AVG(front_hit_count), 0) as avg_front_hits,
                COALESCE(AVG(back_hit_count), 0) as avg_back_hits
            FROM reward_penalty_records
            """
            reward_stats = self._execute_query(reward_query)

            result = {
                'status': 'success',
                'algorithm_performance': self._convert_decimals_to_float(recent_performance),
                'reward_statistics': self._convert_decimals_to_float(reward_stats[0] if reward_stats else {}),
                'summary': {
                    'total_algorithms_tracked': len(recent_performance),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }

            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}