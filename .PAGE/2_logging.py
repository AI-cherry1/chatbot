import streamlit as st
import db


def init_auth_state():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "auth_message" not in st.session_state:
        st.session_state.auth_message = None


def logout():
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_admin = False
    st.session_state.page = "home"
    st.session_state.auth_message = None
    st.experimental_rerun()


def page_login():
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("로그인")

    login_username = st.text_input("아이디", key="login_id")
    login_password = st.text_input("비밀번호", type="password", key="login_pw")

    if st.button("로그인", key="login_submit"):
        user = db.get_user_by_username(login_username)
        if user and db.verify_password(user["password_hash"], login_password):
            st.session_state.user_id = user["id"]
            st.session_state.username = user["username"]
            st.session_state.is_admin = bool(user["is_admin"])
            st.session_state.auth_message = f"{user['username']}님 환영합니다."
            st.experimental_rerun()
        else:
            st.error("아이디 또는 비밀번호가 틀렸습니다.")

    st.write("")
    if st.button("회원가입하기", key="go_registration"):
        st.session_state.page = "registration"
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def page_account():
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("내 정보")

    if not st.session_state.user_id:
        st.info("로그인이 필요합니다.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    user = db.get_user_by_username(st.session_state.username)
    if not user:
        st.error("사용자 정보를 찾을 수 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown(f"**아이디:** {user['username']}")
    st.markdown(f"**성별:** {user.get('gender', '미등록')}")
    st.markdown(f"**나이대:** {user.get('age_group', '미등록')}")
    st.markdown(f"**권한:** {'관리자' if user.get('is_admin') else '일반 사용자'}")
    st.markdown(f"**가입일:** {user.get('created_at', '알 수 없음')}")

    if st.button("로그아웃", key="account_logout"):
        logout()

    st.markdown("</div>", unsafe_allow_html=True)
