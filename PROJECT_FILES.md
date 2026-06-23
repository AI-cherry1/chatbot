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

원하시면 특정 파일을 바로 열도록 더 링크 추가해 드립니다.
