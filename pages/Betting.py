# file: pages/Betting.py (已升级支持复式和胆拖)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import math  # 需要导入 math 库来进行组合计算
from src.database.database_manager import DatabaseManager
from src.ui.style_utils import load_global_styles

FRONT_AREA_NUMBERS = list(range(1, 36))
BACK_AREA_NUMBERS = list(range(1, 13))


# --- 核心函数：验证逻辑已修复 ---
def calculate_and_validate_bet(bet_type, front_nums, back_nums):
    """验证投注并计算注数，已修复单式验证逻辑"""
    try:
        if bet_type == 'single':
            if len(front_nums) != 5 or len(back_nums) != 2:
                return 0, "单式投注必须选择5个前区号码和2个后区号码。"
            return 1, None

        elif bet_type == 'compound':
            if len(front_nums) < 5 or len(back_nums) < 2:
                return 0, "复式投注号码不符合规则 (前区≥5, 后区≥2)。"
            if len(front_nums) == 5 and len(back_nums) == 2:
                st.warning("提示：您选择的号码组合为5+2，这实际上是一注单式投注。")
                return 1, None

            front_comb = math.comb(len(front_nums), 5)
            back_comb = math.comb(len(back_nums), 2)
            return front_comb * back_comb, None

        elif bet_type == 'dantuo':
            front_dan, front_tuo = front_nums["dan"], front_nums["tuo"]
            back_dan, back_tuo = back_nums["dan"], back_nums["tuo"]
            if not (1 <= len(front_dan) <= 4): return 0, "前区胆码必须在1到4个之间。"
            if (len(front_dan) + len(front_tuo)) < 6: return 0, "前区(胆码+拖码)总数必须大于等于6。"
            if not (0 <= len(back_dan) <= 1): return 0, "后区胆码必须是0或1个。"
            if (len(back_dan) + len(back_tuo)) < 3: return 0, "后区(胆码+拖码)总数必须大于等于3。"
            if set(front_dan) & set(front_tuo): return 0, "前区胆码和拖码不能有重复号码。"
            if set(back_dan) & set(back_tuo): return 0, "后区胆码和拖码不能有重复号码。"
            front_comb = math.comb(len(front_tuo), 5 - len(front_dan))
            back_comb = math.comb(len(back_tuo), 2 - len(back_dan))
            return front_comb * back_comb, None

    except (ValueError, TypeError, KeyError):
        return 0, "号码格式或组合有误，无法计算。"
    return 0, "无效的投注类型。"


# --- 数据获取函数 ---
def get_latest_recommendations(db_manager):
    try:
        latest_period = get_latest_period(db_manager)
        if not latest_period: return []
        query = """
        SELECT rd.recommend_type, rd.strategy_logic, rd.front_numbers, rd.back_numbers
        FROM recommendation_details rd
        JOIN algorithm_recommendation ar ON rd.recommendation_metadata_id = ar.id
        WHERE ar.period_number = %s
        ORDER BY ar.recommend_time DESC, rd.win_probability DESC
        """
        return db_manager.execute_query(query, (latest_period,))
    except Exception as e:
        st.error(f"加载算法推荐时出错: {e}");
        return []


def get_user_bets(db_manager, user_id, limit=100):
    try:
        query = "SELECT * FROM personal_betting WHERE user_id = %s ORDER BY bet_time DESC LIMIT %s"
        return db_manager.execute_query(query, (user_id, limit))
    except Exception as e:
        st.error(f"获取投注记录时出错: {e}");
        return []


def get_latest_period(db_manager):
    try:
        query = "SELECT period_number FROM lottery_history ORDER BY draw_date DESC LIMIT 1"
        result = db_manager.execute_query(query)
        return result[0]['period_number'] if result else "2025001"
    except Exception as e:
        st.error(f"获取最新期号时出错: {e}");
        return "2025001"


# --- 数据写入函数 ---
def insert_betting_record(db_manager, user_id, bet_data):
    try:
        query = """
        INSERT INTO personal_betting 
        (user_id, period_number, bet_time, bet_type, front_numbers, front_count, 
         back_numbers, back_count, bet_amount, multiple, strategy_type, confidence_level, analysis_notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        success = db_manager.execute_update(query, (
            user_id, bet_data['period_number'], bet_data['bet_time'], bet_data['bet_type'],
            bet_data['front_numbers'], bet_data['front_count'], bet_data['back_numbers'],
            bet_data['back_count'], bet_data['bet_amount'], bet_data['multiple'],
            bet_data.get('strategy_type', 'manual'), bet_data.get('confidence_level', 50),
            bet_data.get('analysis_notes', '')
        ))
        return success
    except Exception as e:
        st.error(f"插入投注记录时出错: {e}");
        return False


# --- 主页面渲染函数 ---
def betting_page():
    if not st.session_state.get("logged_in", False):
        st.warning("请先登录系统");
        st.switch_page("pages/Login.py");
        return

    load_global_styles()
    user = st.session_state.get("user")
    if not user:
        st.error("用户信息获取失败");
        return

    if 'prefill_front' not in st.session_state:
        st.session_state.prefill_front = []
    if 'prefill_back' not in st.session_state:
        st.session_state.prefill_back = []

    st.markdown(f"""
    <div class="card">
        <h1>💸 投注管理中心</h1>
        <p style="color: #7f8c8d;">欢迎 {user.username}，记录和管理您的投注</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        db_manager = DatabaseManager(host='localhost', user='root', password='123456789',
                                     database='lottery_analysis_system', port=3309)
        if not db_manager.connect():
            st.error("数据库连接失败");
            return
    except Exception as e:
        st.error(f"数据库连接错误: {e}");
        return

    try:
        tab1, tab2, tab3 = st.tabs(["🎯 新增投注", "📋 投注记录", "📊 投注统计"])

        with tab1:
            st.markdown("### 🎯 新增投注记录")
            with st.form("betting_form"):
                col1, col2 = st.columns(2)
                with col1:
                    period_number = st.text_input("期号", value=get_latest_period(db_manager))
                    bet_type = st.selectbox("投注类型", ["single", "compound", "dantuo"],
                                            format_func=lambda x:
                                            {"single": "单式", "compound": "复式", "dantuo": "胆拖"}[x])
                with col2:
                    multiple = st.number_input("投注倍数", min_value=1, value=1, step=1)
                    confidence_level = st.slider("信心指数", 0, 100, 50)

                st.markdown("---")
                if bet_type in ['single', 'compound']:
                    front_numbers = st.multiselect("前区号码", options=FRONT_AREA_NUMBERS,
                                                   default=st.session_state.prefill_front)
                    back_numbers = st.multiselect("后区号码", options=BACK_AREA_NUMBERS,
                                                  default=st.session_state.prefill_back)
                    st.session_state.prefill_front, st.session_state.prefill_back = [], []
                elif bet_type == 'dantuo':
                    c1, c2 = st.columns(2)
                    front_dan = c1.multiselect("前区胆码 (1-4个)", options=FRONT_AREA_NUMBERS)
                    front_tuo = c2.multiselect("前区拖码", options=FRONT_AREA_NUMBERS)
                    back_dan = c1.multiselect("后区胆码 (0-1个)", options=BACK_AREA_NUMBERS)
                    back_tuo = c2.multiselect("后区拖码", options=BACK_AREA_NUMBERS)

                st.markdown("---")
                strategy_type = st.selectbox("投注策略", ["manual", "algorithm", "hot_numbers", "cold_numbers"],
                                             format_func=lambda x:
                                             {"manual": "手动选择", "algorithm": "算法推荐", "hot_numbers": "热号主攻",
                                              "cold_numbers": "冷号回补"}[x])
                analysis_notes = st.text_area("分析备注", placeholder="记录您的选号思路和分析...", height=100)

                if strategy_type == 'algorithm':
                    with st.container():
                        st.markdown("#### 👇 最新算法推荐方案")
                        recommendations = get_latest_recommendations(db_manager)
                        if recommendations:
                            st.info("点击下方按钮可将号码填充至上方选号区。")
                            for i, rec in enumerate(recommendations):
                                with st.expander(f"方案 {i + 1}: {rec['recommend_type']}"):
                                    st.write(
                                        f"**策略:** {rec['strategy_logic']} | **前区:** {rec['front_numbers']} | **后区:** {rec['back_numbers']}")
                                    # ✅ 核心修复：使用 f-string 和循环索引 i 来创建唯一的 key
                                    if st.button("使用此方案", key=f"use_rec_{i}", use_container_width=True):
                                        try:
                                            st.session_state.prefill_front = [int(n) for n in
                                                                              rec['front_numbers'].split(',')]
                                            st.session_state.prefill_back = [int(n) for n in
                                                                             rec['back_numbers'].split(',')]
                                            st.rerun()
                                        except:
                                            st.error("填充号码时格式转换失败！")
                        else:
                            st.warning("未找到当前期号的算法推荐。")

                submitted = st.form_submit_button("💾 保存投注记录", type="primary", use_container_width=True)

            if submitted:
                front_input_data, back_input_data = None, None
                if bet_type in ['single', 'compound']:
                    front_input_data, back_input_data = sorted(front_numbers), sorted(back_numbers)
                elif bet_type == 'dantuo':
                    front_input_data = {"dan": sorted(front_dan), "tuo": sorted(front_tuo)}
                    back_input_data = {"dan": sorted(back_dan), "tuo": sorted(back_tuo)}

                combinations, error_msg = calculate_and_validate_bet(bet_type, front_input_data, back_input_data)
                if error_msg:
                    st.error(f"❌ 投注无效: {error_msg}");
                    return
                if combinations == 0:
                    st.warning("您选择的号码组合无法构成有效投注（0注）。");
                    return

                bet_amount = combinations * 2.0 * multiple
                front_db_json, back_db_json = json.dumps(front_input_data), json.dumps(back_input_data)
                front_count = len(front_input_data) if isinstance(front_input_data, list) else len(
                    front_input_data["dan"]) + len(front_input_data["tuo"])
                back_count = len(back_input_data) if isinstance(back_input_data, list) else len(
                    back_input_data["dan"]) + len(back_input_data["tuo"])

                bet_data = {
                    'period_number': period_number, 'bet_time': datetime.now(), 'bet_type': bet_type,
                    'front_numbers': front_db_json, 'front_count': front_count, 'back_numbers': back_db_json,
                    'back_count': back_count, 'bet_amount': bet_amount, 'multiple': multiple,
                    'strategy_type': strategy_type, 'confidence_level': confidence_level,
                    'analysis_notes': analysis_notes
                }
                if insert_betting_record(db_manager, user.username, bet_data):
                    st.success(f"✅ 投注记录保存成功！共 {combinations} 注，金额 ¥{bet_amount:.2f}");
                    st.balloons()
                # else 语句已在函数内部处理 st.error

        with tab2:
            st.markdown("### 📋 历史投注记录")
            bets = get_user_bets(db_manager, user.username, 100)
            if bets:
                bet_display_list = []
                for bet in bets:
                    # --- 优化数据显示，适配JSON格式 ---
                    try:
                        front_data = json.loads(bet['front_numbers'])
                        back_data = json.loads(bet['back_numbers'])

                        if bet['bet_type'] == 'dantuo':
                            front_display = f"胆: {','.join(map(str, front_data.get('dan', [])))} | 拖: {','.join(map(str, front_data.get('tuo', [])))}"
                            back_display = f"胆: {','.join(map(str, back_data.get('dan', [])))} | 拖: {','.join(map(str, back_data.get('tuo', [])))}"
                        else:  # single or compound
                            front_display = ','.join(map(str, front_data))
                            back_display = ','.join(map(str, back_data))
                    except:  # 兼容旧的非JSON数据
                        front_display = bet['front_numbers']
                        back_display = bet['back_numbers']

                    bet_display_list.append({
                        "期号": bet['period_number'], "投注时间": bet['bet_time'].strftime("%Y-%m-%d %H:%M"),
                        "类型": {"single": "单式", "compound": "复式", "dantuo": "胆拖"}.get(bet['bet_type'],
                                                                                             bet['bet_type']),
                        "前区": front_display, "后区": back_display,
                        "金额": f"¥{bet['bet_amount']:.2f}", "倍数": bet['multiple'],
                        "状态": "🎉 中奖" if bet['is_winning'] else "⏳ 待开奖",
                        "中奖金额": f"¥{bet['winning_amount']:.2f}" if bet['is_winning'] else "-"
                    })
                df = pd.DataFrame(bet_display_list)
                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 导出CSV", csv, f"投注记录_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv",
                                   use_container_width=True)
            else:
                st.info("暂无投注记录，开始您的第一次投注吧！")

        with tab3:
            st.markdown("### 📊 投注统计")
            # ... (此部分代码无需修改) ...
            bets = get_user_bets(db_manager, user.username, 1000)
            if bets:
                total_bets = len(bets)
                total_investment = sum(bet['bet_amount'] for bet in bets)
                winning_bets = [bet for bet in bets if bet['is_winning']]
                total_winnings = sum(bet['winning_amount'] for bet in winning_bets)
                win_rate = len(winning_bets) / total_bets * 100 if total_bets > 0 else 0
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总投注数", f"{total_bets} 次")
                with col2:
                    st.metric("总投入", f"¥{total_investment:.2f}")
                with col3:
                    st.metric("总收益", f"¥{total_winnings:.2f}")
                with col4:
                    st.metric("胜率", f"{win_rate:.1f}%")

                bet_type_counts = {}
                for bet in bets:
                    bet_type_display = {"single": "单式", "compound": "复式", "dantuo": "胆拖"}.get(bet['bet_type'],
                                                                                                    bet['bet_type'])
                    bet_type_counts[bet_type_display] = bet_type_counts.get(bet_type_display, 0) + 1
                if bet_type_counts:
                    type_df = pd.DataFrame(
                        {'类型': list(bet_type_counts.keys()), '数量': list(bet_type_counts.values())})
                    fig = px.pie(type_df, values='数量', names='类型', title="投注类型分布")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无投注数据")

        st.markdown("---")
        st.markdown("### 🚀 快速导航")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏠 返回首页", use_container_width=True): st.switch_page("pages/Home.py")
        with col2:
            if st.button("🔍 智能分析", use_container_width=True): st.switch_page("pages/Analysis.py")
        with col3:
            if st.button("🤖 算法推荐", use_container_width=True): st.switch_page("pages/Recommendations.py")

    except Exception as e:
        st.error(f"页面加载出错: {e}")
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    betting_page()
else:
    betting_page()