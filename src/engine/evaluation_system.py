# ======================================================================
# --- FILE: src/engine/evaluation_system.py (COMPLETE REPLACEMENT V3) ---
# ======================================================================

import json
import re  # 导入正则表达式模块
from typing import List, Dict, Any, Set

# 您的数据模型，如果路径不正确请相应修改
from src.model.lottery_models import (
    RewardPenaltyRecord
)

class EvaluationSystem:
    """
    评估系统 V3
    - 核心职责：根据开奖结果，计算单个推荐组合的奖罚得分。
    - 增强了数字解析的健壮性。
    """

    def calculate_reward_record(self, recommendation_main: Dict, recommendation_detail: Dict, actual_draw: Dict) -> Dict:
        """
        根据最终推荐详情和开奖结果，计算一个可直接存入数据库的“奖罚记录”字典。
        V3版 - 极度健壮，能处理各种格式错误的号码字符串。
        """
        # 1. 准备标准答案（开奖号码）
        actual_front: Set[int] = {actual_draw[f'front_area_{i + 1}'] for i in range(5)}
        actual_back: Set[int] = {actual_draw[f'back_area_{i + 1}'] for i in range(2)}

        # 2. 准备预测答案，并进行健壮的解析
        pred_front_str = recommendation_detail.get('front_numbers', '')
        pred_back_str = recommendation_detail.get('back_numbers', '')

        def parse_numbers(num_str: Any) -> Set[int]:
            """一个非常健壮的解析器，可以处理字符串、列表、None等。"""
            if not num_str:
                return set()
            # 如果已经是列表或集合，直接处理
            if isinstance(num_str, (list, set)):
                return {int(n) for n in num_str if str(n).isdigit()}
            # 如果是字符串，用正则表达式提取所有数字
            if isinstance(num_str, str):
                numbers = re.findall(r'\d+', num_str)
                return set(map(int, numbers))
            return set()

        pred_front_set = parse_numbers(pred_front_str)
        pred_back_set = parse_numbers(pred_back_str)

        # 3. 计算命中数
        front_hits = len(pred_front_set & actual_front)
        back_hits = len(pred_back_set & actual_back)

        # 4. 计算得分和奖罚
        # 评分逻辑：后区命中权重远大于前区
        hit_score = (front_hits * 10) + (back_hits * 25)
        reward_points = hit_score * 1.5
        penalty_points = 0 if hit_score > 5 else 50 # 只有得分大于5才免罚

        # 5. 组装成DAO需要的字典
        reward_data = {
            'period_number': recommendation_main['period_number'],
            'algorithm_version': recommendation_main['algorithm_version'],
            'recommendation_id': recommendation_main['id'],
            'front_hit_count': front_hits,
            'back_hit_count': back_hits,
            'hit_score': hit_score,
            'reward_points': reward_points,
            'penalty_points': penalty_points,
            'net_points': reward_points - penalty_points,
            'hit_details': json.dumps({
                "evaluated_combo_type": recommendation_detail.get('recommend_type', 'N/A'),
                "front_hits_numbers": sorted(list(pred_front_set & actual_front)),
                "back_hits_numbers": sorted(list(pred_back_set & actual_back))
            }, ensure_ascii=False),
            'missed_numbers': json.dumps({
                "front_missed": sorted(list(actual_front - pred_front_set)),
                "back_missed": sorted(list(actual_back - pred_back_set))
            }, ensure_ascii=False),
            'performance_rating': self._calculate_rating(front_hits, back_hits)
        }
        return reward_data

    def _calculate_rating(self, front_hits: int, back_hits: int) -> int:
        """根据命中数计算1-5星评级"""
        if back_hits == 2 and front_hits >= 3: return 5  # 一等奖
        if back_hits == 2 and front_hits == 2: return 4  # 二等奖
        if (back_hits == 1 and front_hits >= 3) or (back_hits == 2 and front_hits < 2): return 3 # 三、四等奖
        if front_hits >= 4: return 2 # 五、六等奖
        if (back_hits == 1 and front_hits < 3) or (front_hits == 3): return 1 # 七、八等奖
        return 0 # 未中奖