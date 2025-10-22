
import json
from typing import Dict, Any
from src.database.database_manager import DatabaseManager


def analyze_recommendation_performance(period_number: str) -> Dict[str, Any]:
    """
    分析某期推荐结果的表现（命中情况）。
    (优化版：使用JOIN查询，返回更详细的命中数据，并确保连接关闭)

    :param period_number: 期号
    :return: 包含详细分析结果的字典
    """
    db_manager = None  # 初始化变量以确保在 finally 块中可访问
    try:
        # 1. 初始化并连接数据库
        # 根据您的要求，数据库连接信息直接写在函数内部
        db_manager = DatabaseManager(
            host='localhost',
            user='root',
            password='root',
            database='lottery_analysis_system',
            port=3307  # 确保您的 DatabaseManager 支持 port 参数
        )
        if not db_manager.connect():
            raise ConnectionError("数据库连接失败，请检查配置信息。")

        # 2. 查询该期实际开奖数据
        query_lottery = """
        SELECT 
            front_area_1, front_area_2, front_area_3, front_area_4, front_area_5,
            back_area_1, back_area_2
        FROM lottery_history 
        WHERE period_number = %s
        """
        lottery_result = db_manager.execute_query(query_lottery, (period_number,))
        if not lottery_result:
            return {"error": f"未找到期号 {period_number} 的开奖数据"}

        # 提取开奖号码为整数集合，便于比对
        actual_front = {int(lottery_result[0][f'front_area_{i}']) for i in range(1, 6)}
        actual_back = {int(lottery_result[0][f'back_area_{i}']) for i in range(1, 3)}

        # 3. 查询该期所有推荐数据 (使用JOIN优化查询效率)
        query_recommend = """
        SELECT 
            rd.front_numbers, 
            rd.back_numbers
        FROM recommendation_details rd
        JOIN algorithm_recommendation ar ON rd.recommendation_metadata_id = ar.id
        WHERE ar.period_number = %s
        """
        recommendations = db_manager.execute_query(query_recommend, (period_number,))

        # 4. 详细分析每条推荐的命中情况
        analysis_details = []
        for rec in recommendations:
            # 清理字符串并转换为整数集合
            recommended_front = {int(n.strip()) for n in rec["front_numbers"].split(',') if n.strip()}
            recommended_back = {int(n.strip()) for n in rec["back_numbers"].split(',') if n.strip()}

            # 使用集合的交集(&)操作找到命中的号码
            front_hits_set = recommended_front.intersection(actual_front)
            back_hits_set = recommended_back.intersection(actual_back)

            analysis_details.append({
                "recommended_front": sorted(list(recommended_front)),
                "recommended_back": sorted(list(recommended_back)),
                "front_hit_count": len(front_hits_set),
                "back_hit_count": len(back_hits_set),
                "front_hit_numbers": sorted(list(front_hits_set)),  # 新增：命中的前区号码
                "back_hit_numbers": sorted(list(back_hits_set)),  # 新增：命中的后区号码
            })

        # 5. 组装最终返回结果
        return {
            "period_number": period_number,
            "actual_front": sorted(list(actual_front)),
            "actual_back": sorted(list(actual_back)),
            "analysis": analysis_details,
            "total_recommendations": len(analysis_details)
        }

    except Exception as e:
        print(f"❌ 分析推荐表现时发生严重错误: {e}")
        return {"error": str(e)}
    finally:
        # 6. 无论成功或失败，都确保关闭数据库连接
        if db_manager and hasattr(db_manager, 'is_connected') and db_manager.is_connected():
            db_manager.disconnect()
            print("数据库连接已安全关闭。")


def generate_performance_summary(analysis_data: Dict[str, Any]) -> str:
    """
    根据分析数据生成一段人类可读的总结报告。

    :param analysis_data: 来自 analyze_recommendation_performance 函数的返回结果
    :return: 格式化的字符串报告
    """
    if "error" in analysis_data:
        return f"生成分析报告失败: {analysis_data['error']}"

    period = analysis_data['period_number']
    actual_front_str = ', '.join(map(str, analysis_data['actual_front']))
    actual_back_str = ', '.join(map(str, analysis_data['actual_back']))

    # 报告头部
    summary_lines = [
        f"--- **第 {period} 期开奖结果分析报告** ---\n",
        f"**本期开奖号码**: 前区 [{actual_front_str}] | 后区 [{actual_back_str}]\n",
        f"**分析总览**: 共分析了 {analysis_data['total_recommendations']} 条推荐记录。\n"
    ]

    if not analysis_data['analysis']:
        summary_lines.append("本期没有找到任何推荐记录。")
    else:
        # 逐条分析推荐结果
        for i, result in enumerate(analysis_data['analysis']):
            rec_front_str = ','.join(map(str, result['recommended_front']))
            rec_back_str = ','.join(map(str, result['recommended_back']))

            line = f"**推荐 {i + 1}**: [{rec_front_str}] | [{rec_back_str}]"

            front_hit_count = result['front_hit_count']
            back_hit_count = result['back_hit_count']

            if front_hit_count > 0 or back_hit_count > 0:
                hit_parts = []
                if front_hit_count > 0:
                    front_hit_nums_str = ', '.join(map(str, result['front_hit_numbers']))
                    hit_parts.append(f"命中前区 {front_hit_count} 个号 ({front_hit_nums_str})")
                if back_hit_count > 0:
                    back_hit_nums_str = ', '.join(map(str, result['back_hit_numbers']))
                    hit_parts.append(f"命中后区 {back_hit_count} 个号 ({back_hit_nums_str})")

                line += f" -> **结果**: {' 和 '.join(hit_parts)}。"
            else:
                line += " -> **结果**: 未命中任何号码。"

            summary_lines.append(line)

    summary_lines.append("\n--- **报告结束** ---")

    return "\n".join(summary_lines)


# --- 主执行逻辑 ---
if __name__ == "__main__":
    # 设置您想分析的期号
    target_period = "2025068"

    print(f"🚀 正在分析第 {target_period} 期的推荐表现...")

    # 1. 调用函数获取结构化的分析数据
    analysis_result_data = analyze_recommendation_performance(target_period)

    # 2. 调用新函数生成并打印人类可读的总结报告
    summary_report = generate_performance_summary(analysis_result_data)

    print("\n" + summary_report)

    # (可选) 如果你还想看原始的JSON数据，可以取消下面的注释
    # print("\n--- 原始JSON数据 ---")
    # print(json.dumps(analysis_result_data, indent=4, ensure_ascii=False))