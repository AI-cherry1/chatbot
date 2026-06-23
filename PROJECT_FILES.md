프로젝트 주요 파일 인덱스

- [streamlit_app.py](streamlit_app.py)
- [db.py](db.py)
- [requirements.txt](requirements.txt)
- [.streamlit/config.toml](.streamlit/config.toml)
- [README.md](README.md)
- [LICENSE](LICENSE)

빠른 시작

1. 로컬 실행
```
python3 -m pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8503
```

2. 테스트 계정
- 일반: test / test123
- 관리자: admin / admin123

설명
- `streamlit_app.py`: 메인 앱 (회원가입/상담/결제/관리자)
- `db.py`: SQLite DB 초기화 및 CRUD

## 기능 명세
- `.PAGE/Requesting.py`: 상담 요청 전용 페이지
  - 상담 유형 선택
  - 제목, 내용 입력
  - 혈액형, MBTI, 나이, 고려사항 추가 입력 가능
  - 요청 저장 후 마이페이지로 이동
- `.PAGE/Loging.py`: 인증 및 계정 관리
  - 로그인
  - 회원가입
  - 내 정보 조회
  - 로그아웃
- `.PAGE/Mypage.py`: 사용자 마이페이지
  - 계정 정보 조회 및 비밀번호 변경
  - 결제 이력 조회
  - 상담 결과 / 헤이 답변 조회
- `.PAGE/Response.py`: 관리자 답변 페이지
  - 답변 대기 상담 확인
  - 답변 작성 및 저장
  - 사용자 요청 보조 정보 확인
- `db.py`: 데이터베이스 및 데이터 조회 함수
  - 사용자, 상담 요청, 답변, 결제 이력 관리

원하시면 특정 파일을 바로 열도록 더 링크 추가해 드립니다.
