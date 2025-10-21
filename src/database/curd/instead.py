# insert_lottery_data.py
import mysql.connector
from datetime import datetime
import  json

# 测试插入一条数据
# 修改后的 insert_lottery_record() 函数# 修改后的 insert_lottery_record() 函数
def insert_lottery_record():
    """插入一条历史开奖记录"""

    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 3309,
        'user': 'root',
        'password': '123456789',
        'database': 'lottery_analysis_system',
        'charset': 'utf8mb4'
    }

    try:
        # 连接数据库
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # 准备要插入的数据
        period_number = "2025067"
        draw_date = datetime.strptime("2025-06-07", "%Y-%m-%d").date()
        draw_time = datetime.now()

        # 解析开奖号码
        front_numbers = [6, 10, 12, 21, 22]
        back_numbers = [1, 6]

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

        # 连号信息（转换为JSON字符串）
        consecutive_numbers = []
        sorted_front = sorted(front_numbers)
        for i in range(len(sorted_front) - 1):
            if sorted_front[i] + 1 == sorted_front[i + 1]:
                consecutive_numbers.append([sorted_front[i], sorted_front[i + 1]])

        # 将列表转换为JSON字符串
        import json
        consecutive_numbers_json = json.dumps(consecutive_numbers)

        # 跨度计算
        span_value = max(front_numbers) - min(front_numbers)

        # 插入SQL语句
        insert_query = """
        INSERT INTO lottery_history (
            period_number, draw_date, draw_time,
            front_area_1, front_area_2, front_area_3, front_area_4, front_area_5,
            back_area_1, back_area_2,
            sum_value, span_value, ac_value, odd_even_ratio, size_ratio,
            consecutive_numbers, consecutive_count, tail_numbers
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        """

        # 执行插入
        cursor.execute(insert_query, (
            period_number, draw_date, draw_time,
            front_numbers[0], front_numbers[1], front_numbers[2], front_numbers[3], front_numbers[4],
            back_numbers[0], back_numbers[1],
            sum_value, span_value, 0,  # AC值暂时设为0
            odd_even_ratio, size_ratio,
            consecutive_numbers_json, len(consecutive_numbers), None  # 尾数暂时为空
        ))

        # 提交事务
        connection.commit()
        print(f"成功插入期号 {period_number} 的开奖记录")

    except Exception as e:
        print(f"插入数据时出错: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    insert_lottery_record()
