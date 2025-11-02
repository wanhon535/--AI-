# file: pages/Home.py (已修复)
import streamlit as st
import pandas as pd
import plotly.express as px
import extra_streamlit_components as stx
from src.utils.helpers import get_db_manager, authenticated_page  # <-- 导入
from src.ui.style_utils import load_global_styles

cookies = stx.CookieManager()


# --- 数据获取函数（保持不变）---
def get_user_stats(db_manager, user_id):
    """获取用户统计数据"""
    try:
        query_params = (user_id,)
        bet_result = db_manager.execute_query("SELECT COUNT(*) as total_bets FROM personal_betting WHERE user_id = %s",
                                              query_params)
        total_bets = bet_result[0]['total_bets'] if bet_result else 0
        investment_result = db_manager.execute_query(
            "SELECT COALESCE(SUM(bet_amount), 0) as total_investment FROM personal_betting WHERE user_id = %s",
            query_params)
        total_investment = investment_result[0]['total_investment'] if investment_result else 0
        winning_result = db_manager.execute_query(
            "SELECT COALESCE(SUM(winning_amount), 0) as total_winnings FROM personal_betting WHERE user_id = %s AND is_winning = 1",
            query_params)
        total_winnings = winning_result[0]['total_winnings'] if winning_result else 0
        win_count_result = db_manager.execute_query(
            "SELECT COUNT(*) as win_count FROM personal_betting WHERE user_id = %s AND is_winning = 1", query_params)
        win_count = win_count_result[0]['win_count'] if win_count_result else 0
        success_rate = (win_count / total_bets * 100) if total_bets > 0 else 0
        return {'total_bets': total_bets, 'total_investment': total_investment, 'total_winnings': total_winnings,
                'win_count': win_count, 'success_rate': success_rate, 'net_profit': total_winnings - total_investment}
    except Exception as e:
        st.error(f"获取统计数据时出错: {e}");
        return None


def get_recent_bets(db_manager, user_id, limit=5):
    try:
        query = "SELECT period_number, bet_time, bet_type, front_numbers, back_numbers, bet_amount, is_winning, winning_amount, winning_level FROM personal_betting WHERE user_id = %s ORDER BY bet_time DESC LIMIT %s"
        return db_manager.execute_query(query, (user_id, limit))
    except Exception as e:
        st.error(f"获取投注记录时出错: {e}");
        return []


def get_latest_lottery_result(db_manager):
    try:
        query = "SELECT period_number, draw_date, CONCAT(front_area_1, ',', front_area_2, ',', front_area_3, ',', front_area_4, ',', front_area_5) as front_numbers, CONCAT(back_area_1, ',', back_area_2) as back_numbers, sum_value, odd_even_ratio, size_ratio FROM lottery_history ORDER BY draw_date DESC LIMIT 1"
        results = db_manager.execute_query(query)
        return results[0] if results else None
    except Exception as e:
        st.error(f"获取开奖结果时出错: {e}");
        return None


# --- UI 组件创建函数 (保持不变) ---
def create_metrics_cards(stats):
    if not stats: return
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(label="总投注次数", value=f"{stats['total_bets']} 次")
    with col2: st.metric(label="总投资金额", value=f"¥{stats['total_investment']:.2f}")
    with col3: st.metric(label="总中奖金额", value=f"¥{stats['total_winnings']:.2f}",
                         delta=f"¥{stats['net_profit']:.2f}",
                         delta_color="normal" if stats['net_profit'] >= 0 else "inverse")
    with col4: st.metric(label="投注成功率", value=f"{stats['success_rate']:.1f}%")


def create_quick_actions():
    st.markdown("### ⚡ 快速操作")
    col1, col2, col3, col4 = st.columns(4)
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2, row2_col3 = st.columns(3)

    # 第一行
    if row1_col1.button("💬 AI 对话", use_container_width=True, type="primary"):  # 新增的聊天按钮
        st.switch_page("pages/Chatbot.py")
    if col1.button("🎯 智能分析", use_container_width=True): st.switch_page("pages/Analysis.py")
    if col2.button("📊 数据看板", use_container_width=True): st.switch_page("pages/_Dashboard.py")
    if col3.button("💸 我要投注", use_container_width=True): st.switch_page("pages/Betting.py")
    if col4.button("📈 历史记录", use_container_width=True): st.switch_page("pages/History.py")
    if row2_col3.button("🔬 回测分析", use_container_width=True):  # 将回测分析也加入快捷入口
        st.switch_page("pages/Backtest_Analysis.py")


def create_lottery_display(lottery_data):
    if not lottery_data: st.info("暂无开奖数据"); return
    st.markdown("### 🎰 最新开奖结果")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**期号：** {lottery_data['period_number']} | **开奖日期：** {lottery_data['draw_date']}")
        st.markdown(
            f"**和值：** {lottery_data['sum_value']} | **奇偶比：** {lottery_data['odd_even_ratio']} | **大小比：** {lottery_data['size_ratio']}")
    with col2:
        st.markdown("**开奖号码**")
        front_nums = lottery_data['front_numbers'].split(',')
        back_nums = lottery_data['back_numbers'].split(',')
        front_html = "".join([
                                 f'<span style="display: inline-block; width: 30px; height: 30px; background: #ff4757; color: white; border-radius: 50%; text-align: center; line-height: 30px; margin: 2px;">{num}</span>'
                                 for num in front_nums])
        back_html = "".join([
                                f'<span style="display: inline-block; width: 30px; height: 30px; background: #3742fa; color: white; border-radius: 50%; text-align: center; line-height: 30px; margin: 2px;">{num}</span>'
                                for num in back_nums])
        st.markdown(f'前区: {front_html}<br>后区: {back_html}', unsafe_allow_html=True)


def create_recent_bets_table(recent_bets):
    if not recent_bets: st.info("暂无投注记录"); return
    st.markdown("### 📋 最近投注记录")
    table_data = [
        {"期号": b['period_number'], "投注时间": b['bet_time'].strftime("%Y-%m-%d %H:%M"), "类型": b['bet_type'],
         "前区": b['front_numbers'], "后区": b['back_numbers'], "金额": f"¥{b['bet_amount']:.2f}",
         "状态": "🎉 中奖" if b['is_winning'] else "⏳ 待开奖",
         "中奖金额": f"¥{b['winning_amount']:.2f}" if b['is_winning'] else "-"} for b in recent_bets]
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)


def create_performance_chart(stats):
    if not stats or stats['total_bets'] == 0: return
    fig = px.pie(values=[stats['win_count'], stats['total_bets'] - stats['win_count']], names=['中奖', '未中奖'],
                 title="投注结果分布", color_discrete_sequence=['#2ed573', '#ff6b81'])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=300, showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)


# --- 主页面渲染函数 ---
@authenticated_page  # <-- 应用认证装饰器
def home_page():
    load_global_styles()
    user = st.session_state.get("user")

    # 侧边栏登出逻辑
    with st.sidebar:
        st.success(f"欢迎, {user.username} 👋")
        st.markdown("---")
        if st.button("退出登录", use_container_width=True):
            # 清理会话状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            # 清理Cookie
            cookies.delete('username')

            # 强制重新运行以跳转到登录页
            st.rerun()

    db_manager = get_db_manager()  # 获取共享的数据库连接

    # --- 欢迎卡片 ---
    st.markdown(
        f"""<div class="card"><h1 style="margin-bottom: 0.5rem;">🎯 欢迎回来, {user.username}!</h1><p style="color: #7f8c8d; margin-bottom: 0;">Lotto-Pro 智能分析系统为您提供专业的彩票分析和推荐</p></div>""",
        unsafe_allow_html=True)

    create_quick_actions()
    st.markdown("---")

    # --- 主内容区 ---
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 个人统计概览")
        stats = get_user_stats(db_manager, user.username)
        if stats:
            create_metrics_cards(stats)
            st.markdown("<br>", unsafe_allow_html=True)
            recent_bets = get_recent_bets(db_manager, user.username)
            create_recent_bets_table(recent_bets)
        else:
            st.info("暂无统计数据，开始您的第一次投注吧！")

    with col2:
        lottery_data = get_latest_lottery_result(db_manager)
        create_lottery_display(lottery_data)
        st.markdown("---")
        if 'stats' in locals() and stats and stats['total_bets'] > 0:
            create_performance_chart(stats)
        st.markdown("### 💡 使用提示")
        st.info(
            "使用**智能分析**获取算法推荐\n\n查看**数据看板**了解系统性能\n\n在**投注页面**记录您的选择\n\n定期查看**历史记录**复盘分析")

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #95a5a6; font-size: 0.9rem;'><p>💡 理性投注，量力而行 | Lotto-Pro 智能分析系统 v1.0</p></div>",
        unsafe_allow_html=True)


home_page()