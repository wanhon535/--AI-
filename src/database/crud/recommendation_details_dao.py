# 推荐详情
# src/database/curd/recommendation_details_dao.py
from typing import List, Dict
from ..AllDao import AllDAO
from src.model.lottery_models import RecommendationDetail


class RecommendationDetailsDAO(AllDAO):
    """推荐详情数据访问对象"""

    def insert_recommendation_details_batch(self, recommendation_id: int, details: List[Dict]) -> bool:
        """批量插入推荐详情记录"""
        query = """
           INSERT INTO recommendation_details (
               recommendation_metadata_id, recommend_type, strategy_logic,
               front_numbers, back_numbers, win_probability
           ) VALUES (%s, %s, %s, %s, %s, %s)
           """
        params_list = []
        for detail in details:
            params = (
                recommendation_id,
                detail.get('recommend_type'),
                detail.get('strategy_logic'),
                detail.get('front_numbers'),
                detail.get('back_numbers'),
                float(detail.get('win_probability', 0)) if detail.get('win_probability') else None
            )
            params_list.append(params)

        return self.execute_many(query, params_list)

    def insert_recommendation_detail(self, detail: RecommendationDetail) -> bool:
        """插入推荐详情记录"""
        query = """
           INSERT INTO recommendation_details (
               recommendation_metadata_id, recommend_type, strategy_logic,
               front_numbers, back_numbers, win_probability
           ) VALUES (%s, %s, %s, %s, %s, %s)
           """
        params = (
            detail.recommendation_metadata_id,
            detail.recommend_type,
            detail.strategy_logic,
            detail.front_numbers,
            detail.back_numbers,
            detail.win_probability
        )
        return self.execute_update(query, params)

    def get_recommendation_details(self, recommendation_id: int) -> List[RecommendationDetail]:
        """获取推荐详情列表"""
        query = """
           SELECT * FROM recommendation_details 
           WHERE recommendation_metadata_id = %s
           """
        results = self.execute_query(query, (recommendation_id,))
        details = []
        for row in results:
            detail = RecommendationDetail(
                id=row['id'],
                recommendation_metadata_id=row['recommendation_metadata_id'],
                recommend_type=row['recommend_type'],
                strategy_logic=row['strategy_logic'],
                front_numbers=row['front_numbers'],
                back_numbers=row['back_numbers'],
                win_probability=float(row['win_probability']) if row['win_probability'] else None,
                created_at=row['created_at']
            )
            details.append(detail)
        return details