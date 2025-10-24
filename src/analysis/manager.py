# dlt_lottery_manager.py
import requests
import json
import os
from datetime import datetime


# 更新历史数据接口

# 配置常量
DATA_FILENAME = "大乐透历史开奖数据.md"
JSON_DATA_FILENAME = "dlt_history_data.json"
API_URL = "https://www.mxnzp.com/api/lottery/common/history"
API_PARAMS = {
    "code": "cjdlt",
    "size": "50",  # 首次获取50条记录
    "app_id": "jxiipcnflvfqzshq",
    "app_secret": "YobXpwlknmoevRgCxGbxcUZftMSznHQ2"
}

def process_opencodes(data_list):
    """
    遍历数据列表，对每一条记录的 'openCode' 字段进行排序和规范化处理。
    修正了解包错误，现在处理 X+Y+Z 格式。
    """
    processed_list = []

    for item in data_list:
        open_code_str = item.get('openCode')

        if not open_code_str:
            processed_list.append(item)
            continue

        try:
            # 1. 区分前后区 (现在预期是 3 个部分)
            parts = open_code_str.split('+')

            if len(parts) != 3:
                # 处理非预期的 X+Y+Z 格式
                print(
                    f"警告：期号 {item.get('expect', '未知期号')} 的 openCode 格式非预期 (非 X+Y+Z 格式)。原始 openCode: {open_code_str}")
                processed_list.append(item)
                continue

            front_area_str = parts[0]
            # 后区号码是 parts[1] 和 parts[2]
            back_codes_str = [parts[1], parts[2]]

            # 2. 将前区字符串转换为整数列表 (假设前区号码之间用逗号分隔)
            front_codes = [int(n) for n in front_area_str.split(',') if n.strip()]

            # 3. 将后区字符串转换为整数列表
            # 后区号码本身已经独立，不需要再次 split(',')
            back_codes = [int(n) for n in back_codes_str if n.strip()]

            # 4. 分别进行从小到大的排序
            front_codes.sort()
            back_codes.sort()

            # 5. 重新组合成规范化的字符串 (数字补零，例如 '5' 变为 '05')
            sorted_front_str = ','.join(f'{n:02d}' for n in front_codes)
            sorted_back_str = ','.join(f'{n:02d}' for n in back_codes)

            # 6. 拼接成最终的规范格式 (使用标准的 前区+后区 格式)
            new_open_code = f"{sorted_front_str}+{sorted_back_str}"

            # 7. 更新数据项
            item['openCode'] = new_open_code

            # 增加额外的字段方便 AI 理解 (可选)
            item['frontArea'] = front_codes
            item['backArea'] = back_codes

            # 1. frontArea_Sum (和值)
            item['frontArea_Sum'] = sum(front_codes)

            # 2. frontArea_OddEven (奇偶比)
            odd_count = sum(1 for n in front_codes if n % 2 != 0)
            even_count = len(front_codes) - odd_count
            item['frontArea_OddEven'] = f"{odd_count}:{even_count}"

            # 3. frontArea_IsConsecutive (连号判断)
            # 判断是否存在至少一对相邻号码差值为 1
            is_consecutive = False
            for i in range(len(front_codes) - 1):
                if front_codes[i + 1] - front_codes[i] == 1:
                    is_consecutive = True
                    break
            item['frontArea_IsConsecutive'] = is_consecutive

            # 4. frontArea_Span (跨度)
            # 跨度 = 最大号 - 最小号
            if front_codes:
                item['frontArea_Span'] = front_codes[-1] - front_codes[0]
            else:
                item['frontArea_Span'] = 0  # 避免空列表报错

        except Exception as e:
            # 捕获任何在处理过程中发生的错误，并记录下来
            print(f"处理期号 {item.get('expect', '未知期号')} 的 openCode 时发生错误: {e}")
            print(f"原始 openCode: {open_code_str}")

        processed_list.append(item)

    return processed_list
def save_data_for_ai(data, filename=DATA_FILENAME):
    """
    将结构化数据保存为 Markdown 格式，保持原有格式并在顶部添加新数据。

    参数:
    data (list): 从 API 获取的原始彩票数据列表。
    filename (str): 要保存的文件名。
    """
    if not data:
        print("没有数据可保存。")
        return

    # --- 关键优化: 使用 'expect' 字段进行期号排序 ---
    def get_issue_number(item):
        """从数据项中提取期号 (expect) 并转为整数，用于降序排序。"""
        # 确保 'expect' 字段存在且可转换为整数
        return int(item.get('expect', 0))

    try:
        # 按期号 (expect) 降序排序，保证最新的数据在列表前部
        data_sorted = sorted(data, key=get_issue_number, reverse=True)
    except Exception as e:
        print(f"警告：期号排序失败。请检查 'expect' 字段是否为可转为整数的字符串。错误: {e}")
        data_sorted = data  # 排序失败则使用原始顺序

    # 确保保存目录存在
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)

    # 如果文件存在，读取现有内容
    existing_lines = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()

    # 查找表格开始位置（通常是第4行，即"| 期号 | 开奖号码..."）
    table_start_index = 0
    for i, line in enumerate(existing_lines):
        if line.startswith("| 期号 |"):
            table_start_index = i
            break

    # 提取表格头部（包括标题和表头）
    header_lines = existing_lines[:table_start_index + 2] if existing_lines else [
        "# 大乐透历史开奖数据\n\n",
        "| 期号 | 开奖号码 | 前区 | 后区 | 和值 | 奇偶比 | 是否连号 | 跨度 |\n",
        "|------|----------|------|------|------|--------|----------|------|\n"
    ]

    # 提取已有数据行（除了头部）
    existing_data_lines = existing_lines[table_start_index + 2:] if len(existing_lines) > table_start_index + 2 else []

    # 准备新增数据行
    new_data_lines = []
    for item in data_sorted:
        expect = item.get('expect', '未知')
        open_code = item.get('openCode', '未知')
        front_area = ','.join(map(str, item.get('frontArea', [])))
        back_area = ','.join(map(str, item.get('backArea', [])))
        sum_value = item.get('frontArea_Sum', '')
        odd_even = item.get('frontArea_OddEven', '')
        is_consecutive = '是' if item.get('frontArea_IsConsecutive') else '否'
        span = item.get('frontArea_Span', '')

        new_data_lines.append(f"| {expect} | {open_code} | {front_area} | {back_area} | {sum_value} | {odd_even} | {is_consecutive} | {span} |\n")

    # 写入文件：头部 + 新数据 + 原有数据
    with open(filename, 'w', encoding='utf-8') as f:
        # 写入头部
        f.writelines(header_lines)
        # 写入新数据
        f.writelines(new_data_lines)
        # 写入原有数据
        f.writelines(existing_data_lines)

    # 同时保存JSON格式文件用于后续处理
    json_filename = JSON_DATA_FILENAME
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(data_sorted, f, ensure_ascii=False, indent=4)

    print(f"\n数据已成功保存到文件：{filename}")
    print("---------------------------------")

def load_existing_data():
    """
    加载现有的数据文件
    """
    if os.path.exists(JSON_DATA_FILENAME):
        try:
            with open(JSON_DATA_FILENAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    return []

def get_latest_lottery_data(size=1):
    """
    获取最新的彩票数据

    参数:
    size (int): 获取记录的数量，默认为1条最新记录
    """
    params = API_PARAMS.copy()
    params['size'] = str(size)

    print(f"开始请求大乐透最新数据... URL: {API_URL}")
    print(f"查询参数: {params}")

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()

        print("请求成功！正在解析数据...")
        data = response.json()

        if data.get('code') == 1 and 'data' in data and isinstance(data['data'], list):
            lottery_data_list = data['data']
            if lottery_data_list:
                print(f"成功获取 {len(lottery_data_list)} 条开奖记录。")
                return process_opencodes(lottery_data_list)
            else:
                print("API 返回成功，但数据列表为空。")
        else:
            print(f"API 返回错误或非预期结构。API code: {data.get('code')}, 消息: {data.get('msg')}")

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
    except json.JSONDecodeError:
        print("无法解析 JSON 响应。")

    return []
def update_lottery_data():
    """
    更新彩票数据，只添加新的不重复记录（不会替换现有数据）
    """
    # 获取最新的1条记录来检查是否有更新
    latest_data = get_latest_lottery_data(1)

    if not latest_data:
        print("无法获取最新数据，更新失败。")
        return False

    latest_record = latest_data[0]
    latest_expect = latest_record.get('expect')

    # 加载现有数据
    existing_data = load_existing_data()

    # 检查最新期号是否已存在（统一转换为字符串进行比较）
    existing_expects = {str(item.get('expect')) for item in existing_data}

    if str(latest_expect) in existing_expects:
        print(f"最新期号 {latest_expect} 已存在，无需更新。")
        return False

    # 获取更多数据以确保不会遗漏
    print("发现新期号，正在获取更多数据...")
    more_data = get_latest_lottery_data(5)  # 只获取最近5条记录，避免获取过多历史数据

    # 找出新增的记录
    new_records = []
    for record in more_data:
        expect = record.get('expect')
        if str(expect) not in existing_expects:
            new_records.append(record)
            print(f"发现新期号: {expect}")

    if new_records:
        # 合并数据并重新保存
        combined_data = existing_data + new_records  # 注意：这里使用 + 而不是 +=，确保顺序正确
        save_data_for_ai(combined_data)
        print(f"成功添加 {len(new_records)} 条新记录。")
        return True
    else:
        print("未发现新记录。")
        return False


def initial_fetch():
    """
    首次全量获取数据
    """
    print("执行首次全量数据获取...")
    params = API_PARAMS.copy()
    params['size'] = '50'  # 首次获取50条记录

    print(f"开始请求大乐透历史数据... URL: {API_URL}")
    print(f"查询参数: {params}")

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()

        print("请求成功！正在解析数据...")
        data = response.json()

        if data.get('code') == 1 and 'data' in data and isinstance(data['data'], list):
            lottery_data_list = data['data']

            if lottery_data_list:
                print(f"成功获取 {len(lottery_data_list)} 条历史开奖记录。")
                print("正在对 openCode 进行前后区分排序和格式化...")
                processed_data = process_opencodes(lottery_data_list)

                # 保存数据
                save_data_for_ai(processed_data)
                print("首次数据获取完成。")
            else:
                print("API 返回成功，但数据列表为空。")
        else:
            print(f"API 返回错误或非预期结构。API code: {data.get('code')}, 消息: {data.get('msg')}")

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
    except json.JSONDecodeError:
        print("无法解析 JSON 响应。")


def main():
    """
    主函数：首次运行时全量获取数据，之后每天运行时检查更新
    """
    if not os.path.exists(DATA_FILENAME):
        print("检测到首次运行，执行全量数据获取...")
        initial_fetch()
    else:
        print("检测到已有数据文件，执行增量更新检查...")
        update_lottery_data()

if __name__ == "__main__":
    main()
