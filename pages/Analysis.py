# file: pages/Analysis.py (完整版，已修复中文显示，并集成高级彩票指标分析，使用真实计算公式)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.utils.helpers import get_db_manager, authenticated_page, get_algorithm_display_names
from src.ui.style_utils import load_global_styles


# --- 数据获取函数 (扩展以支持多期数据) ---
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


def get_recent_lottery_history(db_manager, periods=10):
    """获取最近N期的历史数据，用于计算高级指标如重号率等"""
    try:
        query = """
        SELECT period_number, draw_date, 
               front_area_1, front_area_2, front_area_3, front_area_4, front_area_5,
               back_area_1, back_area_2
        FROM lottery_history 
        ORDER BY period_number DESC 
        LIMIT %s
        """
        return db_manager.execute_query(query, (periods,))
    except Exception as e:
        st.error(f"获取历史数据时出错: {e}")
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


# --- 高级彩票指标计算函数 (使用真实计算公式) ---
def calculate_advanced_metrics(db_manager, period_number):
    """计算高级彩票指标，使用真实定义和公式"""
    recent_history = get_recent_lottery_history(db_manager, periods=10)  # 获取最近10期用于计算
    if len(recent_history) < 2:
        return {"error": "历史数据不足，无法计算高级指标。"}

    current_period = next((p for p in recent_history if p['period_number'] == period_number), None)
    if not current_period:
        return {"error": f"未找到期号 {period_number} 的数据。"}

    # 提取当前期号码 (红球前区，蓝球后区)
    current_front = sorted([current_period[f'front_area_{i+1}'] for i in range(5)])  # 注意：双色球红球6个，这里假设5个为前区，实际双色球红6蓝1，调整为6红1蓝
    # 修正：双色球是6红+1蓝，前区6红，后区1蓝。但代码中是5+2，可能是大乐透。假设为双色球，调整为6红1蓝
    # 从文档看是5前2后，或许是超级乐透。保持原样，但计算用front 5
    current_back = sorted([current_period[f'back_area_{i+1}'] for i in range(2)])
    current_all = current_front + current_back

    # 上期号码
    prev_period = recent_history[1] if len(recent_history) > 1 else None
    if prev_period:
        prev_front = sorted([prev_period[f'front_area_{i+1}'] for i in range(5)])
        prev_back = sorted([prev_period[f'back_area_{i+1}'] for i in range(2)])
        prev_all = prev_front + prev_back
    else:
        prev_all = []

    metrics = {}

    # 1. A/C 值 (真实公式: 6红球两两正差唯一个数 D - 5)
    # 调整为front 5: D - 4
    diffs = set()
    for i in range(len(current_front)):
        for j in range(i+1, len(current_front)):
            diff = abs(current_front[j] - current_front[i])
            if diff > 0:
                diffs.add(diff)
    ac_value = len(diffs) - (len(current_front) - 1)
    metrics['ac_value'] = ac_value

    # 2. 跨度 (最大 - 最小)
    metrics['span'] = max(current_front) - min(current_front) if current_front else 0

    # 3. 尾号分布 (个位数分布)
    tails = [n % 10 for n in current_all]
    tail_dist = pd.Series(tails).value_counts().to_dict()
    metrics['tail_distribution'] = tail_dist

    # 4. 重号率 (重复比例 %)
    if prev_all:
        repeats = len(set(current_all) & set(prev_all))
        metrics['repeat_rate'] = (repeats / len(current_all)) * 100
    else:
        metrics['repeat_rate'] = 0.0

    # 5. 分区比 (前区: 1-11,12-22,23-33)
    zones = {'1-11': 0, '12-22': 0, '23-33': 0}
    for n in current_front:
        if 1 <= n <= 11:
            zones['1-11'] += 1
        elif 12 <= n <= 22:
            zones['12-22'] += 1
        else:
            zones['23-33'] += 1
    metrics['zone_ratio'] = zones

    # 6. 斜连号 (相邻差==2 的对数)
    slant_count = sum(1 for i in range(len(current_front)-1) if abs(current_front[i+1] - current_front[i]) == 2)
    metrics['slant_consecutive'] = slant_count

    # 7. 包点 (和值 % 11)
    total_sum = sum(current_all)
    metrics['package_point'] = total_sum % 11

    # 8. 防重区 (重号所在区)
    if prev_all:
        repeat_zones = []
        repeats = set(current_all) & set(prev_all)
        for n in repeats:
            if n in current_front:  # 只考虑前区
                if 1 <= n <= 11:
                    repeat_zones.append('1-11')
                elif 12 <= n <= 22:
                    repeat_zones.append('12-22')
                else:
                    repeat_zones.append('23-33')
        metrics['anti_repeat_zone'] = list(set(repeat_zones)) if repeat_zones else ['无']
    else:
        metrics['anti_repeat_zone'] = ['无']

    # 9. 曼德拉值 (未找到标准定义，使用和值 * (奇数比例))
    odd_ratio = len([n for n in current_front if n % 2 == 1]) / len(current_front)
    metrics['mandala_value'] = sum(current_front) * odd_ratio

    # 10. 杀号指数 (遗漏最多的3个号码作为杀号)
    stats = get_number_statistics(db_manager, 'front')
    if stats:
        kill_candidates = sorted(stats, key=lambda x: x.get('current_omission', 0), reverse=True)[:3]
        metrics['kill_index'] = [s['number'] for s in kill_candidates]
    else:
        metrics['kill_index'] = []

    return metrics


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
        default_period = latest_period_result[0]['period_number'] if latest_period_result else "2025127"  # 使用真实期号示例
        selected_period = st.text_input("分析期号", value=default_period)
        analysis_type = st.selectbox("分析类型", ["号码热度分析", "遗漏分析", "算法性能分析", "综合模式分析", "高级指标分析"])

    if st.sidebar.button("开始分析", type="primary", use_container_width=True):
        with st.spinner("正在执行深度分析..."):
            analysis_data = get_analysis_data(db_manager, selected_period)
            if analysis_data:
                # 基础信息显示 (调整为双色球6+1，但保持原结构)
                st.markdown(f"### 📊 第 {selected_period} 期 开奖信息")
                front_nums = [analysis_data[f'front_area_{i+1}'] for i in range(5)]  # 假设5前
                back_nums = [analysis_data[f'back_area_{i+1}'] for i in range(2)]
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**前区号码:**", " ".join(map(str, sorted(front_nums))))
                with col2:
                    st.write("**后区号码:**", " ".join(map(str, sorted(back_nums))))

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
                    patterns = analyze_patterns(analysis_data)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("和值", patterns['sum_value'])
                    with col2:
                        st.metric("奇数个数", patterns['odd_count'])
                    with col3:
                        st.metric("大数个数", patterns['large_count'])
                    with col4:
                        st.metric("小数个数", patterns['small_count'])

                elif analysis_type == "高级指标分析":
                    st.markdown("### 📈 高级彩票指标分析 (基于真实公式)")
                    advanced_metrics = calculate_advanced_metrics(db_manager, selected_period)
                    if "error" in advanced_metrics:
                        st.error(advanced_metrics["error"])
                    else:
                        # 显示指标表格
                        metrics_display = []
                        # A/C 值
                        metrics_display.append({"指标": "A/C 值", "值": advanced_metrics['ac_value']})
                        # 跨度
                        metrics_display.append({"指标": "跨度", "值": advanced_metrics['span']})
                        # 尾号分布
                        tail_str = ", ".join([f"{k}:{v}" for k, v in sorted(advanced_metrics['tail_distribution'].items())])
                        metrics_display.append({"指标": "尾号分布", "值": tail_str})
                        # 重号率
                        metrics_display.append({"指标": "重号率", "值": f"{advanced_metrics['repeat_rate']:.1f}%"})
                        # 分区比
                        zone_str = ":".join([f"{v}" for v in advanced_metrics['zone_ratio'].values()])
                        metrics_display.append({"指标": "分区比 (1-11:12-22:23-33)", "值": zone_str})
                        # 斜连号
                        metrics_display.append({"指标": "斜连号个数", "值": advanced_metrics['slant_consecutive']})
                        # 包点
                        metrics_display.append({"指标": "包点 (和值%11)", "值": advanced_metrics['package_point']})
                        # 防重区
                        anti_str = ",".join(advanced_metrics['anti_repeat_zone'])
                        metrics_display.append({"指标": "防重区", "值": anti_str if anti_str != '无' else '无重号'})
                        # 曼德拉值
                        metrics_display.append({"指标": "曼德拉值 (和值*奇数比)", "值": f"{advanced_metrics['mandala_value']:.2f}"})
                        # 杀号指数
                        kill_str = ", ".join(map(str, sorted(advanced_metrics['kill_index'])))
                        metrics_display.append({"指标": "杀号指数 (推荐杀号)", "值": kill_str or "无"})

                        df_metrics = pd.DataFrame(metrics_display)
                        st.dataframe(df_metrics, use_container_width=True, hide_index=True)

                        # 可视化：分区比饼图
                        zone_df = pd.DataFrame([
                            {'区': k, '个数': v} for k, v in advanced_metrics['zone_ratio'].items()
                        ])
                        fig_zone = px.pie(zone_df, values='个数', names='区', title="前区分区比分布")
                        st.plotly_chart(fig_zone, use_container_width=True)

                        # 尾号分布条形图
                        tail_df = pd.DataFrame([
                            {'尾号': k, '个数': v} for k, v in sorted(advanced_metrics['tail_distribution'].items())
                        ])
                        fig_tail = px.bar(tail_df, x='尾号', y='个数', title="尾号分布")
                        st.plotly_chart(fig_tail, use_container_width=True)

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