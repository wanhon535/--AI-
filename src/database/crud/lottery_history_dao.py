# 彩票历史数据
# src/database/curd/lottery_history_dao.py
import json
from typing import List, Optional
from datetime import datetime
from ..AllDao import AllDAO
from src.model.lottery_models import LotteryHistory


class LotteryHistoryDAO(AllDAO):
    """彩票历史数据访问对象"""

    def get_latest_lottery_history(self, limit: int = 50) -> List[LotteryHistory]:
        """获取最新的历史开奖数据（按日期倒序）"""
        query = """
           SELECT * FROM lottery_history 
           ORDER BY draw_date DESC 
           LIMIT %s
           """
        results = self.execute_query(query, (limit,))
        return self._convert_to_lottery_history_list(results)

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
           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            if isinstance(latest_period, str) and latest_period.isdigit():
                return str(int(latest_period) + 1)
            elif isinstance(latest_period, int):
                return str(latest_period + 1)
        return ""

    def _convert_to_lottery_history_list(self, results) -> List[LotteryHistory]:
        """将查询结果转换为 LotteryHistory 对象列表"""
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