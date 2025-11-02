# file: pages/Chatbot.py (已修改为工作流触发器)
import streamlit as st
import subprocess
import sys
import os
from src.utils.helpers import authenticated_page
from src.ui.style_utils import load_global_styles


def run_main_workflow():
    """
    执行 main.py 脚本并实时返回其输出。
    这是一个生成器函数，会逐行 yield 输出。
    """
    # 确保我们使用的是与Streamlit应用相同的Python环境
    python_executable = sys.executable

    # 获取项目根目录，并构建 main.py 的绝对路径
    # __file__ -> .../pages/Chatbot.py
    # os.path.dirname -> .../pages
    # os.path.dirname -> .../
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_script_path = os.path.join(project_root, "main.py")

    if not os.path.exists(main_script_path):
        yield "❌ **错误**: 找不到 'main.py' 文件。"
        return

    # 使用 Popen 启动子进程，以便我们可以实时读取输出
    process = subprocess.Popen(
        [python_executable, main_script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        bufsize=1,  # 行缓冲
        cwd=project_root  # 在项目根目录执行脚本，以确保相对路径正确
    )

    # 实时读取标准输出
    for line in iter(process.stdout.readline, ''):
        yield line.strip()

    process.stdout.close()

    # 等待进程结束并检查错误
    return_code = process.wait()
    if return_code != 0:
        # 如果有错误，读取并返回标准错误流的内容
        error_output = process.stderr.read()
        yield f"\n--- ❌ 脚本执行出错 (返回码: {return_code}) ---\n"
        yield error_output.strip()
    else:
        yield "\n--- ✅ 流程执行完毕 ---"

    process.stderr.close()


@authenticated_page
def chatbot_page():
    """
    一个AI助手页面，用于触发并监控后端的 main.py 工作流。
    """
    load_global_styles()
    user = st.session_state.get("user")

    # --- 页面标题 ---
    st.markdown("""
    <div class="card">
        <h1>⚙️ AI 工作流助手</h1>
        <p style="color: #7f8c8d;">在此处触发和监控系统核心的数据处理与分析工作流</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 移除模型选择的侧边栏 ---

    # --- 聊天会话状态初始化 ---
    if "workflow_messages" not in st.session_state:
        st.session_state.workflow_messages = [{"role": "assistant",
                                               "content": f"你好, {user.username}！我是您的工作流助手。\n\n输入任何内容（例如“开始今日分析”或“运行”）即可启动每日数据处理和推荐流程。"}]

    # --- 显示历史聊天记录 ---
    for msg in st.session_state.workflow_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)  # 使用markdown以支持格式化

    # --- 输入框及逻辑处理 ---
    if prompt := st.chat_input("输入 '运行' 来启动工作流..."):
        # 1. 将用户输入添加到会话历史并立即显示
        st.session_state.workflow_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. 准备执行工作流
        with st.chat_message("assistant"):
            st.info("✅ 指令已收到！正在启动系统主流程... 请稍候。")

            # 使用 st.empty() 创建一个占位符，用于实时更新日志输出
            log_placeholder = st.empty()

            full_log_output = ""
            try:
                # 实时显示工作流的输出
                for line in run_main_workflow():
                    # 将新日志行追加到完整日志中
                    full_log_output += line + "\n"
                    # 使用Markdown的代码块格式来显示日志，更美观
                    log_placeholder.markdown(f"```log\n{full_log_output}\n```")

            except Exception as e:
                full_log_output += f"❌ 前端调用时发生严重错误: {e}"
                log_placeholder.error(full_log_output)

        # 3. 将完整的日志输出保存到会话历史中
        st.session_state.workflow_messages.append({"role": "assistant", "content": f"```log\n{full_log_output}\n```"})


# 运行页面
chatbot_page()