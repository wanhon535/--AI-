import hashlib
import random
import streamlit as st


def hash_password(password: str) -> str:
    """对密码进行SHA-256加密"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_captcha_challenge():
    """
    生成一个简单的数学题验证码，并将答案存储在 session_state 中。
    """
    # 只有当 session_state 中没有答案时，才生成新题目
    if 'captcha_answer' not in st.session_state:
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        st.session_state.captcha_answer = num1 + num2
        st.session_state.captcha_question = f"请问 {num1} + {num2} 等于多少？"

    # 从 session_state 中获取问题并显示
    question = st.session_state.captcha_question
    user_answer = st.text_input(question, key="captcha_input")
    return user_answer


def verify_captcha(user_answer: str) -> bool:
    """
    验证用户的答案是否正确，并在验证后清除 session_state。
    """
    try:
        # 将用户输入转为整数进行比较
        correct_answer = st.session_state.get('captcha_answer', object())
        is_correct = int(user_answer) == correct_answer
    except (ValueError, TypeError):
        # 如果用户输入不是数字，则肯定不正确
        is_correct = False

    # 不论对错，都清除当前的题目，防止重复使用
    if 'captcha_answer' in st.session_state:
        del st.session_state.captcha_answer
    if 'captcha_question' in st.session_state:
        del st.session_state.captcha_question

    return is_correct

