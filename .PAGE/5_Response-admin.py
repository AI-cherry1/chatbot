import streamlit as st
import db
import Main


def page_admin():
    st.title("🔐 관리자 대시보드")

    if not st.session_state.is_admin:
        st.error("관리자만 접근할 수 있습니다.")
        return

    if st.button("로그아웃", key="admin_logout"):
        Main.logout()
        return

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("답변 대기 중인 상담")

    pending = db.get_pending_consultations()
    if not pending:
        st.info("답변할 상담이 없습니다.")
    else:
        for p in pending:
            with st.expander(f"[{p['mode'].upper()}] {p['title']} - {p['username']}"):
                st.write(f"**상담 유형:** {p['mode']}")
                st.write(f"**질문:** {p['question']}")
                if p.get("blood_type"):
                    st.write(f"**혈액형:** {p['blood_type']}")
                if p.get("mbti"):
                    st.write(f"**MBTI:** {p['mbti']}")
                if p.get("age"):
                    st.write(f"**나이:** {p['age']}")
                if p.get("consideration"):
                    st.write(f"**고려사항:** {p['consideration']}")

                answer_content = st.text_area(
                    f"답변 작성 ({p['id']})",
                    height=160,
                    key=f"answer_{p['id']}",
                )

                if st.button(f"답변 저장하기", key=f"save_answer_{p['id']}"):
                    if not answer_content:
                        st.error("답변을 입력해주세요.")
                    else:
                        db.save_answer(p["id"], answer_content, st.session_state.user_id)
                        st.success("✅ 답변이 등록되었습니다.")

    st.markdown('</div>', unsafe_allow_html=True)
