# 뉴스레터 프로젝트

이 저장소는 기존 Streamlit 기반 Python 앱과 새로 전환할 Next.js 앱을 함께 관리합니다.

## 폴더 구조

```text
.
├── python-newsletter/   # 기존 Streamlit 뉴스 클리핑 앱
└── next-newsletter/     # 신규 Next.js 뉴스레터 앱
```

## Python 앱 실행

```bash
cd python-newsletter
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/streamlit run app.py
```

## Next.js 앱 실행

```bash
cd next-newsletter
npm install
npm run dev
```

Next.js 앱은 Supabase 연동과 새 Figma 화면 구현을 위한 기본 골격만 준비되어 있습니다.

