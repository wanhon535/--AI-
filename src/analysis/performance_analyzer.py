# file: src/analysis/performance_analyzer.py (V4.1 - 修复连接问题)

from typing import Dict, Any, List
# 注意：这里只需要导入类型，不需要再实例化了
from src.database.database_manager import DatabaseManager


def analyze_recommendation_performance(db_manager: DatabaseManager, period_number: str) -> Dict[str, Any]:
    """
    (V4.1 修复版)
    分析某期推荐结果，并按模型进行分组。
    👉 关键修复：复用传入的 db_manager 连接，不再自行创建和关闭。
    """
    try:
        # 0. 确保连接是活的
        if not db_manager.is_connected():
            # 尝试重连一次
            if not db_manager.connect():
                return {"error": "数据库连接已断开，且重连失败"}

        # 1. 查询开奖数据
        lottery_result = db_manager.execute_query("SELECT * FROM lottery_history WHERE period_number = %s",
                                                  (period_number,))
        if not lottery_result:
            return {"error": f"未找到期号 {period_number} 的开奖数据"}

        actual_front = {int(lottery_result[0][f'front_area_{i}']) for i in range(1, 6)}
        actual_back = {int(lottery_result[0][f'back_area_{i}']) for i in range(1, 3)}

        # 2. 使用JOIN一次性查询所有推荐详情及其所属模型
        query = """
            SELECT
                ar.model_name,
                rd.front_numbers,
                rd.back_numbers
            FROM recommendation_details rd
            JOIN algorithm_recommendation ar ON rd.recommendation_metadata_id = ar.id
            WHERE ar.period_number = %s
        """
        all_recommendations = db_manager.execute_query(query, (period_number,))

        # 3. 按模型对推荐数据进行分组
        grouped_results = {}
        for rec in all_recommendations:
            model_name = rec.get("model_name", "未知模型")
            if model_name not in grouped_results:
                grouped_results[model_name] = []

            front_nums = {int(n.strip()) for n in rec["front_numbers"].split(',') if n.strip()}
            back_nums = {int(n.strip()) for n in rec["back_numbers"].split(',') if n.strip()}

            grouped_results[model_name].append({
                "recommended_front": sorted(list(front_nums)),
                "recommended_back": sorted(list(back_nums)),
                "front_hit_count": len(front_nums.intersection(actual_front)),
                "back_hit_count": len(back_nums.intersection(actual_back)),
                "front_hit_numbers": sorted(list(front_nums.intersection(actual_front))),
                "back_hit_numbers": sorted(list(back_nums.intersection(actual_back))),
            })

        return {
            "period_number": period_number,
            "actual_front": sorted(list(actual_front)),
            "actual_back": sorted(list(actual_back)),
            "analysis_by_model": grouped_results
        }
    except Exception as e:
        return {"error": f"分析过程发生异常: {str(e)}"}
    # 这里不再有 finally { db_manager.disconnect() }，因为连接要留给 dashboard 继续用


def generate_performance_summary(analysis_data: Dict[str, Any]) -> str:
    """
    (V4.1 修复版) 生成结构化 Markdown 报告 (保持 V4.0 的分组展示逻辑不变)
    """
    if "error" in analysis_data:
        return f"### ❌ 分析失败\n{analysis_data['error']}"

    grouped_analysis = analysis_data.get("analysis_by_model", {})
    if not grouped_analysis:
        return "本期没有找到可供分析的推荐记录。"

    report_parts = []
    for model_name, recommendations in grouped_analysis.items():
        report_parts.append(f"#### 🤖 模型: **{model_name}** ({len(recommendations)}条推荐)")
        model_lines = []
        for i, result in enumerate(recommendations):
            front_nums = result.get('recommended_front', [])
            back_nums = result.get('recommended_back', [])
            bet_type = "(复式)" if len(front_nums) > 5 or len(back_nums) > 2 else "(单式)"
            line = f"- **推荐 {i + 1}** {bet_type}: `[{','.join(map(str, front_nums))}] | [{','.join(map(str, back_nums))}]`"

            front_hit = result.get('front_hit_count', 0)
            back_hit = result.get('back_hit_count', 0)
            if front_hit > 0 or back_hit > 0:
                hit_parts = []
                if front_hit > 0: hit_parts.append(f"前区命中 **{front_hit}** 个")
                if back_hit > 0: hit_parts.append(f"后区命中 **{back_hit}** 个")
                line += f" → ✅ **结果**: {' 和 '.join(hit_parts)}"
            else:
                line += " → ❌ **结果**: 未命中"
            model_lines.append(line)
        report_parts.append("\n".join(model_lines))

    return "\n\n".join(report_parts)