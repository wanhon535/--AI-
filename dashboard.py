# file: dashboard.py
import streamlit as st
import pandas as pd
# 假设数据库管理器和分析函数可以被导入
from src.database.database_manager import DatabaseManager
from src.analysis.performance_analyzer import analyze_recommendation_performance, generate_performance_summary

# --- 页面配置 ---
st.set_page_config(page_title="Lotto-Pro 智能分析系统", layout="wide")

st.title("🔮 Lotto-Pro 智能分析与推荐系统")


# --- 初始化数据库连接 (Streamlit 会缓存这个对象) ---
def get_db_manager():
    db = DatabaseManager(
        host='localhost', user='root', password='root',
        database='lottery_analysis_system', port=3307
    )
    db.connect()
    return db


db_manager = get_db_manager()

# --- 侧边栏 ---
st.sidebar.header("功能选择")
selected_period = st.sidebar.text_input("输入要分析的期号",
                                        value=db_manager.get_latest_lottery_history(1)[0].period_number)

if st.sidebar.button("开始分析"):
    # --- 主内容区 ---
    st.header(f"📊 第 {selected_period} 期表现分析")

    # 1. 获取并展示分析报告
    with st.spinner("正在生成分析报告..."):
        analysis_data = analyze_recommendation_performance(selected_period)
        summary_report = generate_performance_summary(analysis_data)

    st.markdown(summary_report)

    # 2. 展示详细的推荐与命中数据
    if "analysis" in analysis_data and analysis_data["analysis"]:
        st.subheader("推荐详情与命中情况")

        # 将分析结果转换为 DataFrame 以便用 st.dataframe 展示
        df_data = []
        for rec in analysis_data["analysis"]:
            df_data.append({
                "推荐前区": ', '.join(map(str, rec['recommended_front'])),
                "推荐后区": ', '.join(map(str, rec['recommended_back'])),
                "前区命中": f"{rec['front_hit_count']}个 ({', '.join(map(str, rec['front_hit_numbers'])) if rec['front_hit_numbers'] else '无'})",
                "后区命中": f"{rec['back_hit_count']}个 ({', '.join(map(str, rec['back_hit_numbers'])) if rec['back_hit_numbers'] else '无'})",
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

else:
    st.info("👈 请在左侧输入期号并点击“开始分析”来查看结果。")

# --- 你还可以在这里添加更多功能，比如历史数据查询、图表展示等 ---
st.sidebar.header("其他功能")
if st.sidebar.checkbox("显示最近10期开奖历史"):
    st.subheader("最近10期开奖历史")
    history_data = db_manager.get_latest_lottery_history(10)
    history_df = pd.DataFrame([vars(h) for h in history_data])
    st.dataframe(history_df[['period_number', 'front_area', 'back_area', 'sum_value']], use_container_width=True)