# file: pages/Login.py (正确版本)
# file: pages/Login.py (最终版)
import streamlit as st
import extra_streamlit_components as stx
from src.database.database_manager import DatabaseManager
from src.model.user_models import User
from src.auth.auth_utils import hash_password
from src.ui.style_utils import load_global_styles, hide_sidebar_for_pre_login_pages

from datetime import timedelta, datetime




cookies = stx.CookieManager()


def authenticate_user(username: str, password: str) -> User or None:
    # ... (此函数内部逻辑不变)
    db_manager = None
    try:
        db_manager = DatabaseManager(host='localhost', user='root', password='123456789',
                                     database='lottery_analysis_system', port=3309)
        if not db_manager.connect():
            st.error("数据库连接失败");
            return None
        query = "SELECT id, username, password_hash, email, is_active, last_login FROM users WHERE username = %s"
        result = db_manager.execute_query(query, (username,))
        if not result: return None
        user_data = result[0]
        if user_data['password_hash'] == hash_password(password):
            db_manager.execute_update("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                                      (user_data['id'],))
            return User(**user_data)
        return None
    except Exception as e:
        st.error(f"登录过程出错: {str(e)}");
        return None
    finally:
        if db_manager: db_manager.disconnect()


def login_page():
    load_global_styles()
    hide_sidebar_for_pre_login_pages()

    if st.session_state.get("logged_in", False):
        st.switch_page("pages/Home.py");
        return

    st.markdown('<div class="login-card"><h2>用户登录</h2></div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("用户名", placeholder="请输入您的用户名", key="login_username")
        password = st.text_input("密码", type="password", placeholder="请输入您的密码", key="login_password")
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        login_submitted = col1.form_submit_button("登录", use_container_width=True, type="primary")
        register_clicked = col2.form_submit_button("注册", use_container_width=True)

    if login_submitted:
        if username and password:
            with st.spinner("正在验证..."):
                user = authenticate_user(username, password)
                if user and user.is_active:
                    st.session_state["user"] = user
                    st.session_state["logged_in"] = True

                    expires_at = datetime.now() + timedelta(minutes=5)
                    cookies.set('username', user.username, expires_at=expires_at)
                    cookies.set('expires_at', expires_at.isoformat(), expires_at=expires_at)

                    # 使用 st.experimental_rerun() 可能会更稳定
                    st.experimental_rerun()
                elif user and not user.is_active:
                    st.error("您的账号已被禁用")
                else:
                    st.error("用户名或密码错误")
        else:
            st.warning("请输入用户名和密码")

    if register_clicked:
        st.switch_page("pages/Register.py")

    st.markdown(
        "<div style='text-align: center; margin-top: 1rem; padding-top: 1.5rem;'><p style='color: #95a5a6; font-size: 14px; margin: 0;'>首次使用？请点击注册按钮创建账号</p></div>",
        unsafe_allow_html=True)

if __name__ == "__main__":
    login_page()
else:
    login_page()