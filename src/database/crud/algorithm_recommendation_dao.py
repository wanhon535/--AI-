# src/database/crud/algorithm_recommendation_dao.py
import json
import re
from typing import List, Optional, Dict,Any
from datetime import datetime
from ..AllDao import AllDAO
from src.model.lottery_models import AlgorithmRecommendation


class AlgorithmRecommendationDAO(AllDAO):
    """算法推荐数据访问对象"""

    def insert_algorithm_recommendation_root(self, period_number: str, algorithm_version: str,
                                             confidence_score: float, risk_level: str,
                                             analysis_basis: Optional[str] = None) -> Optional[int]:
        """
        插入算法推荐根记录，返回插入的ID。
        V2.1: 在保留原有逻辑基础上，增加了 algorithm_version 和 analysis_basis 参数。
        """
        # --- 您原有的输入验证逻辑，保持不变 ---
        if not period_number or not algorithm_version:
            # <<< 关键修改 1/3 >>>：将 model_name 检查改为 algorithm_version
            print("❌ Invalid input: period_number and algorithm_version are required.")
            return None
        if not (0.0 <= confidence_score <= 1.0):
            print("❌ Invalid confidence_score: Must be between 0.0 and 1.0.")
            return None

        # --- SQL 语句保持不变，因为它已经包含了所有字段 ---
        query = """
        INSERT INTO algorithm_recommendation (
            period_number, recommend_time, algorithm_version,
            algorithm_parameters, model_weights,
            confidence_score, risk_level, analysis_basis, key_patterns, models
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # --- 参数准备部分进行修改 ---
        params = (
            period_number,
            datetime.now(),
            # <<< 关键修改 2/3 >>>：使用新的 algorithm_version 参数
            algorithm_version,
            None,  # algorithm_parameters
            None,  # model_weights
            confidence_score,
            risk_level,
            # <<< 关键修改 3/3 >>>：使用新的 analysis_basis 参数
            analysis_basis,
            None,  # key_patterns
            algorithm_version  # models (这里也使用 algorithm_version 保持一致)
        )

        # --- 您原有的数据库操作和错误处理逻辑，保持不变 ---
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                last_id = self.get_last_insert_id(cursor)
                print(f"✅ 插入推荐主记录成功，ID: {last_id}")
                return last_id
        except Exception as e:
            print(f"❌ 插入推荐主记录失败: {e}")
            self.connection.rollback()
            return None

    def insert_algorithm_recommendation(self, recommendation: AlgorithmRecommendation) -> Optional[int]:
        """插入算法推荐记录，返回插入的ID"""
        query = """
        INSERT INTO algorithm_recommendation (
            period_number, recommend_time, algorithm_version,
            algorithm_parameters, model_weights,
            confidence_score, risk_level, analysis_basis, key_patterns, models
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            recommendation.period_number,
            recommendation.recommend_time,
            recommendation.algorithm_version,
            json.dumps(recommendation.algorithm_parameters) if recommendation.algorithm_parameters else None,
            json.dumps(recommendation.model_weights) if recommendation.model_weights else None,
            recommendation.confidence_score,
            recommendation.risk_level,
            json.dumps(recommendation.analysis_basis) if recommendation.analysis_basis else None,
            json.dumps(recommendation.key_patterns) if recommendation.key_patterns else None,
            recommendation.algorithm_version
        )

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                last_id = self.get_last_insert_id(cursor)
                print(f"✅ 插入推荐记录成功，ID: {last_id}")
                return last_id
        except Exception as e:
            print(f"❌ 插入推荐记录失败: {e}")
            self.connection.rollback()
            return None

    def get_recommendation_by_period(self, period_number: str) -> Optional[AlgorithmRecommendation]:
        """根据期号获取推荐记录"""
        query = """
        SELECT * FROM algorithm_recommendation 
        WHERE period_number = %s 
        ORDER BY recommend_time DESC 
        LIMIT 1
        """
        results = self.execute_query(query, (period_number,))
        if results:
            row = results[0]
            return AlgorithmRecommendation(
                id=row['id'],
                period_number=row['period_number'],
                recommend_time=row['recommend_time'],
                algorithm_version=row['algorithm_version'],
                algorithm_parameters=json.loads(row['algorithm_parameters']) if row['algorithm_parameters'] else None,
                model_weights=json.loads(row['model_weights']) if row['model_weights'] else None,
                confidence_score=float(row['confidence_score']),
                risk_level=row['risk_level'],
                analysis_basis=json.loads(row['analysis_basis']) if row['analysis_basis'] else None,
                key_patterns=json.loads(row['key_patterns']) if row['key_patterns'] else None
            )
        return None

    def get_earliest_period(self) -> Optional[int]:
        """获取 algorithm_recommendation 表中最早的期号"""
        sql = "SELECT period_number FROM algorithm_recommendation ORDER BY period_number ASC LIMIT 1"
        try:
            results = self.execute_query(sql)
            if results:
                return int(results[0]['period_number'])
            return None
        except Exception as e:
            print(f"❌ 获取最早期号异常: {e}")
            return None

    def get_latest_period(self) -> Optional[int]:
        """获取 algorithm_recommendation 表中最新的期号"""
        sql = "SELECT period_number FROM algorithm_recommendation ORDER BY period_number DESC LIMIT 1"
        try:
            results = self.execute_query(sql)
            if results:
                return int(results[0]['period_number'])
            return None
        except Exception as e:
            print(f"❌ 获取最新期号异常: {e}")
            return None

    def get_by_period(self, period_number: str) -> List[Dict[str, Any]]:
        """
        查询某一期号的所有算法推荐记录
        返回列表，每条记录包含:
        - model_name
        - recommended_numbers
        - confidence_score
        """
        sql = "SELECT * FROM algorithm_recommendation WHERE period_number=%s"
        try:
            results = self.execute_query(sql, (period_number,))
            return results
        except Exception as e:
            print(f"❌ 查询 period_number={period_number} 异常: {e}")
            return []




    def get_latest_id(self) -> Optional[int]:
        """获取最新插入记录的ID"""
        try:
            with self.connection.cursor() as cursor:
                return self.get_last_insert_id(cursor)
        except Exception as e:
            print(f"⚠️ 获取最新插入ID失败: {e}")
            return None

    @staticmethod
    def parse_ai_recommendations(content: str) -> List[Dict]:
        """解析AI返回的推荐内容（支持Markdown表格和加粗格式）"""
        recommendations = []
        if not content:
            return recommendations

        lines = content.strip().split('\n')

        # 1. 找到表格的表头行索引
        header_index = -1
        for i, line in enumerate(lines):
            if "推荐类型" in line and "策略逻辑" in line and line.strip().startswith('|'):
                header_index = i
                break

        if header_index == -1:
            print("❌ 解析失败：未在内容中找到推荐表格的表头。")
            return recommendations

        # 2. 跳过表头和分隔线
        data_start_index = header_index + 1
        if data_start_index < len(lines) and '---' in lines[data_start_index]:
            data_start_index += 1

        # 3. 编译正则表达式以提高效率
        pattern = re.compile(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')

        for i in range(data_start_index, len(lines)):
            line = lines[i].strip()
            if not line.startswith('|'):
                break

            match = pattern.match(line)
            if not match:
                continue

            try:
                recommend_type = re.sub(r'\*\*', '', match.group(1)).strip()
                strategy_logic = re.sub(r'\*\*', '', match.group(2)).strip()
                front_numbers = re.sub(r'\*\*', '', match.group(3)).strip()
                back_numbers = re.sub(r'\*\*', '', match.group(4)).strip()
                win_probability = float(re.sub(r'\*\*', '', match.group(5)).strip())

                recommendations.append({
                    "recommend_type": recommend_type,
                    "strategy_logic": strategy_logic,
                    "front_numbers": front_numbers,
                    "back_numbers": back_numbers,
                    "win_probability": win_probability
                })
            except (ValueError, IndexError) as e:
                print(f"⚠️ 跳过格式不正确的行: '{line}'. 错误: {e}")
                continue

        return recommendations
