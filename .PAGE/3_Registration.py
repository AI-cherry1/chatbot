import streamlit as st
import db


def page_registration():
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("회원가입")

    signup_username = st.text_input("아이디", key="signup_id")
    signup_password = st.text_input("비밀번호", type="password", key="signup_pw")
    signup_password_confirm = st.text_input("비밀번호 확인", type="password", key="signup_pw_confirm")

    gender = st.selectbox("성별", ["남", "여"], key="signup_gender")
    age_group = st.selectbox(
        "나이대",
        ["10대", "20대", "30대", "40대", "50대", "60대", "70대", "80대", "90대"],
        key="signup_age",
    )

    agree_privacy = st.checkbox("개인정보 수집 및 이용에 동의합니다", key="agree_privacy")
    agree_push = st.checkbox("푸시 알림 수신에 동의합니다", key="agree_push")

    if st.button("가입하기", key="signup_submit"):
        if signup_password != signup_password_confirm:
            st.error("비밀번호가 일치하지 않습니다.")
        elif not (agree_privacy and agree_push):
            st.error("필수 약관에 동의해주세요.")
        elif not signup_username or not signup_password:
            st.error("아이디와 비밀번호를 모두 입력해주세요.")
        else:
            user_id = db.create_user(signup_username, signup_password, gender, age_group)
            if user_id:
                st.success("회원가입이 완료되었습니다. 로그인 후 이용해 주세요.")
                st.session_state.page = "home"
                st.experimental_rerun()
            else:
                st.error("이미 존재하는 아이디입니다.")

    st.markdown("</div>", unsafe_allow_html=True)
