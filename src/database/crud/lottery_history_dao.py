# 彩票历史数据

# src/database/curd/lottery_history_dao.py
import json
from typing import List, Optional
from datetime import datetime
from ..AllDao import AllDAO
from src.model.lottery_models import LotteryHistory


class LotteryHistoryDAO(AllDAO):
    """彩票历史数据访问对象"""

    def get_by_period(self, period_number: str) -> Optional[LotteryHistory]:
        """
        根据期号获取一条历史开奖记录（返回 LotteryHistory 实例，如果找不到返回 None）
        """
        query = """
            SELECT *
            FROM lottery_history
            WHERE period_number = %s
            LIMIT 1
        """
        rows = self.execute_query(query, (period_number,))
        if not rows:
            return None

        row = rows[0]
        # 如果你有 LotteryHistory 类，构造它；否则返回原始字典
        try:
            return LotteryHistory(**row)
        except Exception:
            return row

    def get_earliest_period(self) -> Optional[str]:
        """返回 lottery_history 表中最早的期号（字符串）"""
        query = "SELECT period_number FROM lottery_history ORDER BY CAST(period_number AS UNSIGNED) ASC LIMIT 1"
        rows = self.execute_query(query)
        if not rows:
            return None
        return str(rows[0].get('period_number'))

    def get_latest_period(self) -> Optional[str]:
        """返回 lottery_history 表中最新的期号（字符串）"""
        query = "SELECT period_number FROM lottery_history ORDER BY CAST(period_number AS UNSIGNED) DESC LIMIT 1"
        rows = self.execute_query(query)
        if not rows:
            return None
        return str(rows[0].get('period_number'))

    def get_latest_lottery_history(self, limit: int = 50) -> List[LotteryHistory]:
        """
        获取最近几期的开奖记录，按期号降序返回（转换为 LotteryHistory 实例列表）
        """
        query = """
            SELECT *
            FROM lottery_history
            ORDER BY CAST(period_number AS UNSIGNED) DESC
            LIMIT %s
        """
        rows = self.execute_query(query, (limit,))

        # ✅ 使用一个统一的、健壮的转换方法
        return self._convert_rows_to_history_list(rows)

    # def get_lottery_history(self, limit: int = 100, offset: int = 0) -> List[LotteryHistory]:
    #     """获取历史开奖数据"""
    #     query = """
    #        SELECT * FROM lottery_history
    #        ORDER BY draw_date DESC
    #        LIMIT %s OFFSET %s
    #        """
    #     results = self.execute_query(query, (limit, offset))
    #     return self._convert_to_lottery_history_list(results)
    def get_lottery_history(self, limit: int = 100, offset: int = 0) -> List[LotteryHistory]:
        """
        分页获取历史开奖记录（默认返回最新100条）
        """
        query = """
            SELECT *
            FROM lottery_history
            ORDER BY CAST(period_number AS UNSIGNED) DESC
            LIMIT %s OFFSET %s
        """
        rows = self.execute_query(query, (limit, offset))

        # ✅ 使用一个统一的、健壮的转换方法
        return self._convert_rows_to_history_list(rows)

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

    def _convert_rows_to_history_list(self, rows: List[dict]) -> List[LotteryHistory]:
        """
        【新增的辅助方法】将从数据库查询出的字典行列表，安全地转换为 LotteryHistory 对象列表。
        这个方法会处理 JSON 字段的解析和字段名转换。
        """
        results = []
        if not rows:
            return results

        for row in rows:
            try:
                # 复制一份，避免修改原始数据
                processed_row = row.copy()
                
                # 将数据库字段转换为LotteryHistory类期望的参数格式
                # 前区号码
                front_area = [
                    processed_row.pop('front_area_1'),
                    processed_row.pop('front_area_2'),
                    processed_row.pop('front_area_3'),
                    processed_row.pop('front_area_4'),
                    processed_row.pop('front_area_5')
                ]
                processed_row['front_area'] = front_area
                
                # 后区号码
                back_area = [
                    processed_row.pop('back_area_1'),
                    processed_row.pop('back_area_2')
                ]
                processed_row['back_area'] = back_area

                # --- 核心修正：手动解析 JSON 字符串 ---
                if 'consecutive_numbers' in processed_row and isinstance(processed_row['consecutive_numbers'], str):
                    processed_row['consecutive_numbers'] = json.loads(processed_row['consecutive_numbers'])
                if 'tail_numbers' in processed_row and isinstance(processed_row['tail_numbers'], str):
                    processed_row['tail_numbers'] = json.loads(processed_row['tail_numbers'])

                # 现在 processed_row 中的数据类型是正确的，可以安全地创建对象
                results.append(LotteryHistory(**processed_row))

            except (json.JSONDecodeError, TypeError, KeyError) as e:
                print(f"⚠️ 解析或转换期号 {row.get('period_number')} 的数据时出错: {e}。该条记录将被跳过。")
                # 选择性地将原始行加入，或者直接跳过
                # results.append(row)
                continue
        return results

    def get_all_period_numbers(self) -> set:
        """获取数据库中所有已存在的期号集合，用于快速去重检查。"""
        query = "SELECT period_number FROM lottery_history"
        rows = self.execute_query(query)
        return {str(r['period_number']) for r in rows}

    def is_table_empty(self) -> bool:
        """检查 lottery_history 表是否为空。"""
        query = "SELECT 1 FROM lottery_history LIMIT 1"
        return not self.execute_query(query)

    def get_all_history(self, limit=None):
        query = "SELECT * FROM lottery_history ORDER BY draw_date ASC"
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query)

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