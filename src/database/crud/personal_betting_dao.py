"""个人投注数据访问对象"""
import json
# src/database/curd/personal_betting_dao.py
from typing import List
from ..AllDao import AllDAO

from src.model.lottery_models import PersonalBetting


class PersonalBettingDAO(AllDAO):
    """个人投注数据访问对象"""

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

    def insert(self, betting: PersonalBetting) -> bool:
        """插入个人投注记录"""
        query = """
        INSERT INTO personal_betting (
            user_id, period_number, bet_time, bet_type,
            front_numbers, front_count, back_numbers, back_count,
            bet_amount, multiple, is_winning, winning_level,
            winning_amount, strategy_type, confidence_level, analysis_notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            betting.user_id,
            betting.period_number,
            betting.bet_time,
            betting.bet_type,
            json.dumps(betting.front_numbers) if betting.front_numbers else None,
            betting.front_count,
            json.dumps(betting.back_numbers) if betting.back_numbers else None,
            betting.back_count,
            betting.bet_amount,
            betting.multiple,
            betting.is_winning,
            betting.winning_level,
            betting.winning_amount,
            betting.strategy_type,
            betting.confidence_level,
            betting.analysis_notes
        )
        return self.execute_update(query, params)