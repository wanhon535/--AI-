# file: _Dashboard.py
import streamlit as st
import pandas as pd
import base64  # 用于处理背景图片（如果需要的话）

# 确保从正确的位置导入我们最终确认的函数和类
from src.analysis.performance_analyzer import analyze_recommendation_performance, generate_performance_summary
from src.database.database_manager import DatabaseManager


# --- ✨ UI美化魔法函数 ✨ ---
# 这个函数就是实现渐变背景的核心
def set_gradient_background():
    """
    注入自定义CSS来实现页面的渐变背景。
    """
    # --- 你可以在这里自定义你喜欢的渐变色 ---
    color1 = "#1d2b64"  # 深邃的星空蓝
    color2 = "#f8cdda"  # 温柔的黎明粉
    # -----------------------------------------

    css_style = f"""
    <style>
    /* Streamlit 主背景 */
    .stApp {{
        background-image: linear-gradient(to bottom right, {color1}, {color2});
        background-attachment: fixed;
        background-size: cover;
    }}

    /* 侧边栏样式 */
    [data-testid="stSidebar"] > div:first-child {{
        background-color: rgba(255, 255, 255, 0.08); /* 增加一点玻璃拟态效果 */
        backdrop-filter: blur(5px); /* 毛玻璃效果 */
    }}

    /* 主内容区块的样式，让它也带一点透明感 */
    [data-testid="stBlockContainer"] {{
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 2rem;
    }}

    /* 让标题和文本颜色在深色背景下更清晰 */
    h1, h2, h3, h4, h5, h6, .stMarkdown, label {{
        color: #FFFFFF; /* 白色文字 */
    }}

    /* 美化按钮 */
    .stButton>button {{
        border: 2px solid #FFFFFF;
        border-radius: 20px;
        color: #FFFFFF;
        background-color: transparent;
    }}
    .stButton>button:hover {{
        border-color: #f8cdda;
        color: #f8cdda;
        background-color: rgba(255, 255, 255, 0.1);
    }}
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)


# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="Lotto-Pro 智能分析系统",
    page_icon="🔮",
    layout="wide"
)

# --- ✨ 调用UI美化函数！---
set_gradient_background()

# --- 2. 页面标题和简介 ---
st.title("🔮 Lotto-Pro 智能分析与推荐系统")
st.markdown("---", unsafe_allow_html=True)  # unsafe_allow_html 确保自定义样式能正确应用


# ... (后续的代码与之前的标准UI版本完全相同) ...

# 数据库操作的辅助函数
def fetch_latest_lottery_history(limit: int):
    db_manager = None
    try:
        db_manager = DatabaseManager(
            host='localhost', user='root', password='root',
            database='lottery_analysis_system', port=3307
        )
        if not db_manager.connect():
            st.sidebar.error("数据库连接失败")
            return []
        return db_manager.get_latest_lottery_history(limit)
    except Exception as e:
        st.sidebar.error(f"获取数据时出错: {e}")
        return []
    finally:
        if db_manager and db_manager.is_connected():
            db_manager.disconnect()


# 侧边栏：用户的输入控件
st.sidebar.header("⚙️ 分析控制台")

latest_history = fetch_latest_lottery_history(1)
default_period = ""
if latest_history:
    default_period = latest_history[0].period_number

selected_period = st.sidebar.text_input(
    "请输入要分析的期号:",
    value=default_period,
    help="输入一个有效的彩票期号，例如 '2025068'"
)

if st.sidebar.button("🚀 开始分析", use_container_width=True) and selected_period:
    st.header(f"📊 第 {selected_period} 期表现分析")
    with st.spinner("正在连接数据库并生成分析报告..."):
        analysis_data = analyze_recommendation_performance(selected_period)
    if "error" in analysis_data:
        st.error(f"❌ 分析失败: {analysis_data['error']}")
    else:
        summary_report = generate_performance_summary(analysis_data)
        st.markdown(summary_report, unsafe_allow_html=True)
        if analysis_data.get("analysis"):
            st.subheader("📋 推荐详情与命中情况")
            df_data = []
            for i, rec in enumerate(analysis_data["analysis"]):
                df_data.append({
                    "序号": i + 1,
                    "推荐前区": ', '.join(map(str, rec['recommended_front'])),
                    "推荐后区": ', '.join(map(str, rec['recommended_back'])),
                    "前区命中": f"{rec['front_hit_count']}个 ({', '.join(map(str, rec['front_hit_numbers'])) if rec['front_hit_numbers'] else '无'})",
                    "后区命中": f"{rec['back_hit_count']}个 ({', '.join(map(str, rec['back_hit_numbers'])) if rec['back_hit_numbers'] else '无'})",
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("本期没有找到任何推荐记录可供分析。")
else:
    st.info("👈 请在左侧输入期号并点击“开始分析”来查看结果。")

st.sidebar.markdown("---")
st.sidebar.header("📚 历史数据")
if st.sidebar.checkbox("显示最近10期开奖历史"):
    st.subheader("📜 最近10期开奖历史")
    history_data = fetch_latest_lottery_history(10)
    if history_data:
        history_df_data = [vars(h) for h in history_data]
        history_df = pd.DataFrame(history_df_data)
        st.dataframe(
            history_df[['period_number', 'draw_date', 'front_area', 'back_area']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("暂无历史开奖数据或获取失败。")