# file: pages/Register.py (已修复)
import streamlit as st
import re
import time
from src.database.database_manager import DatabaseManager
from src.utils.helpers import get_db_manager  # <-- 导入新的辅助函数
from src.auth.auth_utils import hash_password, generate_captcha_challenge, verify_captcha
from src.ui.style_utils import load_global_styles, hide_sidebar_for_pre_login_pages


def is_valid_email(email: str) -> bool:
    """验证邮箱格式是否有效"""
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is not None


def register_user(db_manager: DatabaseManager, username, password, email) -> (bool, str):
    """使用共享的db_manager进行用户注册"""
    try:
        if db_manager.execute_query("SELECT id FROM users WHERE username = %s", (username,)):
            return False, "该用户名已被注册，请更换一个。"
        if db_manager.execute_query("SELECT id FROM users WHERE email = %s", (email,)):
            return False, "该邮箱已被注册，请使用其他邮箱。"

        hashed_pwd = hash_password(password)
        query = "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
        success = db_manager.execute_update(query, (username, hashed_pwd, email))

        if success:
            return True, "恭喜！账号注册成功，请前往登录页面登录。"
        else:
            return False, "注册失败，数据库写入时发生错误。"
    except Exception as e:
        return False, f"注册过程发生未知错误: {e}"


def register_page():
    load_global_styles()
    hide_sidebar_for_pre_login_pages()

    if st.session_state.get("logged_in", False):
        st.switch_page("pages/Home.py")
        return

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>新用户注册</h2>", unsafe_allow_html=True)

    with st.form("register_form"):
        username = st.text_input("用户名", placeholder="至少4个字符")
        email = st.text_input("电子邮箱", placeholder="用于通知和密码找回")
        password = st.text_input("设置密码", type="password", placeholder="至少6个字符")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        st.markdown("---")
        # 简单的人机验证
        user_captcha_answer = generate_captcha_challenge()
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("立即注册", use_container_width=True, type="primary")

    if submitted:
        if not verify_captcha(user_captcha_answer):
            st.error("❌ 人机验证问题回答错误，请重试！")
        elif len(username) < 4:
            st.warning("⚠️ 用户名长度不能少于4个字符")
        elif not is_valid_email(email):
            st.warning("⚠️ 请输入有效的电子邮箱地址")
        elif len(password) < 6:
            st.warning("⚠️ 密码长度不能少于6个字符")
        elif password != confirm_password:
            st.error("❌ 两次输入的密码不一致！")
        else:
            with st.spinner("正在为您创建账号..."):
                db_manager = get_db_manager()  # 获取共享的数据库连接
                success, message = register_user(db_manager, username, password, email)
                if success:
                    st.success("✅ " + message)
                    time.sleep(2)
                    st.switch_page("pages/Login.py")
                else:
                    st.error("❌ " + message)

    st.markdown("---")
    if st.button("↩️ 返回登录", use_container_width=True):
        st.switch_page("pages/Login.py")

    st.markdown("</div>", unsafe_allow_html=True)


register_page()