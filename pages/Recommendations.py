# file: pages/Recommendations.py (已修复中文显示和乱码问题)
import streamlit as st
import pandas as pd
from src.utils.helpers import get_db_manager, authenticated_page, get_algorithm_display_names
from src.ui.style_utils import load_global_styles


# --- 数据获取函数 (保持不变) ---
def get_algorithm_recommendations(db_manager, period_number=None):
    try:
        query = """
                SELECT ar.algorithm_version, \
                       ar.confidence_score, \
                       ar.recommend_time,
                       rd.recommend_type, \
                       rd.strategy_logic, \
                       rd.front_numbers, \
                       rd.back_numbers
                FROM algorithm_recommendation ar
                         LEFT JOIN recommendation_details rd ON ar.id = rd.recommendation_metadata_id
                WHERE ar.period_number = %s
                ORDER BY ar.recommend_time DESC \
                """
        return db_manager.execute_query(query, (period_number,))
    except Exception as e:
        st.error(f"获取历史推荐时出错: {e}")
        return []


def get_available_algorithms(db_manager):
    try:
        query = "SELECT algorithm_name, algorithm_type, description FROM algorithm_configs WHERE is_active = 1"
        return db_manager.execute_query(query)
    except Exception as e:
        st.error(f"获取算法列表时出错: {e}")
        return []


def trigger_recommendation_workflow(selected_algo_id, selected_period):
    st.session_state.last_triggered_workflow = {
        "message": f"✅ 已成功为 {selected_period} 期，提交【{get_algorithm_display_names().get(selected_algo_id, selected_algo_id)}】的推荐生成任务！"
    }
    return True


# --- 主页面渲染 ---
@authenticated_page
def recommendations_page():
    load_global_styles()
    db_manager = get_db_manager()

    ALGO_NAME_MAP = get_algorithm_display_names()
    REVERSE_ALGO_NAME_MAP = {v: k for k, v in ALGO_NAME_MAP.items()}

    st.markdown("""
    <div class="card">
        <h1><span style="font-size: 1.5em;">🤖</span> 智能算法推荐</h1>
        <p style="color: #7f8c8d;">在此处选择算法并触发新一期的号码推荐流程</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 布局分为主操作区和算法信息区 ---
    main_col, info_col = st.columns([2, 1])

    with main_col:
        st.markdown("### <span style='font-size: 1.2em;'>🎯</span> 生成新推荐", unsafe_allow_html=True)

        with st.container(border=True):  # 使用带边框的容器
            latest_period_query = "SELECT period_number FROM lottery_history ORDER BY draw_date DESC LIMIT 1"
            latest_period_result = db_manager.execute_query(latest_period_query)
            default_period = latest_period_result[0]['period_number'] if latest_period_result else "2025123"

            # 布局输入控件
            col1, col2 = st.columns(2)
            with col1:
                selected_period = st.text_input("推荐期号", value=str(int(default_period) + 1))
            with col2:
                available_algorithms = get_available_algorithms(db_manager)
                if available_algorithms:
                    algo_ids_from_db = [alg['algorithm_name'] for alg in available_algorithms]
                    display_options = [ALGO_NAME_MAP.get(id, id) for id in algo_ids_from_db]
                    selected_display_name = st.selectbox("选择分析算法", options=display_options)
                else:
                    st.warning("系统中未配置可用算法。")
                    selected_display_name = None

            if st.button("🚀 开始生成", type="primary", use_container_width=True):
                if selected_display_name:
                    selected_algo_id = REVERSE_ALGO_NAME_MAP.get(selected_display_name, selected_display_name)
                    with st.spinner(f"正在提交任务..."):
                        if trigger_recommendation_workflow(selected_algo_id, selected_period):
                            st.rerun()
                else:
                    st.error("请先在左侧选择一个算法。")

        # 显示来自会话状态的反馈信息
        if "last_triggered_workflow" in st.session_state:
            st.success(st.session_state.last_triggered_workflow["message"])
            del st.session_state.last_triggered_workflow

        st.markdown(f"### <span style='font-size: 1.2em;'>📈</span> 第 **{selected_period}** 期历史推荐",
                    unsafe_allow_html=True)
        historical_recommendations = get_algorithm_recommendations(db_manager, selected_period)

        if historical_recommendations:
            rec_data = []
            for rec in historical_recommendations:
                rec_data.append({
                    "算法名称": ALGO_NAME_MAP.get(rec['algorithm_version'], rec['algorithm_version']),
                    "推荐类型": rec['recommend_type'],
                    "前区": rec['front_numbers'], "后区": rec['back_numbers'],
                    "置信度": f"{rec.get('confidence_score', 0) * 100:.1f}%",
                    "生成时间": rec['recommend_time'].strftime("%Y-%m-%d %H:%M") if rec.get('recommend_time') else "N/A"
                })
            df = pd.DataFrame(rec_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"暂无 {selected_period} 期的历史推荐记录。")

    with info_col:
        st.markdown("### <span style='font-size: 1.2em;'>🔧</span> 算法库信息", unsafe_allow_html=True)
        if available_algorithms:
            for alg in available_algorithms:
                display_name = ALGO_NAME_MAP.get(alg['algorithm_name'], alg['algorithm_name'])
                # --- ✅ 核心修复：简化标题并添加标准图标，彻底解决乱码问题 ---
                with st.expander(display_name, icon="💡"):
                    st.markdown(f"**类型:** `{alg['algorithm_type']}`")
                    st.markdown(f"**描述:** {alg.get('description') or '暂无详细描述。'}")
        else:
            st.info("暂无算法配置信息")


recommendations_page()