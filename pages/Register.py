# file: pages/Register.py
import streamlit as st
import re
from src.database.database_manager import DatabaseManager
from src.auth.auth_utils import hash_password  # 从共享文件导入加密函数
from src.ui.style_utils import add_final_elegant_css,hide_sidebar_for_pre_login_pages  # 导入共享样式
from src.auth.auth_utils import hash_password, generate_captcha_challenge, verify_captcha

def is_valid_email(email: str) -> bool:
    """简单的邮箱格式验证"""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def register_user(username, password, email) -> (bool, str):
    """处理用户注册逻辑，【真实地】返回 (是否成功, 消息)"""
    db_manager = DatabaseManager(
        host='localhost', user='root', password='123456789',  # ❗️ 确保配置正确
        database='lottery_analysis_system', port=3309
    )
    try:
        # 1. 检查用户名和邮箱是否存在 (这部分逻辑是正确的)
        if db_manager.execute_query("SELECT id FROM users WHERE username = %s", (username,)):
            return False, "该用户名已被注册，请更换一个"
        if db_manager.execute_query("SELECT id FROM users WHERE email = %s", (email,)):
            return False, "该邮箱已被注册，请使用其他邮箱"

        # 2. ✅ --- 关键修复在这里 --- ✅
        # 密码加密
        hashed_pwd = hash_password(password)
        insert_query = "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)"

        # 将 execute_update 的返回结果 (True 或 False) 存入变量
        success = db_manager.execute_update(insert_query, (username, hashed_pwd, email))

        # 根据数据库操作的真实结果，返回不同的消息
        if success:
            return True, "恭喜！账号注册成功，请前往登录页面登录。"
        else:
            # execute_update 内部已经 st.error() 打印了详细错误，这里给用户一个通用提示
            return False, "注册失败，数据库写入时发生错误，请联系管理员。"

    except Exception as e:
        # 为了调试，我们可以在后台打印详细错误
        print(f"注册函数顶层异常: {e}")
        return False, f"注册过程发生未知错误: {e}"
    finally:
        if db_manager:
            db_manager.disconnect()


def register_page():
    """显示注册页面UI并集成我们自己的数学题人机验证"""
    st.set_page_config(page_title="Lotto-Pro - 注册", page_icon="📝", layout="centered")
    add_final_elegant_css()

    hide_sidebar_for_pre_login_pages()

    st.title("📝 Lotto-Pro 新用户注册")
    st.markdown("---")

    with st.form("register_form"):
        st.markdown("请填写以下信息来创建您的新账号。")
        username = st.text_input("用户名", placeholder="至少4个字符")
        email = st.text_input("电子邮箱", placeholder="我们将用于通知和密码找回")
        password = st.text_input("设置密码", type="password", placeholder="至少6个字符")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入您的密码")

        st.markdown("---")  # 添加分割线
        # 2. 调用函数来显示数学题和输入框
        user_captcha_answer = generate_captcha_challenge()

        submitted = st.form_submit_button("立即注册", use_container_width=True, type="primary")

    if submitted:
        # 3. 使用我们自己的验证函数来检查答案
        if not verify_captcha(user_captcha_answer):
            st.error("人机验证问题回答错误，请重试！")
        # 表单验证
        elif len(username) < 4:
            st.warning("用户名长度不能少于4个字符")
        elif not is_valid_email(email):
            st.warning("请输入有效的电子邮箱地址")
        elif len(password) < 6:
            st.warning("密码长度不能少于6个字符")
        elif password != confirm_password:
            st.error("两次输入的密码不一致！")
        else:
            # 所有验证通过，执行注册
            with st.spinner("正在为您创建账号..."):
                success, message = register_user(username, password, email)
                if success:
                    st.success(message)
                    # 注册成功后，可以清空输入框
                    st.session_state.captcha_input = ""
                else:
                    st.error(message)

    st.markdown("---")
    if st.button("已有账号？返回登录", use_container_width=True):
        st.switch_page("pages/Login.py")

register_page()