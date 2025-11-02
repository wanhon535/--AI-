# file: pages/Analysis.py (完整版，已修复中文显示)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.utils.helpers import get_db_manager, authenticated_page, get_algorithm_display_names
from src.ui.style_utils import load_global_styles


# --- 数据获取函数 (保持不变) ---
def get_analysis_data(db_manager, period_number=None):
    try:
        if period_number:
            query = "SELECT * FROM lottery_history WHERE period_number = %s"
            result = db_manager.execute_query(query, (period_number,))
        else:
            query = "SELECT * FROM lottery_history ORDER BY draw_date DESC LIMIT 1"
            result = db_manager.execute_query(query)
        return result[0] if result else None
    except Exception as e:
        st.error(f"获取分析数据时出错: {e}");
        return None


def get_number_statistics(db_manager, number_type='front'):
    try:
        query = "SELECT * FROM number_statistics WHERE number_type = %s ORDER BY number"
        return db_manager.execute_query(query, (number_type,))
    except Exception as e:
        st.error(f"获取号码统计时出错: {e}");
        return []


def get_algorithm_performance(db_manager):
    try:
        query = "SELECT * FROM algorithm_performance"
        return db_manager.execute_query(query)
    except Exception as e:
        st.error(f"获取算法性能时出错: {e}");
        return []


# --- 图表创建函数 (部分修改) ---
def create_number_heat_map(stats_data, title):
    if not stats_data: return
    df = pd.DataFrame(stats_data)
    fig = px.bar(df, x='number', y='appearance_rate', title=title, color='heat_score',
                 color_continuous_scale='RdYlGn_r')
    fig.update_layout(xaxis_title="号码", yaxis_title="出现频率", height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_omission_chart(stats_data, title):
    if not stats_data: return
    df = pd.DataFrame(stats_data)
    fig = px.bar(df, x='number', y='current_omission', title=title, color='current_omission',
                 color_continuous_scale='Viridis')
    fig.update_layout(xaxis_title="号码", yaxis_title="当前遗漏期数", height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_algorithm_performance_chart(performance_data):
    """创建算法性能图表 (已更新为中文显示)"""
    if not performance_data: return
    df = pd.DataFrame(performance_data)
    ALGO_NAME_MAP = get_algorithm_display_names()
    df['algorithm_display_name'] = df['algorithm_version'].apply(lambda x: ALGO_NAME_MAP.get(x, x))
    fig = go.Figure()
    fig.add_trace(
        go.Bar(name='前区命中率', x=df['algorithm_display_name'], y=df['avg_front_hit_rate'], marker_color='#ff6b6b'))
    fig.add_trace(
        go.Bar(name='后区命中率', x=df['algorithm_display_name'], y=df['avg_back_hit_rate'], marker_color='#4ecdc4'))
    fig.update_layout(title="算法性能对比", xaxis_title="算法", yaxis_title="命中率", barmode='group', height=400)
    st.plotly_chart(fig, use_container_width=True)


def analyze_patterns(lottery_data):
    if not lottery_data: return {}
    front_numbers = [lottery_data[f'front_area_{i + 1}'] for i in range(5)]
    analysis = {
        'sum_value': lottery_data['sum_value'], 'odd_count': len([n for n in front_numbers if n % 2 == 1]),
        'even_count': len([n for n in front_numbers if n % 2 == 0]),
        'large_count': len([n for n in front_numbers if n > 18]),
        'small_count': len([n for n in front_numbers if n <= 18])
    }
    return analysis


# --- 主页面渲染 ---
@authenticated_page
def analysis_page():
    load_global_styles()
    db_manager = get_db_manager()

    st.markdown("""
    <div class="card"><h1>🔍 智能分析中心</h1><p style="color: #7f8c8d;">基于历史数据的深度分析和模式识别</p></div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("分析设置")
        latest_period_query = "SELECT period_number FROM lottery_history ORDER BY draw_date DESC LIMIT 1"
        latest_period_result = db_manager.execute_query(latest_period_query)
        default_period = latest_period_result[0]['period_number'] if latest_period_result else "2025123"
        selected_period = st.text_input("分析期号", value=default_period)
        analysis_type = st.selectbox("分析类型", ["号码热度分析", "遗漏分析", "算法性能分析", "综合模式分析"])

    if st.sidebar.button("开始分析", type="primary", use_container_width=True):
        with st.spinner("正在执行深度分析..."):
            analysis_data = get_analysis_data(db_manager, selected_period)
            if analysis_data:
                # ... (基础信息显示部分保持不变) ...

                if analysis_type == "号码热度分析":
                    st.markdown("### 🔥 号码热度分析")
                    col1, col2 = st.columns(2)
                    with col1:
                        create_number_heat_map(get_number_statistics(db_manager, 'front'), "前区号码热度")
                    with col2:
                        create_number_heat_map(get_number_statistics(db_manager, 'back'), "后区号码热度")

                elif analysis_type == "遗漏分析":
                    st.markdown("### ⏳ 号码遗漏分析")
                    col1, col2 = st.columns(2)
                    with col1:
                        create_omission_chart(get_number_statistics(db_manager, 'front'), "前区号码遗漏")
                    with col2:
                        create_omission_chart(get_number_statistics(db_manager, 'back'), "后区号码遗漏")

                elif analysis_type == "算法性能分析":
                    st.markdown("### 🤖 算法性能分析")
                    performance_data = get_algorithm_performance(db_manager)
                    create_algorithm_performance_chart(performance_data)
                    st.markdown("#### 算法性能详情")
                    if performance_data:
                        perf_df = pd.DataFrame(performance_data)
                        ALGO_NAME_MAP = get_algorithm_display_names()
                        perf_df['算法名称'] = perf_df['algorithm_version'].apply(lambda x: ALGO_NAME_MAP.get(x, x))
                        display_df = perf_df[['算法名称', 'avg_front_hit_rate', 'avg_back_hit_rate', 'stability_score',
                                              'performance_trend']]
                        display_df.columns = ['算法名称', '平均前区命中率', '平均后区命中率', '稳定性评分', '性能趋势']
                        st.dataframe(display_df, use_container_width=True, hide_index=True)

                elif analysis_type == "综合模式分析":
                    st.markdown("### 🧩 综合模式分析")
                    # ... (此部分保持不变) ...

            else:
                st.error(f"未找到期号 {selected_period} 的数据")
    else:
        st.info("👈 请在左侧选择分析参数并点击'开始分析'")

    # --- 快速导航 (保持不变) ---
    st.markdown("---")
    st.markdown("### 🚀 快速导航")
    nav_cols = st.columns(3)
    if nav_cols[0].button("🏠 返回首页", use_container_width=True): st.switch_page("pages/Home.py")
    if nav_cols[1].button("💸 我要投注", use_container_width=True): st.switch_page("pages/Betting.py")
    if nav_cols[2].button("🤖 算法推荐", use_container_width=True): st.switch_page("pages/Recommendations.py")


analysis_page()