# src/ai_caller.py (Refactored)

from src.database.database_manager import DatabaseManager
from src.prompt_templates import build_lotto_pro_prompt
from src.llm.clients import get_llm_client  # ⬅️ 关键导入：从新模块获取工厂函数
from src.test import parse_ai_recommendations


# ... (保留 parse_ai_recommendations 和其他辅助函数)

def main():
    # ... (数据库连接和数据准备部分保持不变)
    db_manager = ...
    db_manager.connect()

    recent_draws = db_manager.get_latest_lottery_history(50)
    user_bets = db_manager.get_user_bets('default', 20)
    next_issue = db_manager.get_next_period_number()

    PROMPT_TEMPLATE_CONTENT, _ = build_lotto_pro_prompt(...)
    USER_QUERY = "帮我预测分析下一期的彩票号码"

    # --- 多模型调用循环 ---
    models_to_run = ["gemini-1.5-pro", "qwen3-max"]  # 选择要运行的模型

    for model_name in models_to_run:
        print(f"\n🚀 Processing with model: {model_name}")
        try:
            # 1. 使用工厂函数获取正确的客户端实例
            llm_client = get_llm_client(model_name)

            # 2. 调用统一的 generate 方法
            response_content = llm_client.generate(PROMPT_TEMPLATE_CONTENT, USER_QUERY)

            # 3. 后续处理（解析、存入数据库等）
            recommendations = parse_ai_recommendations(response_content)
            if recommendations:
                print(f"✅ Parsed {len(recommendations)} recommendations from {model_name}.")
                # ... 在此处编写将结果存入数据库的逻辑 ...
                db_manager.insert_algorithm_recommendation_root(
                    period_number=next_issue,
                    model_name=model_name,  # 动态传入模型名称

                )
            else:
                print(f"⚠️ Could not parse recommendations from {model_name}.")

        except Exception as e:
            print(f"❌ An error occurred while processing {model_name}: {e}")

    # ... (关闭数据库连接)
    db_manager.disconnect()


if __name__ == "__main__":
    main()