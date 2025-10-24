# 用户购买记录DAO
# src/database/curd/user_purchase_dao.py
from typing import List, Dict
from datetime import datetime
from ..AllDao import AllDAO
from src.model.lottery_models import UserPurchaseRecord


class UserPurchaseDAO(AllDAO):
    """用户购买记录数据访问对象"""

    def insert_user_purchase_records_batch(self, period_metadata_id: int, purchases: List[Dict]) -> bool:
        """批量插入用户购买记录"""
        query = """
        INSERT INTO user_purchase_records (
            period_metadata_id, user_id, purchase_type,
            front_numbers_purchased, back_numbers_purchased,
            cost, is_hit, front_hit_count, back_hit_count,
            winnings_amount, purchase_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params_list = []
        for purchase in purchases:
            params = (
                period_metadata_id,
                purchase.get('user_id', 'default'),
                purchase.get('purchase_type'),
                purchase.get('front_numbers_purchased'),
                purchase.get('back_numbers_purchased'),
                float(purchase.get('cost', 0)),
                bool(purchase.get('is_hit', False)),
                purchase.get('front_hit_count', 0),
                purchase.get('back_hit_count', 0),
                float(purchase.get('winnings_amount', 0)),
                datetime.now()
            )
            params_list.append(params)

        return self.execute_many(query, params_list)

    def insert_user_purchase_record(self, record: UserPurchaseRecord) -> bool:
        """插入用户购买记录"""
        query = """
        INSERT INTO user_purchase_records (
            period_metadata_id, user_id, purchase_type,
            front_numbers_purchased, back_numbers_purchased,
            cost, is_hit, front_hit_count, back_hit_count,
            winnings_amount, purchase_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            record.period_metadata_id,
            record.user_id,
            record.purchase_type,
            record.front_numbers_purchased,
            record.back_numbers_purchased,
            record.cost,
            record.is_hit,
            record.front_hit_count,
            record.back_hit_count,
            record.winnings_amount,
            record.purchase_time
        )
        return self.execute_update(query, params)

    def get_user_purchase_records(self, period_metadata_id: int) -> List[UserPurchaseRecord]:
        """获取用户购买记录列表"""
        query = """
        SELECT * FROM user_purchase_records 
        WHERE period_metadata_id = %s
        """
        results = self.execute_query(query, (period_metadata_id,))
        records = []
        for row in results:
            record = UserPurchaseRecord(
                id=row['id'],
                period_metadata_id=row['period_metadata_id'],
                user_id=row['user_id'],
                purchase_type=row['purchase_type'],
                front_numbers_purchased=row['front_numbers_purchased'],
                back_numbers_purchased=row['back_numbers_purchased'],
                cost=float(row['cost']) if row['cost'] else None,
                is_hit=bool(row['is_hit']),
                front_hit_count=row['front_hit_count'],
                back_hit_count=row['back_hit_count'],
                winnings_amount=float(row['winnings_amount']) if row['winnings_amount'] else None,
                purchase_time=row['purchase_time'],
                created_at=row['created_at']
            )
            records.append(record)
        return records