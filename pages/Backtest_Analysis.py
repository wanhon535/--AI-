# file: pages/Backtest_Analysis.py (完整版，已修复中文显示)
import streamlit as st
import pandas as pd
import json
from src.utils.helpers import get_db_manager, authenticated_page, get_algorithm_display_names
from src.ui.style_utils import load_global_styles


@st.cache_data(ttl=600)
def load_backtest_data(_db_manager):
    """一次性加载所有需要的回测数据"""
    # ❗️注意: 'algorithm_prediction_logs' 表在您的数据库文档中不存在。
    # 此处假设该表存在。如果不存在，此页面将无法加载数据。
    try:
        periods_raw = _db_manager.execute_query(
            "SELECT DISTINCT period_number FROM algorithm_prediction_logs ORDER BY period_number DESC")
        periods = [p['period_number'] for p in periods_raw] if periods_raw else []

        performance_raw = _db_manager.execute_query("SELECT * FROM algorithm_performance")
        performance_df = pd.DataFrame(performance_raw) if performance_raw else pd.DataFrame()

        return periods, performance_df
    except Exception as e:
        # 如果表不存在，数据库会抛出异常，我们在这里捕获它
        st.error(f"加载回测数据时出错: {e}")
        st.warning("这通常是因为 'algorithm_prediction_logs' 表不存在。请检查您的数据库结构或运行必要的回测脚本。")
        return [], pd.DataFrame()


@authenticated_page
def backtest_analysis_page():
    load_global_styles()
    db_manager = get_db_manager()
    ALGO_NAME_MAP = get_algorithm_display_names()

    st.markdown("""
    <div class="card">
        <h1>🔬 历史回测分析</h1>
        <p style="color: #7f8c8d;">深入分析和验证每个算法在任意历史期数的具体表现</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("正在加载回测数据..."):
        available_periods, performance_df = load_backtest_data(db_manager)

    # 如果没有期数数据，可能是因为表不存在或为空
    if not available_periods:
        st.info("系统中当前没有可供分析的回测数据。")
        st.stop()

    # --- 核心功能 1: 算法长期性能总览 ---
    st.markdown("### 📈 算法长期性能总览")
    if not performance_df.empty:
        df_display = performance_df.copy()
        df_display['算法名称'] = df_display['algorithm_version'].apply(lambda x: ALGO_NAME_MAP.get(x, x))

        format_dict = {'avg_front_hit_rate': '{:.2%}', 'avg_back_hit_rate': '{:.2%}', 'current_weight': '{:.3f}'}
        display_cols = {
            '算法名称': '算法名称', 'total_periods_analyzed': '分析期数', 'avg_front_hit_rate': '前区平均命中',
            'avg_back_hit_rate': '后区平均命中', 'current_weight': '当前权重', 'performance_trend': '性能趋势'
        }

        # 筛选出实际存在的列进行显示
        cols_to_show = [col for col in display_cols.keys() if col in df_display.columns]
        df_to_show = df_display[cols_to_show]
        df_to_show = df_to_show.rename(columns=display_cols)

        st.dataframe(df_to_show.style.format(format_dict), use_container_width=True, hide_index=True)
    else:
        st.warning("`algorithm_performance` 表为空，无法显示长期性能。")

    # --- 核心功能 2: 单期预测结果追溯 ---
    st.markdown("### 🎯 单期预测结果追溯")
    selected_period = st.selectbox("请选择要分析的历史期号:", options=available_periods)

    if selected_period:
        actual_draw_raw = db_manager.execute_query("SELECT * FROM lottery_history WHERE period_number = %s",
                                                   (selected_period,))
        prediction_logs = db_manager.execute_query("SELECT * FROM algorithm_prediction_logs WHERE period_number = %s",
                                                   (selected_period,))

        if not actual_draw_raw:
            st.error(f"找不到第 {selected_period} 期的开奖数据。")
        elif not prediction_logs:
            st.warning(f"在第 {selected_period} 期没有找到任何算法的预测记录。")
        else:
            actual_draw = actual_draw_raw[0]
            actual_front = {actual_draw[f'front_area_{i + 1}'] for i in range(5)}
            actual_back = {actual_draw[f'back_area_{i + 1}'] for i in range(2)}

            st.metric("当期开奖号码",
                      f"🔴 {' '.join(map(str, sorted(list(actual_front))))}   🔵 {' '.join(map(str, sorted(list(actual_back))))}")
            st.write("---")

            for log in prediction_logs:
                algo_version = log['algorithm_version']
                display_name = ALGO_NAME_MAP.get(algo_version, algo_version)
                try:
                    predictions = json.loads(log['predictions'])
                    # 适应可能不存在 'recommendations' 键的情况
                    primary_rec = predictions.get('recommendations', [{}])[0] if predictions.get(
                        'recommendations') else {}
                    pred_front = primary_rec.get('front_numbers', [])
                    pred_back = primary_rec.get('back_numbers', [])
                    front_hits = len(set(pred_front) & actual_front)
                    back_hits = len(set(pred_back) & actual_back)

                    with st.expander(f"**{display_name}** | 命中: 🔴 {front_hits}/5 + 🔵 {back_hits}/2"):
                        def highlight_numbers(predicted, actual):
                            return [f"**<font color='green'>{n}</font>**" if n in actual else str(n) for n in predicted]

                        front_display = ", ".join(highlight_numbers(pred_front, actual_front))
                        back_display = ", ".join(highlight_numbers(pred_back, actual_back))
                        st.markdown(f"**预测:** {front_display} + {back_display}", unsafe_allow_html=True)
                        with st.popover("查看原始数据"):
                            st.json(predictions)
                except Exception as e:
                    st.error(f"解析【{display_name}】的预测数据时出错: {e}")


backtest_analysis_page()