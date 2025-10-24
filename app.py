# file: app.py (新的应用主入口)
import streamlit as st
from pages.Login import login_page  # 从您的登录页面文件中导入登录函数
from src.ui.style_utils import add_final_elegant_css,hide_sidebar_for_pre_login_pages


# --- 1. 统一的页面配置 ---
# st.set_page_config 应该只在主入口文件中调用一次
st.set_page_config(
    page_title="Lotto-Pro 智能分析系统",
    page_icon="🔮",
    layout="wide"
)

add_final_elegant_css()


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # 如果用户未登录
    if not st.session_state.logged_in:
        hide_sidebar_for_pre_login_pages()
        login_page()
    # 如果用户已登录
    else:
        # 登录后，侧边栏和按钮会自动恢复显示
        st.sidebar.success(f"欢迎, {st.session_state.user.username} 👋")
        st.sidebar.markdown("---")

        # （可选）检查是否在主页，避免在每个子页面都显示欢迎语
        # 注意: Streamlit的多页面应用URL可能不反映在query_params中，
        # 更稳健的方式是检查当前页面的脚本路径或使用其他状态。
        # 但对于简单的欢迎信息，这样已经足够。
        current_page = st.session_state.get('page', 'main')
        if current_page == 'main':
            st.title("🔮 Lotto-Pro 智能分析系统")
            st.info("👈 请从左侧侧边栏选择一个页面开始使用。")

        if st.sidebar.button("退出登录"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()


if __name__ == "__main__":
    main()

