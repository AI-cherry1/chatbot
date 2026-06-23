import streamlit as st
import db


def page_mypage():
    if not st.session_state.user_id:
        st.warning("로그인이 필요합니다.")
        return

    user = db.get_user_by_id(st.session_state.user_id)
    if not user:
        st.error("사용자 정보를 찾을 수 없습니다.")
        return

    st.title("마이페이지")
    st.markdown(f"**{user['username']}**님 반갑습니다.")

    tab_account, tab_payment, tab_results = st.tabs(["계정정보", "결제이력", "상담결과"])

    with tab_account:
        st.subheader("계정정보")
        st.write(f"**아이디:** {user['username']}")
        st.write(f"**성별:** {user.get('gender', '미등록')}")
        st.write(f"**나이대:** {user.get('age_group', '미등록')}")
        st.write(f"**권한:** {'관리자' if user.get('is_admin') else '일반 사용자'}")
        st.write(f"**가입일:** {user.get('created_at', '알 수 없음')}")

        st.markdown("---")
        st.subheader("비밀번호 변경")
        current_password = st.text_input("현재 비밀번호", type="password", key="mypage_current_password")
        new_password = st.text_input("새 비밀번호", type="password", key="mypage_new_password")
        confirm_password = st.text_input("새 비밀번호 확인", type="password", key="mypage_confirm_password")

        if st.button("비밀번호 변경", key="mypage_change_password"):
            if not current_password or not new_password or not confirm_password:
                st.error("모든 비밀번호 항목을 입력해주세요.")
            elif new_password != confirm_password:
                st.error("새 비밀번호가 일치하지 않습니다.")
            elif not db.verify_password(user['password_hash'], current_password):
                st.error("현재 비밀번호가 틀렸습니다.")
            else:
                db.update_user_password(user['id'], new_password)
                st.success("비밀번호가 변경되었습니다.")

    with tab_payment:
        st.subheader("결제이력")
        payments = db.get_user_payment_history(user['id'])
        if not payments:
            st.info("결제 내역이 없습니다.")
        else:
            for payment in payments:
                with st.expander(f"{payment['title']} - {payment['created_at'][:10]}"):
                    st.write(f"**결제 금액:** {payment['payment_amount']:,}원")
                    st.write(f"**결제 상태:** {payment['payment_status']}")
                    st.write(f"**결제 수단:** {payment.get('payment_method', '미정')}")
                    st.write(f"**상담 유형:** {payment['mode']}")
                    if payment.get('answer_status'):
                        st.write(f"**답변 상태:** {payment['answer_status']}")
                    if payment.get('expires_at'):
                        st.write(f"**조회 종료일:** {payment['expires_at']}")

    with tab_results:
        st.subheader("나의 질문 및 헤이 답변")
        consultations = db.get_user_consultation_details(user['id'])
        if not consultations:
            st.info("상담 요청 내역이 없습니다.")
        else:
            for c in consultations:
                with st.expander(f"[{c['mode']}] {c['title']} - {c['created_at'][:10]}"):
                    st.write(f"**상담 내용:** {c['question']}")
                    if c.get('blood_type'):
                        st.write(f"**혈액형:** {c['blood_type']}")
                    if c.get('mbti'):
                        st.write(f"**MBTI:** {c['mbti']}")
                    if c.get('age'):
                        st.write(f"**나이:** {c['age']}")
                    if c.get('consideration'):
                        st.write(f"**추가 고려사항:** {c['consideration']}")
                    st.markdown("---")
                    if c.get('answer_content'):
                        if c.get('is_deleted'):
                            st.warning("조회기간 만료된 답변입니다.")
                        else:
                            st.success("✅ 헤이의 답변")
                            st.write(c['answer_content'])
                            if c.get('answer_created_at'):
                                st.caption(f"답변 생성일: {c['answer_created_at']}")
                    else:
                        st.info("아직 답변이 도착하지 않았습니다.")
