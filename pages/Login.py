# file: pages/Login.py (已修复)
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta

from src.database.database_manager import DatabaseManager
from src.utils.helpers import get_db_manager  # <-- 导入新的辅助函数
from src.model.user_models import User
from src.auth.auth_utils import hash_password
from src.ui.style_utils import load_global_styles, hide_sidebar_for_pre_login_pages

cookies = stx.CookieManager()


def authenticate_user(db_manager: DatabaseManager, username: str, password: str) -> User or None:
    """使用共享的db_manager进行用户认证"""
    try:
        query = "SELECT id, username, password_hash, email, is_active, last_login FROM users WHERE username = %s"
        result = db_manager.execute_query(query, (username,))
        if not result:
            return None

        user_data = result[0]
        # 验证密码
        if user_data['password_hash'] == hash_password(password):
            db_manager.execute_update("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                                      (user_data['id'],))
            return User(**user_data)
        return None
    except Exception as e:
        st.error(f"登录过程出错: {str(e)}")
        return None


def login_page():
    load_global_styles()
    hide_sidebar_for_pre_login_pages()

    # 如果已登录，则自动跳转到主页
    if st.session_state.get("logged_in", False):
        st.switch_page("pages/Home.py")
        return

    st.markdown('<div class="login-card"><h2>用户登录</h2></div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("用户名", placeholder="请输入您的用户名", key="login_username")
        password = st.text_input("密码", type="password", placeholder="请输入您的密码", key="login_password")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        login_submitted = col1.form_submit_button("登录", use_container_width=True, type="primary")
        register_clicked = col2.form_submit_button("注册", use_container_width=True)

    if login_submitted:
        if username and password:
            with st.spinner("正在验证..."):
                db_manager = get_db_manager()  # 获取共享的数据库连接
                user = authenticate_user(db_manager, username, password)

                if user and user.is_active:
                    # 设置会话状态
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = user

                    # 设置cookie
                    expires_at = datetime.now() + timedelta(days=1)
                    cookies.set('username', user.username, expires_at=expires_at)

                    # 使用 st.rerun() 强制页面重新运行以应用新的会话状态
                    # 这将触发顶部的 "if logged_in" 检查并自动跳转
                    st.rerun()

                elif user and not user.is_active:
                    st.error("您的账号已被禁用，请联系管理员。")
                else:
                    st.error("用户名或密码错误。")
        else:
            st.warning("请输入用户名和密码。")

    if register_clicked:
        st.switch_page("pages/Register.py")

    st.markdown(
        "<div style='text-align: center; margin-top: 1rem;'><p style='color: #95a5a6; font-size: 14px;'>首次使用？请点击注册按钮创建账号</p></div>",
        unsafe_allow_html=True
    )


login_page()