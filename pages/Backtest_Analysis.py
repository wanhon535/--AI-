# pages/Backtest_Analysis.py
import streamlit as st
import pandas as pd
import json
from src.utils.helpers import get_db_manager, authenticated_page, get_algorithm_display_names
from src.ui.style_utils import load_global_styles


@st.cache_data(ttl=600)
def load_all_periods(_db_manager):
    """
    使用 algorithm_recommendation 表作为期号来源
    """
    raw = _db_manager.execute_query(
        "SELECT DISTINCT period_number FROM algorithm_recommendation ORDER BY period_number DESC"
    )
    return [row["period_number"] for row in raw] if raw else []


@st.cache_data(ttl=300)
def load_recommendations_and_details(_db_manager, period_number):
    """
    核心：一次性加载该期的 algorithm_recommendation 和 recommendation_details 到内存
    返回：
      - algo_recs: list of recommendation meta dicts
      - details_map: dict mapping recommendation_metadata_id -> list of detail dicts
    """
    # 1) 加载元数据
    algo_recs = _db_manager.execute_query(
        """
        SELECT * FROM algorithm_recommendation
        WHERE period_number = %s
        ORDER BY algorithm_version ASC, created_at ASC
        """,
        (period_number,)
    ) or []

    if not algo_recs:
        return [], {}

    # 收集所有元数据 id
    meta_ids = [meta["id"] for meta in algo_recs]

    # 2) 批量查询 recommendation_details（使用 IN 子句）
    # 防止 meta_ids 为空（已经检查过非空）
    placeholders = ",".join(["%s"] * len(meta_ids))
    sql = f"""
        SELECT * FROM recommendation_details
        WHERE recommendation_metadata_id IN ({placeholders})
        ORDER BY win_probability DESC, id ASC
    """
    details_raw = _db_manager.execute_query(sql, tuple(meta_ids)) or []

    # 3) 构建 mapping：metadata_id -> [detail,...]
    details_map = {}
    for d in details_raw:
        k = d["recommendation_metadata_id"]
        details_map.setdefault(k, []).append(d)

    return algo_recs, details_map


@authenticated_page
def backtest_analysis_page():
    load_global_styles()
    db_manager = get_db_manager()
    ALGO_NAME_MAP = get_algorithm_display_names()

    st.markdown("""
    <div class="card">
        <h1>🔬 历史推荐回测分析（链表预取版）</h1>
        <p style="color: #7f8c8d;">先链表查询入内存，再做对比与渲染 — 避免空数据与异步问题</p>
    </div>
    """, unsafe_allow_html=True)

    # 加载所有可用期号
    with st.spinner("正在加载可分析的期号..."):
        periods = load_all_periods(db_manager)

    if not periods:
        st.warning("当前系统没有任何算法推荐数据，无法进行回测分析。")
        st.stop()

    # 选择期号
    st.markdown("### 🎯 请选择分析期号")
    selected_period = st.selectbox("选择期号", options=periods)

    if not selected_period:
        st.stop()

    # 先查询并缓存该期的推荐元数据与详情（一次性）
    with st.spinner("正在一次性加载该期的推荐元数据与所有组合..."):
        algo_recs, details_map = load_recommendations_and_details(db_manager, selected_period)

    if not algo_recs:
        st.warning(f"期号 {selected_period} 没有任何算法推荐数据。")
        st.stop()

    # 查询开奖号码（单条）
    actual_draw_raw = db_manager.execute_query(
        "SELECT * FROM lottery_history WHERE period_number = %s",
        (selected_period,)
    )

    if not actual_draw_raw:
        st.error(f"期号 {selected_period} 的开奖数据不存在，请先补全历史开奖记录。")
        st.stop()

    actual_draw = actual_draw_raw[0]
    try:
        actual_front = {actual_draw[f"front_area_{i + 1}"] for i in range(5)}
        actual_back = {actual_draw[f"back_area_{i + 1}"] for i in range(2)}
    except KeyError:
        st.error("lottery_history 表字段不完整，请确认字段名为 front_area_1..5, back_area_1..2")
        st.stop()

    st.markdown("### ✅ 当期开奖号码")
    st.metric(
        "开奖号码",
        f"🔴 {' '.join(map(str, sorted(list(actual_front))))}    🔵 {' '.join(map(str, sorted(list(actual_back))))}"
    )
    st.write("---")

    # 渲染所有算法（使用内存中的数据进行对比）
    st.markdown("### 🤖 算法推荐命中情况（基于内存中的链表数据）")

    for meta in algo_recs:
        algo_version = meta.get("algorithm_version", "unknown")
        display_name = ALGO_NAME_MAP.get(algo_version, algo_version)
        meta_id = meta.get("id")

        # header 卡片
        st.markdown(f"""
        <div class="card">
            <h3>🧠 {display_name}（版本：{algo_version}）</h3>
            <p>置信度：<b>{meta.get("confidence_score", "N/A")}</b> | 风险等级：<b>{meta.get("risk_level", "N/A")}</b></p>
        </div>
        """, unsafe_allow_html=True)

        # 从 details_map 里取出所有组合（已预取）
        details = details_map.get(meta_id, [])

        if not details:
            st.info("该算法没有推荐任何组合（或 recommendation_details 中没有对应记录）。")
            continue

        # 遍历并渲染每个组合
        for d in details:
            # 解析号码（兼容字符串或 json 存储形式）
            front_raw = d.get("front_numbers") or ""
            back_raw = d.get("back_numbers") or ""

            # 支持 "1,2,3,4,5" 或 JSON 列表 '["1","2",...]'
            def parse_number_field(val):
                if isinstance(val, (list, tuple)):
                    return [int(x) for x in val]
                if not isinstance(val, str):
                    return []
                v = val.strip()
                if v.startswith("[") and v.endswith("]"):
                    try:
                        arr = json.loads(v)
                        return [int(x) for x in arr]
                    except Exception:
                        pass
                # 最后按逗号分割
                return [int(x) for x in v.split(",") if x.strip().isdigit()]

            try:
                front_nums = parse_number_field(front_raw)
                back_nums = parse_number_field(back_raw)
            except Exception:
                front_nums = []
                back_nums = []

            hit_front = len(set(front_nums) & actual_front) if front_nums else 0
            hit_back = len(set(back_nums) & actual_back) if back_nums else 0

            title = (
                f"组合：🔴 {front_nums} + 🔵 {back_nums} "
                f"| 命中：{hit_front}/5 + {hit_back}/2"
            )

            with st.expander(title):
                # 高亮命中号码
                def fmt(nums, actual_set):
                    return ", ".join(
                        f"**🟩 {n}**" if n in actual_set else str(n)
                        for n in nums
                    )

                st.markdown(f"**前区：** {fmt(front_nums, actual_front)}  \n**后区：** {fmt(back_nums, actual_back)}",
                            unsafe_allow_html=True)

                # 显示细节字段（安全地取）
                st.write("推荐类型：", d.get("recommend_type", "N/A"))
                st.write("策略逻辑：", d.get("strategy_logic", ""))
                st.write("预计中奖概率：", d.get("win_probability", "N/A"))

                # 若你希望看到 meta 的分析依据，也可以在此处展示
                if meta.get("analysis_basis"):
                    with st.expander("查看该算法元数据（analysis_basis）"):
                        st.json(meta.get("analysis_basis"))

                # 原始数据
                with st.popover("查看原始组合记录"):
                    st.json(d)

    st.success("已完成基于内存链表的对比与渲染。")


# 运行页面
backtest_analysis_page()
