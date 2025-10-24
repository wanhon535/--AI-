# file: pages/Login.py
import streamlit as st
from src.database.database_manager import DatabaseManager
from src.model.user_models import User
from src.auth.auth_utils import hash_password
# 1. ✅ 导入我们需要的【全部】UI工具函数
from src.ui.style_utils import add_final_elegant_css, hide_sidebar_for_pre_login_pages


# --- 核心函数 (这部分保持不变) ---
def authenticate_user(username: str, password: str) -> User or None:
    db_manager = None
    try:
        db_manager = DatabaseManager(
            host='localhost', user='root', password='123456789',  # ❗️ 确保配置正确
            database='lottery_analysis_system', port=3309
        )
        if not db_manager.connect():
            st.error("数据库连接失败")
            return None

        query = "SELECT * FROM users WHERE username = %s"
        result = db_manager.execute_query(query, (username,))

        if not result: return None
        user_data = result[0]
        if user_data['password_hash'] == hash_password(password):
            update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s"
            db_manager.execute_update(update_query, (user_data['id'],))
            return User(**user_data)  # 使用 **kwargs 简化对象创建
        return None
    except Exception as e:
        st.error(f"登录过程出错: {str(e)}")
        return None
    finally:
        if db_manager:
            db_manager.disconnect()


# --- 登录页面UI与逻辑 ---
def login_page():
    """显示登录页面并处理所有逻辑"""
    # 2. ✅ 让登录页面自我管理其外观和行为
    st.set_page_config(page_title="Lotto-Pro - 登录", page_icon="🔮", layout="centered")
    add_final_elegant_css()
    hide_sidebar_for_pre_login_pages()  # 3. ✅ 这是最关键的一行修复！

    st.title("🔮 Lotto-Pro 智能分析系统")
    st.subheader("用户登录")
    st.markdown("---")

    with st.form("login_form"):
        username = st.text_input("用户名", placeholder="请输入您的用户名")
        password = st.text_input("密码", type="password", placeholder="请输入您的密码")

        col1, col2 = st.columns(2)
        with col1:
            login_submitted = st.form_submit_button("登录", use_container_width=True)
        with col2:
            register_clicked = st.form_submit_button("注册新账号", use_container_width=True)

    if login_submitted:
        if username and password:
            with st.spinner("正在验证..."):
                user = authenticate_user(username, password)
                if user and user.is_active:
                    st.session_state["user"] = user
                    st.session_state["logged_in"] = True
                    st.rerun()  # 登录成功后，让 app.py 重新接管
                elif user and not user.is_active:
                    st.error("您的账号已被禁用，请联系管理员")
                else:
                    st.error("用户名或密码错误")
        else:
            st.warning("请输入用户名和密码")

    if register_clicked:
        # 4. ✅ 修正跳转到注册页的正确路径
        st.switch_page("pages/Register.py")


# --- 主逻辑 ---
# 5. ✅ 简化文件结构，直接运行UI函数
login_page()