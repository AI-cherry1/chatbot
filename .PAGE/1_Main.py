import importlib.util
import os
import sys
from datetime import datetime

import streamlit as st

SCRIPT_DIR = os.path.dirname(__file__)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

st.set_page_config(page_title="상담 챗봇 헤이", page_icon="💬", layout="centered")

import db


def load_module(module_name, filename):
    path = os.path.join(SCRIPT_DIR, filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

Main = load_module("Main", "2_logging.py")
Registration = load_module("Registration", "3_Registration.py")
Response = load_module("Response", "5_Response-admin.py")
Mypage = load_module("Mypage", "4_Mypage.py")

# DB 초기화
db.init_db()
Main.init_auth_state()

if "consultation_type" not in st.session_state:
    st.session_state.consultation_type = None
if "consultation_id" not in st.session_state:
    st.session_state.consultation_id = None


def render_style():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Pen+Script&family=Nunito+Sans:wght@400;600;700&display=swap');
html, body, [data-testid='stAppViewContainer'] {
    background: linear-gradient(180deg, #fff7fb 0%, #eef7ff 100%);
    color: #4b2e34;
    font-family: 'Nunito Sans', sans-serif;
}
.block-container {
    padding-top: 24px;
    padding-bottom: 24px;
    max-width: 900px;
}
.app-card {
    background: rgba(255,255,255,0.96);
    border: 1px solid rgba(190,167,205,0.24);
    border-radius: 28px;
    box-shadow: 0 20px 60px rgba(131, 93, 156, 0.12);
    padding: 32px;
    margin-bottom: 24px;
}
.app-card h1, .app-card h2, .app-card h3 {
    font-family: 'Nanum Pen Script', cursive;
}
.app-hero {
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
    justify-content: space-between;
}
.app-hero .hey-avatar {
    width: 130px;
    height: 130px;
    border-radius: 32px;
    background: linear-gradient(135deg, #f4d7f1, #d8e6ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: #5f3f54;
    box-shadow: 0 18px 46px rgba(99, 67, 113, 0.14);
}
.app-hero .hey-avatar small {
    display: block;
    font-size: 0.9rem;
    color: #6f4b63;
}
.app-hero .hero-text {
    flex: 1;
    min-width: 260px;
}
.hero-text h1 {
    margin: 0;
    font-size: 2.6rem;
    letter-spacing: 0.02em;
    color: #5f3f54;
}
.hero-text p {
    margin-top: 12px;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #6e566c;
}
.mode-card {
    background: #fff;
    border-radius: 24px;
    border: 1px solid rgba(216, 185, 217, 0.45);
    padding: 22px;
    box-shadow: 0 12px 28px rgba(151, 113, 166, 0.08);
    min-height: 220px;
}
.mode-card h3 {
    margin-top: 0;
    margin-bottom: 12px;
}
.mode-card ul {
    padding-left: 18px;
    color: #7c5b76;
}
.mode-card li {
    margin-bottom: 8px;
}
.stButton>button {
    border-radius: 18px;
    padding: 12px 18px;
    font-weight: 700;
    background: linear-gradient(135deg, #ffdaed, #d2e7ff);
    color: #5f3f54;
    border: 1px solid rgba(172, 122, 162, 0.32);
    box-shadow: 0 14px 28px rgba(127, 86, 145, 0.12);
    transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 18px 32px rgba(127, 86, 145, 0.16);
}
.stButton>button:focus-visible {
    outline: 2px solid rgba(159, 104, 191, 0.35);
    outline-offset: 2px;
}
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div {
    border-radius: 18px !important;
    border: 1px solid rgba(206, 169, 212, 0.55) !important;
    background: #fffafc !important;
}
.stTextArea>div>div>textarea {
    min-height: 170px;
}
.stCheckbox>div,
.stRadio>div {
    margin-top: 8px;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Nanum Pen Script', cursive;
}
@media (max-width: 768px) {
    .app-hero {justify-content: center;}
    .app-hero .hey-avatar {margin-bottom: 16px;}
}
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    if st.session_state.is_admin:
        if st.sidebar.button("📊 관리자"):
            st.session_state.page = "admin"
            st.experimental_rerun()

    if st.session_state.user_id and not st.session_state.is_admin:
        if st.sidebar.button("🏠"):
            st.session_state.page = "home"
            st.experimental_rerun()
        if st.sidebar.button("🧾 마이페이지"):
            st.session_state.page = "mypage"
            st.experimental_rerun()
        if st.sidebar.button("🚪 로그아웃"):
            Main.logout()


def page_home():
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="app-hero">
          <div class="hey-avatar">헤이<br/><small>40대</small></div>
          <div class="hero-text">
            <h1>💬 상담 챗봇 — 헤이</h1>
            <p>지금은 상담 요청을 남기고, 헤이가 답변을 보내주는 흐름입니다.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.user_id:
        st.success(f"{st.session_state.username}님, 상담 요청을 남겨보세요.")

        st.markdown("---")
        st.subheader("상담 요청 남기기")

        consultation_type = st.selectbox(
            "상담 유형",
            ["", "정서/심리", "관계", "직장", "가족", "경제", "기타"],
            key="consultation_type",
        )
        title = st.text_input("제목", key="request_title")
        question = st.text_area("상담 내용", height=220, key="request_question")

        with st.expander("추가 정보 및 고려사항 (선택)"):
            blood_type = st.selectbox(
                "혈액형",
                ["", "A", "B", "AB", "O"],
                key="request_blood_type",
            )
            mbti = st.selectbox(
                "MBTI",
                ["", "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"],
                key="request_mbti",
            )
            age = st.number_input("나이", min_value=0, max_value=120, value=0, step=1, key="request_age")
            consideration = st.text_area(
                "추가 고려사항",
                placeholder="헤이가 답변할 때 함께 고려하면 좋은 내용을 입력하세요.",
                height=120,
                key="request_consideration",
            )

        if st.button("요청 저장하기", key="submit_request"):
            if not consultation_type:
                st.error("상담 유형을 선택해주세요.")
            elif not title.strip() or not question.strip():
                st.error("제목과 상담 내용을 입력해주세요.")
            else:
                blood_type_value = blood_type if blood_type else None
                mbti_value = mbti if mbti else None
                age_value = age if age > 0 else None
                db.create_consultation(
                    st.session_state.user_id,
                    consultation_type,
                    title.strip(),
                    question.strip(),
                    blood_type_value,
                    mbti_value,
                    age_value,
                    consideration.strip() if consideration else None,
                )
                st.success("상담 요청이 저장되었습니다. 마이페이지에서 확인해보세요.")
                st.session_state.page = "mypage"
                st.experimental_rerun()
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            Main.page_login()
        with col2:
            st.markdown('<div class="app-card">', unsafe_allow_html=True)
            st.subheader("아직 회원이 아니신가요?")
            st.write("간단한 회원가입으로 서비스를 이용하실 수 있습니다.")
            if st.button("회원가입하기", key="home_go_registration"):
                st.session_state.page = "registration"
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def page_mypage():
    Mypage.page_mypage()


def page_admin():
    Response.page_admin()


def main():
    render_style()
    render_sidebar()

    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "registration":
        Registration.page_registration()
    elif st.session_state.page == "mypage":
        page_mypage()
    elif st.session_state.page == "admin":
        page_admin()
    else:
        page_home()


if __name__ == "__main__":
    main()
