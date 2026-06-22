import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="상담 답변 다듬기", page_icon="💼")

st.title("💼 상담 답변 다듬기 서비스")
st.write(
    "내가 만든 상담 답변을 기본으로 삼아 AI가 말투를 다듬어줍니다. "
    "연애, 직장생활, 경제, 가족 상담 등 다양한 상담 상황에 맞춰 자연스럽게 정리하세요."
)

openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("OpenAI API 키를 입력하면 상담 답변 다듬기를 시작할 수 있습니다.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    if "history" not in st.session_state:
        st.session_state.history = []

    with st.form("counseling_form"):
        st.subheader("기본 상담 답변 입력")
        topic = st.selectbox(
            "상담 주제",
            ["직장생활", "연애", "가족", "경제", "기타"],
        )
        style = st.selectbox(
            "말투 스타일",
            [
                "친절하고 공감형",
                "전문적이고 차분한",
                "편안하고 긍정적인",
                "간결하고 실용적인",
            ],
        )
        user_question = st.text_area(
            "상담자 질문 (선택)",
            placeholder="실제 상담자가 물어본 질문을 입력하면 결과가 더 자연스러워집니다.",
            height=100,
        )
        base_answer = st.text_area(
            "내가 만든 기본 답변",
            placeholder="여기에 상담자가 받게 될 기본 메시지를 입력하세요.",
            height=220,
        )
        submitted = st.form_submit_button("말투 다듬기")

    if submitted:
        if not base_answer.strip():
            st.warning("기본 답변을 입력해 주세요.")
        else:
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
