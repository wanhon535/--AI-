# insert_lottery_data.py
import mysql.connector
from datetime import datetime
import json

def calculate_ac_value(front_numbers):
    """计算AC值"""
    # AC值 = (实际间距数 - 理论最小间距数) / (理论最大间距数 - 理论最小间距数)
    # 简化计算：间距数 - (号码个数 - 1)
    sorted_nums = sorted(front_numbers)
    gaps = []
    for i in range(len(sorted_nums) - 1):
        gap = sorted_nums[i+1] - sorted_nums[i] - 1
        if gap > 0:
            gaps.append(gap)
    return sum(gaps) - (len(front_numbers) - 1)

def calculate_tail_numbers(front_numbers, back_numbers):
    """计算尾数分布"""
    all_numbers = front_numbers + back_numbers
    tails = {}
    for num in all_numbers:
        tail = num % 10
        tails[tail] = tails.get(tail, 0) + 1
    return tails

def insert_lottery_record(period_number, draw_date_str, front_numbers, back_numbers):
    """插入一条历史开奖记录
    :param period_number: 期号
    :param draw_date_str: 开奖日期字符串 "YYYY-MM-DD"
    :param front_numbers: 前区号码列表
    :param back_numbers: 后区号码列表
    """

    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 3307,
        'user': 'root',
        'password': 'root',
        'database': 'lottery_analysis_system',
        'charset': 'utf8mb4'
    }

    connection = None
    cursor = None

    try:
        # 连接数据库
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # 解析开奖日期
        draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
        draw_time = datetime.now()

        # 计算和值
        sum_value = sum(front_numbers) + sum(back_numbers)

        # 奇偶比计算
        odd_count = sum(1 for num in front_numbers if num % 2 == 1)
        even_count = len(front_numbers) - odd_count
        odd_even_ratio = f"{odd_count}:{even_count}"

        # 大小比计算（以18为界）
        size_count = sum(1 for num in front_numbers if num > 18)
        small_count = len(front_numbers) - size_count
        size_ratio = f"{size_count}:{small_count}"

        # 质合比计算（质数：只能被1和自身整除的大于1的自然数）
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31}
        prime_count = sum(1 for num in front_numbers if num in primes)
        composite_count = len(front_numbers) - prime_count
        prime_composite_ratio = f"{prime_count}:{composite_count}"

        # 连号信息
        consecutive_numbers = []
        sorted_front = sorted(front_numbers)
        for i in range(len(sorted_front) - 1):
            if sorted_front[i] + 1 == sorted_front[i + 1]:
                # 找到连续序列
                seq = [sorted_front[i], sorted_front[i + 1]]
                j = i + 2
                while j < len(sorted_front) and sorted_front[j-1] + 1 == sorted_front[j]:
                    seq.append(sorted_front[j])
                    j += 1
                if len(seq) > 1 and seq not in consecutive_numbers:
                    consecutive_numbers.append(seq)

        consecutive_numbers_json = json.dumps(consecutive_numbers) if consecutive_numbers else None

        # 跨度计算
        span_value = max(front_numbers) - min(front_numbers)

        # AC值计算
        ac_value = calculate_ac_value(front_numbers)

        # 尾数分布
        tail_numbers_dict = calculate_tail_numbers(front_numbers, back_numbers)
        tail_numbers_json = json.dumps(tail_numbers_dict)

        # 插入SQL语句
        insert_query = """
        INSERT INTO lottery_history (
            period_number, draw_date, draw_time,
            front_area_1, front_area_2, front_area_3, front_area_4, front_area_5,
            back_area_1, back_area_2,
            sum_value, span_value, ac_value, odd_even_ratio, size_ratio, prime_composite_ratio,
            consecutive_numbers, consecutive_count, tail_numbers
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        """

        # 执行插入
        cursor.execute(insert_query, (
            period_number, draw_date, draw_time,
            front_numbers[0], front_numbers[1], front_numbers[2], front_numbers[3], front_numbers[4],
            back_numbers[0], back_numbers[1],
            sum_value, span_value, ac_value,
            odd_even_ratio, size_ratio, prime_composite_ratio,
            consecutive_numbers_json, len(consecutive_numbers), tail_numbers_json
        ))

        # 提交事务
        connection.commit()
        print(f"✅ 成功插入期号 {period_number} 的开奖记录")
        return True

    except mysql.connector.IntegrityError as e:
        print(f"❌ 数据重复错误: 期号 {period_number} 已存在")
        if connection:
            connection.rollback()
        return False
    except Exception as e:
        print(f"❌ 插入数据时出错: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def batch_insert_lottery_records(records):
    """批量插入开奖记录
    :param records: 记录列表，每条记录格式为 (period_number, draw_date_str, front_numbers, back_numbers)
    """
    success_count = 0
    fail_count = 0

    for record in records:
        period_number, draw_date_str, front_numbers, back_numbers = record
        if insert_lottery_record(period_number, draw_date_str, front_numbers, back_numbers):
            success_count += 1
        else:
            fail_count += 1

    print(f"📊 批量插入完成: 成功 {success_count} 条，失败 {fail_count} 条")

# 示例使用
if __name__ == "__main__":
    # 单条插入示例
    insert_lottery_record(
        period_number="2025067",
        draw_date_str="2025-06-07",
        front_numbers=[6, 10, 12, 21, 22],
        back_numbers=[1, 6]
    )

    # 批量插入示例
    sample_records = [
        ("2025068", "2025-06-09", [3, 7, 14, 18, 29], [2, 8]),
        ("2025069", "2025-06-11", [1, 8, 15, 23, 30], [3, 9]),
        ("2025070", "2025-06-13", [2, 5, 10, 17, 20], [4, 10]),

    ]

    batch_insert_lottery_records(sample_records)
