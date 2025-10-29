import streamlit as st
import pandas as pd
from src.database.database_manager import DatabaseManager
from src.ui.style_utils import load_global_styles


# --- 优化点 1: 使用缓存来管理数据库连接 ---
# @st.cache_resource 会为每个用户的会话缓存这个函数的返回值。
# 这意味着在用户的整个会话期间，数据库连接只会建立一次。
@st.cache_resource
def get_db_manager():
    """
    获取并缓存数据库管理器实例。
    """
    db_manager = DatabaseManager(
        host='localhost',
        user='root',
        password='123456789',
        database='lottery_analysis_system',
        port=3309
    )
    # 确保在使用前连接是活动的
    if not db_manager.is_connected():
        db_manager.connect()
    return db_manager


def get_lottery_history(db_manager, page_num=1, page_size=20):
    """获取分页的历史开奖数据"""
    try:
        offset = (page_num - 1) * page_size
        query = """
        SELECT period_number, draw_date, front_area_1, front_area_2, front_area_3, front_area_4, front_area_5, 
               back_area_1, back_area_2, sum_value, odd_even_ratio, size_ratio 
        FROM lottery_history 
        ORDER BY period_number DESC 
        LIMIT %s OFFSET %s
        """
        results = db_manager.execute_query(query, (page_size, offset))

        count_query = "SELECT COUNT(*) as total FROM lottery_history"
        total_count_result = db_manager.execute_query(count_query)
        total_count = total_count_result[0]['total'] if total_count_result else 0

        return results, total_count
    except Exception as e:
        st.error(f"获取历史记录时出错: {e}")
        return [], 0


def history_page():
    """历史记录页面"""
    if not st.session_state.get("logged_in", False):
        st.warning("请先登录系统")
        st.switch_page("pages/Login.py")
        return

    load_global_styles()

    st.markdown("""
    <div class="card">
        <h1>📈 历史开奖记录</h1>
        <p style="color: #7f8c8d;">查询过往的所有开奖数据，进行复盘分析</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        db_manager = get_db_manager()  # 从缓存中获取数据库管理器
    except Exception as e:
        st.error(f"数据库连接错误: {e}")
        return

    try:
        # --- 分页控制 ---
        page_size = 25  # 每页显示25条
        if 'history_page_num' not in st.session_state:
            st.session_state.history_page_num = 1

        history_data, total_records = get_lottery_history(db_manager, st.session_state.history_page_num, page_size)
        total_pages = (total_records + page_size - 1) // page_size if page_size > 0 else 0

        st.markdown("### 📅 开奖数据列表")

        if history_data:
            df_data = []
            for row in history_data:
                front_nums = f"{row['front_area_1']:02},{row['front_area_2']:02},{row['front_area_3']:02},{row['front_area_4']:02},{row['front_area_5']:02}"
                back_nums = f"{row['back_area_1']:02},{row['back_area_2']:02}"
                df_data.append({
                    "期号": row['period_number'],
                    "开奖日期": row['draw_date'].strftime('%Y-%m-%d'),
                    "前区号码": front_nums,
                    "后区号码": back_nums,
                    "和值": row['sum_value'],
                    "奇偶比": row['odd_even_ratio'],
                    "大小比": row['size_ratio']
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # 分页UI
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 3, 2])

            with col1:
                # 按钮在禁用状态下仍会占用空间
                prev_disabled = st.session_state.history_page_num <= 1
                if st.button("⬅️ 上一页", use_container_width=True, disabled=prev_disabled):
                    st.session_state.history_page_num -= 1
                    st.rerun()

            with col2:
                st.write(f"第 {st.session_state.history_page_num} 页 / 共 {total_pages} 页 ( {total_records} 条记录 )")

            with col3:
                next_disabled = st.session_state.history_page_num >= total_pages
                if st.button("下一页 ➡️", use_container_width=True, disabled=next_disabled):
                    st.session_state.history_page_num += 1
                    st.rerun()
        else:
            st.info("暂无历史开奖记录。")

        # 快速导航
        st.markdown("---")
        st.markdown("### 🚀 快速导航")
        nav_cols = st.columns(3)
        if nav_cols[0].button("🏠 返回首页", use_container_width=True):
            st.switch_page("pages/Home.py")
        if nav_cols[1].button("💸 我要投注", use_container_width=True):
            st.switch_page("pages/Betting.py")
        if nav_cols[2].button("🤖 算法推荐", use_container_width=True):
            st.switch_page("pages/Recommendations.py")

    except Exception as e:
        st.error(f"页面加载时发生未知错误: {e}")
        st.exception(e)  # 打印更详细的堆栈信息以供调试


# --- 优化点 2: 移除文件末尾的直接调用 ---
# Streamlit 会自动运行这个文件，不需要手动调用函数。
# 仅保留主函数定义即可。
history_page()