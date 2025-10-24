# file: src/ui/style_utils.py
import streamlit as st
# ui全局

def add_final_elegant_css():
    st.markdown("""
    <style>
        /* --- 全局字体 --- */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&display=swap');
        html, body, [class*="st-"] { font-family: 'Noto Sans SC', sans-serif; }


        /* 将顶栏(stHeader)和主应用区(.stApp)都选上 */
        [data-testid="stHeader"], [data-testid="stToolbar"], .stApp {
            background-image: linear-gradient(to right top, #d1e4f5, #e3e0f7, #f3dff1, #fde0e8, #ffe3e3);
            background-attachment: fixed;
            background-size: cover;
        }

        /* 确保顶栏本身的背景是透明的，这样渐变才能显示出来 */
        [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: transparent;
        }


        [data-testid="stSidebar"] {
            /* ... 侧边栏样式保持不变 ... */
            background-color: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* ... 样式 (card, h1, stMetric) 保持不变 ... */
        .card {
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3 { color: #2c3e50; }
        [data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.9);
        }
    </style>
    """, unsafe_allow_html=True)

def hide_sidebar_for_pre_login_pages():
        """
        为所有预登录页面（登录、注册等）注入CSS，以彻底隐藏侧边栏及其切换按钮。
        """
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] { display: none; }
                [data-testid="stSidebarNavToggler"] { display: none; }
            </style>
            """,
            unsafe_allow_html=True
        )