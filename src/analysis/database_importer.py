# file: database_importer.py
import traceback

import requests
import json
from datetime import datetime
import os
import sys

# --- 环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.database.crud.lottery_history_dao import LotteryHistoryDAO
from src.model.lottery_models import LotteryHistory

# --- API 配置 ---
API_URL = "https://www.mxnzp.com/api/lottery/common/history"
API_PARAMS = {
    "code": "cjdlt",
    "size": "50",
    "app_id": "jxiipcnflvfqzshq",
    "app_secret": "YobXpwlknmoevRgCxGbxcUZftMSznHQ2"
}

# --- 数据库配置 ---
DB_CONFIG = dict(
    host='127.0.0.1', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)


def parse_api_data_to_lotteryhistory(api_item: dict) -> LotteryHistory:
    """将从API获取的单条记录转换为 LotteryHistory 对象。"""
    open_code_str = api_item.get('openCode')
    parts = open_code_str.split('+')

    front_codes_str = parts[0]
    back_codes_str = parts[1]  # API的后区已经是逗号分隔的

    front_codes = sorted([int(n) for n in front_codes_str.split(',')])
    back_codes = sorted([int(n) for n in back_codes_str.split(',')])

    # 计算附加统计特征
    odd_count = sum(1 for n in front_codes if n % 2 != 0)

    return LotteryHistory(
        period_number=api_item.get('expect'),
        draw_date=api_item.get('time').split(' ')[0],
        draw_time=api_item.get('time').split(' ')[1],
        front_area=front_codes,
        back_area=back_codes,
        sum_value=sum(front_codes),
        span_value=max(front_codes) - min(front_codes) if front_codes else 0,
        odd_even_ratio=f"{odd_count}:{len(front_codes) - odd_count}",
        # 其他字段可以根据需要计算或留空
        ac_value=0,
        size_ratio="",
        prime_composite_ratio="",
        consecutive_numbers=[],
        consecutive_count=0,
        tail_numbers=[],
        data_source="mxnzp_api",
        data_quality="raw"
    )


def sync_lottery_data_to_db(initial_fetch=False):
    """
    从API同步彩票数据到数据库。
    - initial_fetch=True: 首次运行时，会尝试获取50条数据。
    - initial_fetch=False: 日常更新，只获取最新的5条数据检查更新。
    """
    db = DatabaseManager(**DB_CONFIG)
    if not db.connect():
        print("❌ 数据库连接失败。")
        return

    history_dao = LotteryHistoryDAO(db)

    try:
        size = '50' if initial_fetch else '5'
        params = API_PARAMS.copy()
        params['size'] = size

        print(f"🔄 开始从API同步数据 (获取 {size} 条记录)...")
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        api_response = response.json()

        if api_response.get('code') != 1 or not api_response.get('data'):
            print(f"❌ API返回错误: {api_response.get('msg')}")
            return

        api_data_list = api_response['data']
        print(f"✅ 从API成功获取 {len(api_data_list)} 条记录。")

        # 获取数据库中已存在的期号
        existing_periods = history_dao.get_all_period_numbers()

        new_records_count = 0
        for item in reversed(api_data_list):  # 从最旧的开始插入，保证顺序
            period = item.get('expect')
            if period not in existing_periods:
                try:
                    lottery_record = parse_api_data_to_lotteryhistory(item)
                    if history_dao.insert_lottery_history(lottery_record):
                        print(f"  - ✅ 成功插入新开奖期号: {period}")
                        new_records_count += 1
                    else:
                        print(f"  - 🔴 插入期号 {period} 失败 (DAO操作返回False)。")
                except Exception as e:
                    print(f"  - 🔴 解析或插入期号 {period} 时出错: {e}")

        if new_records_count == 0:
            print("👌 数据库已是最新，无需更新。")
        else:
            print(f"🎉 成功向数据库同步了 {new_records_count} 条新记录！")

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求API时发生网络错误: {e}")
    except Exception as e:
        print(f"❌ 同步过程中发生未知错误: {e}")
        traceback.print_exc()
    finally:
        db.disconnect()
        print("🔌 数据库连接已关闭。")


def main():
    """主函数：检查数据库是否为空，决定是首次拉取还是日常更新。"""
    db = DatabaseManager(**DB_CONFIG)
    if not db.connect():
        print("❌ 数据库连接失败，无法执行同步。")
        return

    history_dao = LotteryHistoryDAO(db)
    is_empty = history_dao.is_table_empty()
    db.disconnect()

    if is_empty:
        print("检测到 'lottery_history' 表为空，执行首次数据同步...")
        sync_lottery_data_to_db(initial_fetch=True)
    else:
        print("检测到已有历史数据，执行增量更新检查...")
        sync_lottery_data_to_db(initial_fetch=False)


if __name__ == "__main__":
    main()

# file: src/database/crud/lottery_history_dao.py
# ... (在你的DAO类中添加这两个方法)