
# src/database/crud/add.py
from mysql.connector import Error
from typing import List, Dict, Any
from src.model.lottery_models import LotteryHistory, AlgorithmRecommendation, RecommendationDetail


def get_lottery_history(limit: int = 50) -> List[Dict]:
    """
    查询最近的历史开奖数据
    :param limit: 返回的记录数量，默认50条
    :return: 历史开奖数据列表
    """
    try:
        from src.database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        if not db_manager.connect():
            raise Exception("数据库连接失败")

        query = """
        SELECT 
            period_number,
            draw_date,
            draw_time,
            front_area_1, front_area_2, front_area_3, front_area_4, front_area_5,
            back_area_1, back_area_2
        FROM lottery_history
        ORDER BY period_number DESC
        LIMIT %s
        """
        result = db_manager.execute_query(query, (limit,))

        # 转换为字典格式
        history_data = []
        for row in result:
            history_data.append({
                "period_number": row["period_number"],
                "draw_date": row["draw_date"],
                "draw_time": row["draw_time"],
                "front_area": [
                    row["front_area_1"], row["front_area_2"], row["front_area_3"],
                    row["front_area_4"], row["front_area_5"]
                ],
                "back_area": [
                    row["back_area_1"], row["back_area_2"]
                ]
            })

        return history_data

    except Exception as e:
        print(f"❌ 查询历史数据失败: {e}")
        return []


def get_recommendations(period_number: str = None) -> List[Dict]:
    """
    查询算法推荐数据
    :param period_number: 指定期号，为空则查询所有
    :return: 推荐数据列表
    """
    try:
        from src.database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        if not db_manager.connect():
            raise Exception("数据库连接失败")

        query = """
        SELECT 
            ar.period_number,
            ar.recommend_time,
            ar.algorithm_version,
            ar.confidence_score,
            ar.risk_level,
            ar.analysis_basis,
            ar.key_patterns,
            ar.models,
            rd.recommendation_combinations,
            rd.front_numbers,
            rd.back_numbers,
            rd.win_probability
        FROM algorithm_recommendation ar
        LEFT JOIN recommendation_details rd ON ar.id = rd.recommendation_id
        WHERE 1=1
        """
        params = []

        if period_number:
            query += " AND ar.period_number = %s"
            params.append(period_number)

        query += " ORDER BY ar.recommend_time DESC"

        result = db_manager.execute_query(query, tuple(params))

        # 转换为字典格式
        recommendations = []
        for row in result:
            recommendations.append({
                "period_number": row["period_number"],
                "recommend_time": row["recommend_time"],
                "algorithm_version": row["algorithm_version"],
                "confidence_score": row["confidence_score"],
                "risk_level": row["risk_level"],
                "analysis_basis": row["analysis_basis"],
                "key_patterns": row["key_patterns"],
                "models": row["models"],
                "recommendation_combinations": row["recommendation_combinations"],
                "front_numbers": row["front_numbers"],
                "back_numbers": row["back_numbers"],
                "win_probability": row["win_probability"]
            })

        return recommendations

    except Exception as e:
        print(f"❌ 查询推荐数据失败: {e}")
        return []
