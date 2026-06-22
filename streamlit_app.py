import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="상담 챗봇 - 헤이", page_icon="💬")


def _local_css():
    st.markdown(
        """
        <style>
        .hey-container {display:flex; align-items:flex-start; gap:16px; margin-top:10px;}
        .hey-avatar {width:120px; height:120px; border-radius:16px; background:linear-gradient(135deg,#f5c6d1,#ffd6e0); display:flex; align-items:center; justify-content:center; font-size:20px; color:#4b2e34; box-shadow:0 8px 20px rgba(0,0,0,0.12); animation: bob 3s ease-in-out infinite;}
        @keyframes bob {0%{transform:translateY(0)}50%{transform:translateY(-8px)}100%{transform:translateY(0)}}
        .hey-bubble {background:#ffffff; border-radius:16px; padding:12px 16px; box-shadow:0 6px 18px rgba(0,0,0,0.08); max-width:68%;}
        .hey-bubble p {margin:0; font-size:16px}
        .buttons-top {margin-top:18px}
        .btn {width:100%; padding:14px 18px; font-size:16px}
        </style>
        """,
        unsafe_allow_html=True,
    )


st.title("💬 상담 챗봇 — 헤이(Hey)")
st.write("헤이가 말투를 다듬어 드려요. 원하시는 버튼을 눌러 시작하세요.")

_local_css()

if "history" not in st.session_state:
    st.session_state.history = []
if "mode" not in st.session_state:
    st.session_state.mode = None
if "openai_client" not in st.session_state:
    st.session_state.openai_client = None

# Top: 캐릭터 + 말풍선
st.markdown(
    """
    <div class="hey-container">
      <div class="hey-avatar">헤이<br/><small>40대</small></div>
      <div class="hey-bubble"><p>안녕 나는 헤이(Hey)야..</p></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Buttons: 첫줄 두개, 아래줄 하나
col1, col2 = st.columns(2)
with col1:
    if st.button("기본", key="btn_basic"):
        st.session_state.mode = "basic"
with col2:
    if st.button("심층", key="btn_deep"):
        st.session_state.mode = "deep"

col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    if st.button("스페셜", key="btn_special"):
        st.session_state.mode = "special"


openai_api_key = st.text_input("OpenAI API Key (앱 상단 또는 여기에 입력)", type="password")
if openai_api_key and not st.session_state.openai_client:
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)


def show_counsel_form(client):
    st.subheader("기본 상담 답변 입력")
    topic = st.selectbox("상담 주제", ["직장생활", "연애", "가족", "경제", "기타"])
    style = st.selectbox(
        "말투 스타일",
        [
            "친절하고 공감형",
            "전문적이고 차분한",
            "편안하고 긍정적인",
            "간결하고 실용적인",
        ],
    )
    user_question = st.text_area("상담자 질문 (선택)", placeholder="실제 상담자가 물어본 질문을 입력하면 결과가 더 자연스러워집니다.", height=100)
    base_answer = st.text_area("내가 만든 기본 답변", placeholder="여기에 상담자가 받게 될 기본 메시지를 입력하세요.", height=220)
    if st.button("말투 다듬기(실행)"):
        if not base_answer.strip():
            st.warning("기본 답변을 입력해 주세요.")
            return
        if not client:
            st.warning("OpenAI API 키를 입력해 주세요.")
            return
        system_prompt = (
            "당신은 상담 전문가입니다. 아래 원본 답변의 내용을 그대로 유지하되, "
            f"'{topic}' 상담에 적합한 '{style}' 말투로 매끄럽고 공감 있게 다듬어주세요. "
            "불필요한 표현은 줄이고, 핵심 메시지를 명확하게 전달하세요."
        )
        user_prompt = f"상담자 질문: {user_question.strip() or '없음'}\n\n원본 답변:\n{base_answer.strip()}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        polished_answer = response.choices[0].message.content.strip()
        st.session_state.history.append(
            {
                "topic": topic,
                "style": style,
                "question": user_question,
                "base_answer": base_answer,
                "polished_answer": polished_answer,
            }
        )


if st.session_state.mode:
    st.markdown(f"**선택된 모드:** {st.session_state.mode}")
    client = st.session_state.openai_client
    show_counsel_form(client)

if st.session_state.history:
    st.markdown("---")
    st.subheader("최근 다듬어진 상담 답변")
    for item in reversed(st.session_state.history[-5:]):
        st.markdown(f"**주제:** {item['topic']}  ")
        st.markdown(f"**말투:** {item['style']}  ")
        if item["question"]:
            st.markdown(f"**상담자 질문:** {item['question']}  ")
        st.markdown("**원본 답변:**")
        st.code(item["base_answer"], language="text")
        st.markdown("**다듬어진 답변:**")
        st.code(item["polished_answer"], language="text")
        st.write("---")
