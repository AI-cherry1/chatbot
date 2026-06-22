# 상담 챗봇 (Counseling Chatbot)

이 저장소는 상담용 답변을 사용자가 입력하면 AI가 말투를 다듬어 주는 간단한 Streamlit 앱입니다.

주요 기능
- 사용자가 작성한 기본 상담 답변을 주제(직장생활, 연애, 가족, 경제 등)에 맞춰 말투 스타일로 다듬음
- 최근 다듬은 답변을 히스토리로 표시

빠른 시작
1. 의존성 설치

```bash
pip install -r requirements.txt
```

2. 앱 실행

```bash
streamlit run streamlit_app.py
```

환경 변수
- OpenAI API 키가 필요합니다. 앱 실행 시 입력하거나 `.streamlit/secrets.toml`에 저장하세요.

라이선스
- 이 프로젝트는 LICENSE 파일의 조건을 따릅니다.

파일
- [streamlit_app.py](streamlit_app.py): 메인 앱 코드

문의
- 개선할 점이나 추가하고 싶은 기능이 있으면 이슈를 열어 주세요.
