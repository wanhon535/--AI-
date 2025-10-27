# file: app.py (新的应用主入口)
import streamlit as st
import extra_streamlit_components as stx

from src.database.database_manager import DatabaseManager
from src.model.user_models import User
from datetime import datetime

# --- 1. 统一的页面配置 ---
# st.set_page_config 应该只在主入口文件中调用一次
st.set_page_config(
    page_title="Lotto-Pro 智能分析系统",
    page_icon="🔮",
    layout="wide"
)


cookies = stx.CookieManager()


def restore_session_from_cookie():
    # ... (此函数内部逻辑不变)
    if "logged_in" in st.session_state and st.session_state.logged_in:
        return

    username = cookies.get('username')
    expires_at_str = cookies.get('expires_at')

    if not username or not expires_at_str:
        return

    try:
        expires_at = datetime.fromisoformat(expires_at_str)
        if datetime.now() > expires_at:
            cookies.delete('username')
            cookies.delete('expires_at')
            return
    except ValueError:
        cookies.delete('username')
        cookies.delete('expires_at')
        return

    db_manager = DatabaseManager(host='localhost', user='root', password='123456789',
                                 database='lottery_analysis_system', port=3309)
    if db_manager.connect():
        try:
            query = "SELECT id, username, email, is_active, last_login FROM users WHERE username = %s"
            result = db_manager.execute_query(query, (username,))
            if result:
                user_data = result[0]
                st.session_state.user = User(**user_data)
                st.session_state.logged_in = True
        except Exception as e:
            st.error(f"从Cookie恢复会话时出错: {e}")
        finally:
            db_manager.disconnect()

def main():
    restore_session_from_cookie()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.switch_page("pages/Login.py")
    else:
        st.switch_page("pages/Home.py")

if __name__ == "__main__":
    main()


