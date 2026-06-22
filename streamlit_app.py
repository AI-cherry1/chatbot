import streamlit as st
import db
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="상담 챗봇 헤이", page_icon="💬", layout="wide")

# DB 초기화
db.init_db()

# 세션 상태 초기화
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "page" not in st.session_state:
    st.session_state.page = "home"

# CSS
st.markdown("""
<style>
.hey-avatar {
    width: 120px; height: 120px; border-radius: 16px;
    background: linear-gradient(135deg, #f5c6d1, #ffd6e0);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; color: #4b2e34; box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    animation: bob 3s ease-in-out infinite;
}
@keyframes bob {
    0% {transform: translateY(0)}
    50% {transform: translateY(-8px)}
    100% {transform: translateY(0)}
}
</style>
""", unsafe_allow_html=True)

def logout():
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_admin = False
    st.session_state.page = "home"
    st.rerun()

def page_login():
    """로그인/가입 페이지"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("로그인")
        login_username = st.text_input("아이디", key="login_id")
        login_password = st.text_input("비밀번호", type="password", key="login_pw")
        
        if st.button("로그인"):
            user = db.get_user_by_username(login_username)
            if user and db.verify_password(user["password_hash"], login_password):
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]
                st.session_state.is_admin = user["is_admin"]
                st.success(f"환영합니다, {login_username}님!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 틀렸습니다.")
    
    with col2:
        st.subheader("회원가입")
        signup_username = st.text_input("아이디", key="signup_id")
        signup_password = st.text_input("비밀번호", type="password", key="signup_pw")
        signup_password_confirm = st.text_input("비밀번호 확인", type="password", key="signup_pw_confirm")
        
        gender = st.selectbox("성별", ["남", "여"])
        age_group = st.selectbox("나이대", ["10대", "20대", "30대", "40대", "50대", "60대", "70대", "80대", "90대"])
        
        agree_privacy = st.checkbox("개인정보 수집 및 이용에 동의합니다")
        agree_push = st.checkbox("푸시 알림 수신에 동의합니다")
        
        if st.button("가입하기"):
            if signup_password != signup_password_confirm:
                st.error("비밀번호가 일치하지 않습니다.")
            elif not (agree_privacy and agree_push):
                st.error("필수 약관에 동의해주세요.")
            else:
                user_id = db.create_user(signup_username, signup_password, gender, age_group)
                if user_id:
                    st.success("회원가입이 완료되었습니다. 로그인해주세요.")
                else:
                    st.error("이미 존재하는 아이디입니다.")
    
    st.markdown("---")
    st.info("**보안 안내:** 모든 상담 정보는 암호화되어 철저하게 보호됩니다.")

def page_home():
    """메인 페이지"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💬 상담 챗봇 — 헤이(Hey)")
    with col2:
        if st.session_state.user_id:
            st.write(f"**{st.session_state.username}**님")
            if st.button("로그아웃"):
                logout()
    
    if not st.session_state.user_id:
        page_login()
    else:
        # 로그인 후 메인 페이지
        st.markdown("""
        <div class="hey-avatar" style="margin: 20px 0;">헤이<br/><small>40대 여성</small></div>
        """, unsafe_allow_html=True)
        
        st.markdown("**안녕 나는 헤이(Hey)야.**  \n당신의 고민을 들어주고 따뜻한 답변을 드릴게요.")
        
        st.markdown("---")
        st.subheader("상담 모드 선택")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 📝 기본
            - 500자 이내
            - 1회 답변
            - 가격: 5,000원
            """)
            if st.button("기본 선택", key="mode_basic"):
                st.session_state.page = "consultation"
                st.session_state.mode = "basic"
                st.rerun()
        
        with col2:
            st.markdown("""
            ### 🔍 심층
            - 2,000자 이상
            - 1회 추가 질문 가능
            - 가격: 15,000원
            """)
            if st.button("심층 선택", key="mode_deep"):
                st.session_state.page = "consultation"
                st.session_state.mode = "deep"
                st.rerun()
        
        col3, col4, col5 = st.columns([1, 1, 1])
        with col4:
            st.markdown("""
            ### ⭐ 스페셜
            - 기본+심층+실시간채팅
            - 최대 500자×3회
            - 가격: 30,000원
            """)
            if st.button("스페셜 선택", key="mode_special"):
                st.session_state.page = "consultation"
                st.session_state.mode = "special"
                st.rerun()

def page_consultation():
    """상담 신청 페이지"""
    st.title(f"상담 신청 — {st.session_state.mode.upper()}")
    
    if st.button("← 뒤로가기"):
        st.session_state.page = "home"
        st.rerun()
    
    title = st.text_input("상담 제목")
    question = st.text_area("상담 내용", height=250)
    
    mode_info = {
        "basic": {"limit": 500, "price": 5000},
        "deep": {"limit": 2000, "price": 15000},
        "special": {"limit": 1500, "price": 30000}
    }
    
    info = mode_info[st.session_state.mode]
    st.info(f"**글자 수 제한:** {info['limit']}자 이내  \n**상담료:** {info['price']:,}원")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("상담 신청하기"):
            if not title or not question:
                st.error("제목과 내용을 입력해주세요.")
            elif len(question) > info["limit"]:
                st.error(f"글자 수가 초과되었습니다. ({len(question)}/{info['limit']})")
            else:
                consultation_id = db.create_consultation(
                    st.session_state.user_id,
                    title,
                    question,
                    st.session_state.mode,
                    info["price"]
                )
                st.session_state.consultation_id = consultation_id
                st.session_state.page = "payment"
                st.rerun()

def page_payment():
    """결제 페이지"""
    st.title("결제하기")
    
    if st.button("← 뒤로가기"):
        st.session_state.page = "consultation"
        st.rerun()
    
    mode_info = {
        "basic": {"limit": 500, "price": 5000},
        "deep": {"limit": 2000, "price": 15000},
        "special": {"limit": 1500, "price": 30000}
    }
    
    price = mode_info[st.session_state.mode]["price"]
    
    st.markdown(f"### 결제 금액: **{price:,}원**")
    
    payment_method = st.radio("결제 수단 선택", ["카카오페이", "애플페이", "계좌이체"])
    
    agree_tos = st.checkbox("결제 약관에 동의합니다")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("결제하기"):
            if not agree_tos:
                st.error("약관에 동의해주세요.")
            else:
                db.mark_payment_completed(st.session_state.consultation_id, payment_method)
                st.success(f"✅ 결제 완료!\n\n📌 **1일 이내에 답변을 받아보세요.**\n\n앱 알림을 확인해주세요.")
                st.info(f"결제 수단: {payment_method}\n결제 금액: {price:,}원")
                
                if st.button("상담이력 확인"):
                    st.session_state.page = "history"
                    st.rerun()

def page_history():
    """상담이력 조회"""
    st.title("상담이력")
    
    if st.button("← 뒤로가기"):
        st.session_state.page = "home"
        st.rerun()
    
    consultations = db.get_user_consultations(st.session_state.user_id)
    
    if not consultations:
        st.info("상담이력이 없습니다.")
    else:
        for c in consultations:
            expires_at = datetime.fromisoformat(c["expires_at"])
            is_expired = datetime.now() > expires_at
            
            with st.expander(f"[{c['mode'].upper()}] {c['title']} - {c['created_at'][:10]}"):
                st.write(f"**결제 금액:** {c['payment_amount']:,}원")
                st.write(f"**모드:** {c['mode']}")
                
                answer = db.get_answer(c["id"])
                if answer:
                    if answer["is_deleted"] or is_expired:
                        st.warning("조회기간 만료되었습니다.")
                    else:
                        st.success("✅ 답변 완료")
                        if st.button(f"답변 보기", key=f"view_{c['id']}"):
                            st.write(answer["content"])
                else:
                    st.info("⏳ 답변 대기 중...")

def page_admin():
    """관리자 대시보드"""
    st.title("🔐 관리자 대시보드")
    
    if not st.session_state.is_admin:
        st.error("관리자만 접근할 수 있습니다.")
        return
    
    if st.button("로그아웃"):
        logout()
    
    st.subheader("답변 대기 중인 상담")
    
    pending = db.get_pending_consultations()
    
    if not pending:
        st.info("답변할 상담이 없습니다.")
    else:
        for p in pending:
            with st.expander(f"[{p['mode'].upper()}] {p['title']} - {p['username']}"):
                st.write(f"**질문:** {p['question']}")
                st.write(f"**모드:** {p['mode']}")
                
                answer_content = st.text_area(f"답변 작성 ({p['id']})", height=150, key=f"answer_{p['id']}")
                
                if st.button(f"AI 검증 후 답변 전송", key=f"verify_{p['id']}"):
                    if not answer_content:
                        st.error("답변을 입력해주세요.")
                    else:
                        db.save_answer(p["id"], answer_content, st.session_state.user_id)
                        st.success("✅ 답변이 사용자에게 전송되었습니다.")

# 라우팅
if __name__ == "__main__":
    if st.session_state.is_admin:
        if st.sidebar.button("📊 관리자"):
            st.session_state.page = "admin"
    
    if st.session_state.user_id and not st.session_state.is_admin:
        col1, col2, col3 = st.sidebar.columns(3)
        with col1:
            if st.button("🏠"):
                st.session_state.page = "home"
        with col2:
            if st.button("📋"):
                st.session_state.page = "history"
        with col3:
            if st.button("🚪"):
                logout()
    
    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "consultation":
        page_consultation()
    elif st.session_state.page == "payment":
        page_payment()
    elif st.session_state.page == "history":
        page_history()
    elif st.session_state.page == "admin":
        page_admin()
    else:
        page_home()
