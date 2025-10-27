# file: src/ui/style_utils.py (最终版)
import streamlit as st


def load_global_styles():
    """
    加载应用的所有全局CSS样式。
    这一个函数包含了登录页、主应用、侧边栏等所有部分的统一样式。
    """
    st.markdown("""
    <style>
        /* --- 1. 全局基础设置 --- */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&display=swap');
        html, body, [class*="st-"] { 
            font-family: 'Noto Sans SC', sans-serif; 
        }

        .stApp {
            background-image: linear-gradient(to right top, #d1e4f5, #e3e0f7, #f3dff1, #fde0e8, #ffe3e3);
            background-attachment: fixed;
            background-size: cover;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        /* --- 2. 登录/注册页面专属样式 --- */
        .login-card {
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 20px;
            padding: 2rem 3rem 2.5rem 3rem; 
            border: 1px solid rgba(255, 255, 255, 0.7);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            backdrop-filter: blur(15px);
            max-width: 500px;
            margin: 4rem auto 0 auto;
        }
        .login-card h2 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 2.5rem;
            margin-top: 0;
        }

        /* --- 3. 登录后主应用样式 --- */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.3);
        }

        [data-testid="stSidebarNav"] ul a[href*="Login"],
        [data-testid="stSidebarNav"] ul a[href*="Register"] {
            display: none;
        }

        .card {
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)


def hide_sidebar_for_pre_login_pages():
    """独立的辅助函数，用于在登录前完全隐藏侧边栏"""
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)