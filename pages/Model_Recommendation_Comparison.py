# 文件: pages/Model_Recommendation_Comparison.py
import streamlit as st
import pandas as pd
import json
from typing import List, Dict, Any, Tuple, Optional

# 项目工具（请确保这些函数在你的项目中存在）
from src.utils.helpers import get_db_manager, authenticated_page, get_algorithm_display_names
from src.ui.style_utils import load_global_styles


# -------------------------
# 辅助函数：解析号码、解析组合来源
# -------------------------
def parse_number_field(val) -> List[int]:
    """解析多种存储形式的号码字段，返回 int 列表"""
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        out = []
        for x in val:
            try:
                out.append(int(x))
            except Exception:
                continue
        return out
    if not isinstance(val, str):
        try:
            return [int(val)]
        except Exception:
            return []

    s = val.strip()
    # JSON 列表形式
    if s.startswith("[") and s.endswith("]"):
        try:
            arr = json.loads(s)
            return [int(x) for x in arr]
        except Exception:
            # fallthrough to comma-split
            pass

    parts = [p.strip() for p in s.split(",") if p.strip() != ""]
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except Exception:
            # ignore non-int tokens
            continue
    return nums


def extract_combinations_from_meta(meta: Dict[str, Any], raw_details: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    统一提取组合列表：
      1) 优先使用 recommendation_details 子表（raw_details）
      2) 若子表为空，从 meta 中的 analysis_basis / llm_cognitive_details / model_weights 等 JSON 字段解析组合
    返回的每一项结构：
      {
        "recommend_type": str,
        "strategy_logic": str,
        "front_numbers": [int,...],
        "back_numbers": [int,...],
        "win_probability": float,
        "source": "child_table" | "analysis_basis" | "llm_cognitive_details" | "other_meta"
      }
    """
    combos: List[Dict[str, Any]] = []

    # 1) 子表优先（如果传进来了）
    if raw_details:
        for d in raw_details:
            combos.append({
                "recommend_type": d.get("recommend_type") or d.get("combo_name") or "child_table",
                "strategy_logic": d.get("strategy_logic") or "",
                "front_numbers": parse_number_field(d.get("front_numbers")),
                "back_numbers": parse_number_field(d.get("back_numbers")),
                "win_probability": float(d.get("win_probability") or 0.0),
                "source": "child_table"
            })
        return combos

    # 2) 解析 analysis_basis（通常为字符串化 JSON 或 JSON 字段）
    def try_parse_json_field(field_val) -> Optional[Dict[str, Any]]:
        if not field_val:
            return None
        if isinstance(field_val, dict):
            return field_val
        if isinstance(field_val, str):
            try:
                return json.loads(field_val)
            except Exception:
                return None
        return None

    # helper to inspect a dict node for combo-like content
    def try_extract_from_node(node_key: str, node_value: Any, source_label: str):
        local_found = []
        if not isinstance(node_value, (dict, list)):
            return local_found

        # If node_value is a dict with keys like front_numbers/back_numbers
        if isinstance(node_value, dict):
            # direct combo
            if ("front_numbers" in node_value or "front_area" in node_value) and ("back_numbers" in node_value or "back_area" in node_value):
                front = node_value.get("front_numbers") or node_value.get("front_area")
                back = node_value.get("back_numbers") or node_value.get("back_area")
                local_found.append({
                    "recommend_type": node_value.get("combo_name") or node_value.get("recommend_type") or node_key,
                    "strategy_logic": node_value.get("strategy_focus") or node_value.get("reasoning_summary") or "",
                    "front_numbers": parse_number_field(front),
                    "back_numbers": parse_number_field(back),
                    "win_probability": float(node_value.get("win_probability") or 0.0),
                    "source": source_label
                })
            else:
                # maybe node contains nested combos
                for k2, v2 in node_value.items():
                    if isinstance(v2, dict):
                        if "front_numbers" in v2 or "back_numbers" in v2 or "front_area" in v2:
                            # nested combo
                            front = v2.get("front_numbers") or v2.get("front_area")
                            back = v2.get("back_numbers") or v2.get("back_area")
                            local_found.append({
                                "recommend_type": v2.get("combo_name") or v2.get("recommend_type") or k2,
                                "strategy_logic": v2.get("strategy_focus") or v2.get("reasoning_summary") or "",
                                "front_numbers": parse_number_field(front),
                                "back_numbers": parse_number_field(back),
                                "win_probability": float(v2.get("win_probability") or 0.0),
                                "source": source_label
                            })
                    # lists of combos
                    elif isinstance(v2, list):
                        for item in v2:
                            if isinstance(item, dict) and ("front_numbers" in item or "back_numbers" in item):
                                front = item.get("front_numbers") or item.get("front_area")
                                back = item.get("back_numbers") or item.get("back_area")
                                local_found.append({
                                    "recommend_type": item.get("combo_name") or item.get("recommend_type") or k2,
                                    "strategy_logic": item.get("strategy_focus") or item.get("reasoning_summary") or "",
                                    "front_numbers": parse_number_field(front),
                                    "back_numbers": parse_number_field(back),
                                    "win_probability": float(item.get("win_probability") or 0.0),
                                    "source": source_label
                                })
        elif isinstance(node_value, list):
            for item in node_value:
                if isinstance(item, dict) and ("front_numbers" in item or "back_numbers" in item):
                    front = item.get("front_numbers") or item.get("front_area")
                    back = item.get("back_numbers") or item.get("back_area")
                    local_found.append({
                        "recommend_type": item.get("combo_name") or item.get("recommend_type") or node_key,
                        "strategy_logic": item.get("strategy_focus") or item.get("reasoning_summary") or "",
                        "front_numbers": parse_number_field(front),
                        "back_numbers": parse_number_field(back),
                        "win_probability": float(item.get("win_probability") or 0.0),
                        "source": source_label
                    })
        return local_found

    # Try analysis_basis
    analysis_json = try_parse_json_field(meta.get("analysis_basis") or meta.get("analysis_basis_json") or meta.get("analysis_basis_str"))
    if analysis_json:
        if isinstance(analysis_json, dict):
            for k, v in analysis_json.items():
                combos.extend(try_extract_from_node(k, v, "analysis_basis"))
        else:
            # if top-level is list
            combos.extend(try_extract_from_node("analysis_basis", analysis_json, "analysis_basis"))

    # Try llm_cognitive_details
    llm_json = try_parse_json_field(meta.get("llm_cognitive_details") or meta.get("llm_details"))
    if llm_json:
        if isinstance(llm_json, dict):
            for k, v in llm_json.items():
                combos.extend(try_extract_from_node(k, v, "llm_cognitive_details"))
        else:
            combos.extend(try_extract_from_node("llm_cognitive_details", llm_json, "llm_cognitive_details"))

    # Try model_weights or other fields that might embed combos
    other_fields = ["model_weights", "models", "portfolio_A", "portfolio", "key_patterns"]
    for fld in other_fields:
        fld_json = try_parse_json_field(meta.get(fld))
        if fld_json:
            if isinstance(fld_json, dict):
                for k, v in fld_json.items():
                    combos.extend(try_extract_from_node(k, v, fld))
            else:
                combos.extend(try_extract_from_node(fld, fld_json, fld))

    # 去重：基于 front+back 组合去重（保持第一个出现）
    uniq = []
    seen = set()
    for c in combos:
        key = (tuple(sorted(c.get("front_numbers") or [])), tuple(sorted(c.get("back_numbers") or [])))
        if key not in seen:
            seen.add(key)
            uniq.append(c)

    return uniq


# -------------------------
# 缓存：只缓存可序列化的查询结果（不要把 db 传给缓存函数）
# -------------------------
@st.cache_data(ttl=600, show_spinner=False)
def load_periods() -> List[str]:
    db = get_db_manager()
    rows = db.execute_query("SELECT DISTINCT period_number FROM algorithm_recommendation ORDER BY period_number DESC")
    return [r["period_number"] for r in rows] if rows else []


@st.cache_data(ttl=300, show_spinner=False)
def load_recommendations_and_details(period_number: str) -> Tuple[List[Dict[str, Any]], Dict[int, List[Dict[str, Any]]]]:
    """
    一次性批量加载该期的 algorithm_recommendation (meta) 与 recommendation_details (detail)
    返回：metas(list of dict), detail_map {meta_id: [detail_dicts]}
    """
    db = get_db_manager()
    metas = db.execute_query(
        "SELECT * FROM algorithm_recommendation WHERE period_number = %s ORDER BY algorithm_version ASC, id ASC",
        (period_number,)
    ) or []

    if not metas:
        return [], {}

    meta_ids = [m["id"] for m in metas]
    placeholders = ",".join(["%s"] * len(meta_ids))
    sql = f"SELECT * FROM recommendation_details WHERE recommendation_metadata_id IN ({placeholders}) ORDER BY win_probability DESC, id ASC"
    details = db.execute_query(sql, tuple(meta_ids)) or []

    detail_map: Dict[int, List[Dict[str, Any]]] = {}
    for d in details:
        detail_map.setdefault(d["recommendation_metadata_id"], []).append(d)
    return metas, detail_map


# -------------------------
# 页面主体
# -------------------------
@authenticated_page
def model_recommendation_comparison_page():
    load_global_styles()
    db = get_db_manager()
    ALGO_NAME_MAP = get_algorithm_display_names()

    st.markdown("""
    <div class="card">
        <h1>📊 模型推荐对比（最终版）</h1>
        <p style="color:#7f8c8d">先批量链表查询入内存，再和历史开奖对比 — 支持从主表 JSON 自动解析组合</p>
    </div>
    """, unsafe_allow_html=True)

    # 选择期号
    with st.spinner("加载可用期号..."):
        periods = load_periods()
    if not periods:
        st.warning("当前系统没有 algorithm_recommendation 数据，无法进行对比。")
        st.stop()

    selected_period = st.selectbox("选择期号", periods, index=0)
    if not selected_period:
        st.stop()

    # 一次性加载该期 meta + details（缓存）
    with st.spinner("正在批量加载该期所有模型推荐与组合（元数据 + 子表）..."):
        metas, detail_map = load_recommendations_and_details(selected_period)

    if not metas:
        st.warning(f"期号 {selected_period} 没有任何算法推荐数据。")
        st.stop()

    # 获取开奖号码（不缓存）
    draw_row = db.fetch_one("SELECT * FROM lottery_history WHERE period_number = %s", (selected_period,))
    if not draw_row:
        st.error(f"期号 {selected_period} 的开奖数据不存在，请先补全 lottery_history 表。")
        st.stop()

    try:
        actual_front = {draw_row[f"front_area_{i+1}"] for i in range(5)}
        actual_back = {draw_row[f"back_area_{i+1}"] for i in range(2)}
    except KeyError:
        st.error("lottery_history 表字段不完整，请确认 front_area_1..5, back_area_1..2 存在。")
        st.stop()

    st.markdown("### ✅ 当期开奖号码")
    st.metric("开奖号码", f"🔴 {' '.join(map(str, sorted(actual_front)))}   🔵 {' '.join(map(str, sorted(actual_back)))}")
    st.write("---")

    # 在内存中构建所有模型的汇总与组合（优先子表，无子表则解析 meta）
    models_summary = []
    for meta in metas:
        meta_id = meta["id"]
        model_identifier = meta.get("models") or meta.get("algorithm_version") or f"model_{meta_id}"
        display_name = ALGO_NAME_MAP.get(meta.get("algorithm_version", model_identifier), model_identifier)

        raw_details = detail_map.get(meta_id, [])  # 子表
        combos = extract_combinations_from_meta(meta, raw_details)

        # 统计
        total_combos = len(combos)
        avg_win_prob = 0.0
        if total_combos > 0:
            try:
                avg_win_prob = sum([float(c.get("win_probability") or 0.0) for c in combos]) / total_combos
            except Exception:
                avg_win_prob = 0.0

        total_front_hits = sum(len(set(c.get("front_numbers", [])) & actual_front) for c in combos)
        total_back_hits = sum(len(set(c.get("back_numbers", [])) & actual_back) for c in combos)
        best_front_hit = max((len(set(c.get("front_numbers", [])) & actual_front) for c in combos), default=0)
        best_back_hit = max((len(set(c.get("back_numbers", [])) & actual_back) for c in combos), default=0)

        models_summary.append({
            "meta_id": meta_id,
            "model_identifier": model_identifier,
            "display_name": display_name,
            "confidence_score": meta.get("confidence_score"),
            "risk_level": meta.get("risk_level"),
            "total_combinations": total_combos,
            "avg_win_probability": avg_win_prob,
            "total_front_hits": total_front_hits,
            "total_back_hits": total_back_hits,
            "best_front_hit": best_front_hit,
            "best_back_hit": best_back_hit,
            "raw_meta": meta,
            "combos": combos
        })

    # 顶部汇总表格
    st.markdown("### 🧾 模型汇总（本期）")
    summary_df = pd.DataFrame([{
        "模型": m["display_name"],
        "标识": m["model_identifier"],
        "置信度": m["confidence_score"],
        "风险等级": m["risk_level"],
        "组合数": m["total_combinations"],
        "平均预测概率": m["avg_win_probability"],
        "总前区命中数(合计)": m["total_front_hits"],
        "总后区命中数(合计)": m["total_back_hits"],
        "单组合最高前区命中": m["best_front_hit"],
        "单组合最高后区命中": m["best_back_hit"],
    } for m in models_summary])

    # 排序与显示
    sort_by = st.selectbox("按哪一列排序", options=[
        "平均预测概率", "组合数", "总前区命中数(合计)", "总后区命中数(合计)", "单组合最高前区命中", "单组合最高后区命中"
    ], index=0)
    ascending = False if sort_by in ["平均预测概率", "单组合最高前区命中", "单组合最高后区命中"] else True
    summary_df = summary_df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
    st.dataframe(summary_df, use_container_width=True)

    # 导出 CSV
    csv = summary_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("导出汇总为 CSV", data=csv, file_name=f"model_comparison_summary_{selected_period}.csv", mime="text/csv")
    st.write("---")

    # 逐模型详细展示
    st.markdown("### 🔍 逐模型详解（展开每个模型查看所有组合与命中）")
    for m in models_summary:
        with st.container():
            st.markdown(f"#### 🧠 {m['display_name']} （{m['model_identifier']}）")
            st.write(f"置信度：**{m['confidence_score']}**  | 风险等级：**{m['risk_level']}**")
            st.write(f"组合数：{m['total_combinations']}  | 平均预测概率：{m['avg_win_probability']:.6f}")
            with st.expander("查看模型元数据 (meta)"):
                st.json(m["raw_meta"])

            combos = m["combos"]
            if not combos:
                st.info("该模型没有任何推荐组合（子表为空且 meta 中未检测到可解析组合）。")
                continue

            for idx, c in enumerate(combos, start=1):
                front_nums = c.get("front_numbers") or []
                back_nums = c.get("back_numbers") or []
                front_hit = len(set(front_nums) & actual_front)
                back_hit = len(set(back_nums) & actual_back)
                title = f"{idx}. 组合：🔴 {front_nums} + 🔵 {back_nums}  | 命中：{front_hit}/5 + {back_hit}/2  | 来源：{c.get('source')}  | 预计概率：{c.get('win_probability')}"
                with st.expander(title):
                    def fmt(nums, actual_set):
                        return ", ".join(f"**🟩 {n}**" if n in actual_set else str(n) for n in nums)
                    st.markdown(f"**前区：** {fmt(front_nums, actual_front)}  \n**后区：** {fmt(back_nums, actual_back)}", unsafe_allow_html=True)
                    st.write("推荐类型：", c.get("recommend_type") or "")
                    st.write("策略说明：", c.get("strategy_logic") or "")
                    st.write("预计中奖概率：", c.get("win_probability") or 0.0)
                    st.json(c)

            st.write("---")

    st.success("对比渲染完成。")

# 运行页面
model_recommendation_comparison_page()
