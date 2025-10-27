# 智能分析
# file: pages/Analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.database.database_manager import DatabaseManager
from src.ui.style_utils import load_global_styles


def get_analysis_data(db_manager, period_number=None):
    """获取分析数据"""
    try:
        # 获取最新开奖数据
        if period_number:
            query = """
            SELECT * FROM lottery_history 
            WHERE period_number = %s
            """
            result = db_manager.execute_query(query, (period_number,))
        else:
            query = """
            SELECT * FROM lottery_history 
            ORDER BY draw_date DESC 
            LIMIT 1
            """
            result = db_manager.execute_query(query)

        return result[0] if result else None
    except Exception as e:
        st.error(f"获取分析数据时出错: {e}")
        return None


def get_number_statistics(db_manager, number_type='front'):
    """获取号码统计信息"""
    try:
        query = """
        SELECT number, total_appearances, appearance_rate, current_omission, 
               max_omission, heat_status, heat_score
        FROM number_statistics 
        WHERE number_type = %s
        ORDER BY number
        """
        results = db_manager.execute_query(query, (number_type,))
        return results
    except Exception as e:
        st.error(f"获取号码统计时出错: {e}")
        return []


def get_algorithm_performance(db_manager):
    """获取算法性能数据"""
    try:
        query = "SELECT * FROM algorithm_performance"
        results = db_manager.execute_query(query)
        return results
    except Exception as e:
        st.error(f"获取算法性能时出错: {e}")
        return []


def create_number_heat_map(stats_data, title):
    """创建号码热力图"""
    if not stats_data:
        return

    df = pd.DataFrame(stats_data)
    fig = px.bar(
        df,
        x='number',
        y='appearance_rate',
        title=title,
        color='heat_score',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(
        xaxis_title="号码",
        yaxis_title="出现频率",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def create_omission_chart(stats_data, title):
    """创建遗漏图表"""
    if not stats_data:
        return

    df = pd.DataFrame(stats_data)
    fig = px.bar(
        df,
        x='number',
        y='current_omission',
        title=title,
        color='current_omission',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        xaxis_title="号码",
        yaxis_title="当前遗漏期数",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def create_algorithm_performance_chart(performance_data):
    """创建算法性能图表"""
    if not performance_data:
        return

    df = pd.DataFrame(performance_data)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='前区命中率',
        x=df['algorithm_version'],
        y=df['avg_front_hit_rate'],
        marker_color='#ff6b6b'
    ))

    fig.add_trace(go.Bar(
        name='后区命中率',
        x=df['algorithm_version'],
        y=df['avg_back_hit_rate'],
        marker_color='#4ecdc4'
    ))

    fig.update_layout(
        title="算法性能对比",
        xaxis_title="算法版本",
        yaxis_title="命中率",
        barmode='group',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def analyze_patterns(lottery_data):
    """分析号码模式"""
    if not lottery_data:
        return {}

    # 基础分析
    front_numbers = [
        lottery_data['front_area_1'],
        lottery_data['front_area_2'],
        lottery_data['front_area_3'],
        lottery_data['front_area_4'],
        lottery_data['front_area_5']
    ]

    back_numbers = [
        lottery_data['back_area_1'],
        lottery_data['back_area_2']
    ]

    analysis = {
        'front_numbers': sorted(front_numbers),
        'back_numbers': sorted(back_numbers),
        'sum_value': lottery_data['sum_value'],
        'span_value': max(front_numbers) - min(front_numbers),
        'odd_count': len([n for n in front_numbers if n % 2 == 1]),
        'even_count': len([n for n in front_numbers if n % 2 == 0]),
        'large_count': len([n for n in front_numbers if n > 18]),
        'small_count': len([n for n in front_numbers if n <= 18])
    }

    return analysis


def analysis_page():
    """智能分析页面"""
    # 检查登录状态
    if not st.session_state.get("logged_in", False):
        st.warning("请先登录系统")
        st.switch_page("pages/Login.py")
        return

    load_global_styles()

    # 页面标题
    st.markdown("""
    <div class="card">
        <h1>🔍 智能分析中心</h1>
        <p style="color: #7f8c8d;">基于历史数据的深度分析和模式识别</p>
    </div>
    """, unsafe_allow_html=True)

    # 数据库连接
    try:
        db_manager = DatabaseManager(
            host='localhost', user='root', password='123456789',
            database='lottery_analysis_system', port=3309
        )
        if not db_manager.connect():
            st.error("数据库连接失败")
            return
    except Exception as e:
        st.error(f"数据库连接错误: {e}")
        return

    try:
        # 侧边栏控制
        st.sidebar.header("分析设置")

        # 期号选择
        latest_period_query = "SELECT period_number FROM lottery_history ORDER BY draw_date DESC LIMIT 1"
        latest_period_result = db_manager.execute_query(latest_period_query)
        default_period = latest_period_result[0]['period_number'] if latest_period_result else "2025001"

        selected_period = st.sidebar.text_input("分析期号", value=default_period)

        analysis_type = st.sidebar.selectbox(
            "分析类型",
            ["号码热度分析", "遗漏分析", "算法性能分析", "综合模式分析"]
        )

        # 主内容区
        if st.sidebar.button("开始分析", type="primary", use_container_width=True):
            with st.spinner("正在执行深度分析..."):
                # 获取分析数据
                analysis_data = get_analysis_data(db_manager, selected_period)

                if analysis_data:
                    # 显示基本信息
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 📊 基础信息")
                        st.info(f"**期号:** {analysis_data['period_number']}")
                        st.info(f"**开奖日期:** {analysis_data['draw_date']}")
                        st.info(f"**和值:** {analysis_data['sum_value']}")
                        st.info(f"**跨度:** {analysis_data['span_value']}")

                    with col2:
                        st.markdown("### 🎯 号码分布")
                        st.success(
                            f"**前区:** {analysis_data['front_area_1']}, {analysis_data['front_area_2']}, {analysis_data['front_area_3']}, {analysis_data['front_area_4']}, {analysis_data['front_area_5']}")
                        st.success(f"**后区:** {analysis_data['back_area_1']}, {analysis_data['back_area_2']}")
                        st.success(f"**奇偶比:** {analysis_data['odd_even_ratio']}")
                        st.success(f"**大小比:** {analysis_data['size_ratio']}")

                    # 根据选择的分析类型显示不同内容
                    if analysis_type == "号码热度分析":
                        st.markdown("### 🔥 号码热度分析")

                        col1, col2 = st.columns(2)

                        with col1:
                            front_stats = get_number_statistics(db_manager, 'front')
                            create_number_heat_map(front_stats, "前区号码热度")

                        with col2:
                            back_stats = get_number_statistics(db_manager, 'back')
                            create_number_heat_map(back_stats, "后区号码热度")

                    elif analysis_type == "遗漏分析":
                        st.markdown("### ⏳ 号码遗漏分析")

                        col1, col2 = st.columns(2)

                        with col1:
                            front_stats = get_number_statistics(db_manager, 'front')
                            create_omission_chart(front_stats, "前区号码遗漏")

                        with col2:
                            back_stats = get_number_statistics(db_manager, 'back')
                            create_omission_chart(back_stats, "后区号码遗漏")

                    elif analysis_type == "算法性能分析":
                        st.markdown("### 🤖 算法性能分析")

                        performance_data = get_algorithm_performance(db_manager)
                        create_algorithm_performance_chart(performance_data)

                        # 算法详情表格
                        st.markdown("#### 算法性能详情")
                        if performance_data:
                            perf_df = pd.DataFrame(performance_data)
                            st.dataframe(perf_df[['algorithm_version', 'avg_front_hit_rate', 'avg_back_hit_rate',
                                                  'stability_score', 'performance_trend']],
                                         use_container_width=True)

                    elif analysis_type == "综合模式分析":
                        st.markdown("### 🧩 综合模式分析")

                        patterns = analyze_patterns(analysis_data)

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("奇偶比例", f"{patterns['odd_count']}:{patterns['even_count']}")
                            st.metric("大小比例", f"{patterns['large_count']}:{patterns['small_count']}")

                        with col2:
                            st.metric("号码和值", patterns['sum_value'])
                            st.metric("号码跨度", patterns['span_value'])

                        with col3:
                            st.metric("前区号码", " ".join(map(str, patterns['front_numbers'])))
                            st.metric("后区号码", " ".join(map(str, patterns['back_numbers'])))

                        # 号码分布图
                        st.markdown("#### 号码分布热图")
                        all_numbers = patterns['front_numbers'] + patterns['back_numbers']
                        number_df = pd.DataFrame({
                            'number': all_numbers,
                            'type': ['前区'] * 5 + ['后区'] * 2,
                            'value': [1] * 7
                        })

                        fig = px.scatter(
                            number_df,
                            x='number',
                            y='type',
                            size='value',
                            color='type',
                            title="号码分布"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                else:
                    st.error(f"未找到期号 {selected_period} 的数据")

        else:
            st.info("👈 请在左侧选择分析参数并点击'开始分析'")

        # 快速导航
        st.markdown("---")
        st.markdown("### 🚀 快速导航")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 返回首页", use_container_width=True):
                st.switch_page("pages/Home.py")
        with col2:
            if st.button("💸 我要投注", use_container_width=True):
                st.switch_page("pages/Betting.py")
        with col3:
            if st.button("🤖 算法推荐", use_container_width=True):
                st.switch_page("pages/Recommendations.py")

    except Exception as e:
        st.error(f"分析过程出错: {e}")
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    analysis_page()
else:
    analysis_page()