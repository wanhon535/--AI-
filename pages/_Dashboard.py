# file: _Dashboard.py (V5.2 - “柔和晨曦”全局风格最终版)

import streamlit as st
import pandas as pd
import time

# 导入您的模块
from src.database.database_manager import DatabaseManager
from src.analysis.performance_analyzer import analyze_recommendation_performance, generate_performance_summary
from src.ui.style_utils import load_global_styles

# 登录页面配置：

# --- 1. 页面配置与最终美学设计 ---


# st.set_page_config(page_title="Lotto-Pro 智能分析系统", page_icon="🎨", layout="wide")


from src.ui.style_utils import load_global_styles
def add_final_elegant_css():
    """
    注入最终优化的CSS，实现您喜欢的“柔和晨曦”风格，
    并确保它能【完全覆盖】包括侧边栏在内的所有区域。
    """
    st.markdown("""
    <style>
        /* --- 全局字体 --- */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&display=swap');
        html, body, [class*="st-"] { font-family: 'Noto Sans SC', sans-serif; }

        /* --- ✅ 核心修复：全局背景，覆盖所有区域 --- */
        .stApp {
            background-image: linear-gradient(to right top, #d1e4f5, #e3e0f7, #f3dff1, #fde0e8, #ffe3e3);
            background-attachment: fixed;
            background-size: cover;
        }

        /* --- ✅ 核心修复：精确定位并美化侧边栏 --- */
        [data-testid="stSidebar"] {
            /* 使用半透明白色叠加在渐变背景上，营造磨砂玻璃效果 */
            background-color: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* --- 卡片化布局 (与侧边栏风格统一) --- */
        .card {
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* --- 标题与文本 --- */
        h1, h2, h3 { color: #2c3e50; }

        /* --- Metric 指标卡 --- */
        [data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.9);
        }
    </style>
    """, unsafe_allow_html=True)


add_final_elegant_css()

#
# # --- 2. 数据库连接 (复用上一版的修复) ---
# @st.cache_resource
# def get_db_manager():
#     db = DatabaseManager(
#         host='localhost', user='root', password='123456789',  # ❗️ 请替换为您的密码
#         database='lottery_analysis_system', port=3309,
#         debug=True  # 保持调试模式开启
#     )
#     if db.connect(): return db
#     st.error("数据库连接失败！");
#     st.stop()
#
#
# db_manager = get_db_manager()
#
# # --- 3. 页面布局与最终逻辑 (使用 V5.1 的修复) ---
# st.title("🎨 Lotto-Pro 智能分析系统")
#
# tab1, tab2 = st.tabs(["📈 **智能分析复盘**", "💬 **AI聊天助手**"])
#
# with tab1:
#     st.sidebar.header("⚙️ 分析设置")
#     try:
#         default_period = db_manager.get_latest_lottery_history(1)[0].period_number
#     except:
#         default_period = "2025001"
#     selected_period = st.sidebar.text_input("输入要分析的期号", value=default_period)
#
#     if st.sidebar.button("🚀 开始分析", use_container_width=True, type="primary"):
#         with st.spinner("正在生成多维度分析报告..."):
#             # 使用修复后的、支持模型分组的分析函数
#             analysis_data = analyze_recommendation_performance(db_manager, selected_period)
#
#         # 指标卡
#         with st.container():
#             st.markdown(f'<div class="card"><h2>📊 第 {selected_period} 期 核心指标</h2></div>', unsafe_allow_html=True)
#             all_recs = [rec for model_recs in analysis_data.get("analysis_by_model", {}).values() for rec in model_recs]
#             if all_recs:
#                 best_hit = max(all_recs, key=lambda r: r.get('front_hit_count', 0) * 2 + r.get('back_hit_count', 0) * 5)
#                 col1, col2, col3 = st.columns(3)
#                 col1.metric("总推荐数", f"{len(all_recs)} 条")
#                 col2.metric("最佳前区命中", f"{best_hit.get('front_hit_count', 0)} 个")
#                 col3.metric("最佳后区命中", f"{best_hit.get('back_hit_count', 0)} 个")
#             else:
#                 st.metric("总推荐数", "0 条")
#
#         # 按模型分析详情
#         with st.container():
#             st.markdown('<div class="card"><h3>📝 按模型分析详情</h3></div>', unsafe_allow_html=True)
#             summary_report = generate_performance_summary(analysis_data)
#             st.markdown(summary_report)
#     else:
#         st.info("👈 请在左侧输入期号并点击“开始分析”。")
#
# with tab2:
#     st.markdown('<div class="card"><h2>💬 与 Lotto-Pro AI 助手对话</h2></div>', unsafe_allow_html=True)
#     if "messages" not in st.session_state:
#         st.session_state.messages = [{"role": "assistant", "content": "你好！我是Lotto-Pro AI助手。"}]
#     for msg in st.session_state.messages:
#         st.chat_message(msg["role"]).write(msg["content"])
#     if prompt := st.chat_input("在这里输入..."):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         st.chat_message("user").write(prompt)
#         response = f"模拟回复: {prompt}"
#         st.session_state.messages.append({"role": "assistant", "content": response})
#         st.chat_message("assistant").write(response)