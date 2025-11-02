# file: src/utils/helpers.py
import streamlit as st
from functools import wraps
from src.database.database_manager import DatabaseManager

# --- 1. 标准化的数据库连接管理器 ---
# 使用 @st.cache_resource 确保在整个用户会话中，数据库连接只被创建一次。
# 这是修复所有页面数据库连接问题的核心。
@st.cache_resource
def get_db_manager():
    """
    获取并缓存一个数据库管理器实例。
    此函数确保整个Streamlit会话中只有一个数据库连接对象。
    """
    try:
        db_manager = DatabaseManager(
            host='localhost',
            user='root',
            password='123456789', # ❗️ 请确保这里是您的正确密码
            database='lottery_analysis_system',
            port=3309
        )
        if db_manager.connect():
            print("Database connection successful.") # 在后台终端打印日志，便于调试
            return db_manager
        else:
            st.error("数据库连接失败！应用无法启动。")
            st.stop()
            return None
    except Exception as e:
        st.error(f"数据库初始化失败: {e}")
        st.stop()
        return None

# --- 2. 标准化的页面认证装饰器 ---
# 这是一个Python装饰器，可以应用到任何需要登录才能访问的页面函数上。
# 它统一了登录检查逻辑，让页面代码更干净。
def authenticated_page(page_func):
    """
    一个装饰器，用于保护需要登录才能访问的页面。
    如果用户未登录，则自动重定向到登录页面。
    """
    @wraps(page_func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get("logged_in"):
            st.warning("您需要登录才能访问此页面。")
            st.switch_page("pages/Login.py")
            st.stop() # 停止执行当前页面
        else:
            return page_func(*args, **kwargs)
    return wrapper


def get_algorithm_display_names():
    """
    返回一个字典，用于将后端的算法英文标识符映射为前端显示的中文名称。
    这是维护显示名称的唯一地方。
    """
    return {
        # --- 根据您的截图和项目结构推断 ---
        "FrequencyAnalysisAlgorithm": "频率分析算法",
        "HotColdNumberAlgorithm": "冷热号追踪算法",
        "OmissionValueAlgorithm": "遗漏值分析算法",
        "BayesianNumberPredictor": "贝叶斯号码预测器",
        "MarkovTransitionModel": "马尔可夫转移模型",
        "NumberGraphAnalyzer": "号码图关联分析",

        # --- 根据您的项目结构推断的其他可能存在的算法 ---
        "adaptive_meta_ensemble": "自适应元集成算法",
        "lottery_rl_agent": "强化学习代理",
        "neural_lottery_predictor": "神经网络预测器",
        "intelligent_pattern_recognizer": "智能模式识别器",
        "dynamic_ensemble_optimizer": "动态集成优化器",
        "real_time_feedback_learner": "实时反馈学习器",

        # --- 为了兼容性，可以添加一些通用或旧版本的名称 ---
        "v1.0-statistical": "v1.0-统计基础模型",
        "statistical_algorithms": "统计分析算法",
        "ml_algorithms": "机器学习算法",

        # --- 您可以根据 algorithm_configs 表中的实际情况随时在这里添加或修改 ---
    }