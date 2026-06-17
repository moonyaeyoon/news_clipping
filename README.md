# 디지털자산 뉴스 클리핑

디지털자산, 가상자산, 코인 관련 뉴스를 Google News RSS에서 수집하고, 선택한 기사를 Excel 또는 HTML 이메일 템플릿으로 저장하는 Streamlit 앱입니다.

수동 조회 화면은 `app.py`에서 실행하고, 하루 두 번 자동 누적 수집은 `scheduler.py`에서 별도로 실행합니다.

## 주요 기능

- 기본 키워드로 뉴스 수집
- 기간별 기사 필터링
- 수집 기사 선택 및 전체 선택/해제
- 선택 기사 Excel 저장
- 선택 기사 HTML 이메일 템플릿 저장
- 매일 오전 9시 15분, 오후 3시 30분 자동 수집
- 자동 수집 결과 CSV 누적 저장

## 프로젝트 구조

```text
.
├── app.py                     # Streamlit 수동 조회 화면
├── scheduler.py               # 자동 수집 스케줄러
├── core/
│   ├── settings.py            # 검색어, 조회 기간, 저장 경로, 자동 실행 시간
│   ├── rss_fetcher.py         # Google News RSS 조회
│   ├── news_collector.py      # 자동 수집 및 CSV 누적 저장
│   ├── export_manager.py      # Excel/HTML 파일 저장
│   ├── email_generator.py     # HTML 이메일 생성
│   └── history_manager.py     # 수동 조회 이력 저장
├── templates/
│   └── daily_news_email.html  # 이메일 클라이언트용 HTML 템플릿
├── data/
│   ├── history.json           # 수동 조회 이력
│   └── news_archive.csv       # 자동 수집 누적 파일
├── exports/                   # 사용자가 저장한 Excel/HTML 파일
└── tests/                     # 단위 테스트
```

## 설치

이미 `news_venv` 가상환경이 있으면 바로 실행할 수 있습니다.

새 환경에서 설치하려면:

```bash
python3 -m venv news_venv
./news_venv/bin/pip install -r requirements.txt
```

## 수동 조회 앱 실행

```bash
./news_venv/bin/streamlit run app.py
```

실행 후 브라우저에서 Streamlit이 안내하는 주소로 접속합니다. 보통 다음 주소입니다.

```text
http://localhost:8501
```

앱에서 할 수 있는 일:

- 기간을 선택합니다.
- `뉴스 수집` 버튼을 누릅니다.
- 원하는 기사를 체크합니다.
- `엑셀로 저장하기` 또는 `이메일 템플릿 생성`을 누릅니다.
- 모달에서 파일명과 저장 방식을 선택하고 `파일 생성`을 누릅니다.

저장 방식은 두 가지입니다.

- `브라우저로 다운로드`: 파일을 메모리에서 만든 뒤 다운로드 버튼을 표시합니다. 다운로드 버튼을 누르면 브라우저 기본 다운로드 폴더에 저장됩니다.
- `프로젝트 폴더에 저장`: 입력한 폴더에 파일을 저장합니다. 기본값은 `exports`이며, 폴더가 없으면 자동 생성됩니다.

파일 생성 중에는 상태 박스가 표시됩니다.

`엑셀로 이메일 HTML 만들기` 탭에서는 이미 저장한 Excel 파일을 다시 업로드해 이메일 템플릿 HTML을 만들 수 있습니다.

- 업로드 Excel에는 `날짜`, `제목`, `출처`, `링크` 컬럼이 있어야 합니다.
- 변환이 완료되면 HTML 파일 다운로드 버튼이 표시됩니다.
- 같은 화면의 코드 블록에서 생성된 HTML 코드를 확인할 수 있습니다.

## 자동 수집 실행

자동 수집은 Streamlit 앱과 별도로 실행합니다.

```bash
./news_venv/bin/python scheduler.py
```

이 명령을 실행하면 `scheduler.py`가 계속 켜져 있으면서 정해진 시간까지 기다립니다. 시간이 되면 뉴스를 수집하고 `data/news_archive.csv`에 누적 저장합니다.

현재 자동 수집 시간:

- 오전 9시 15분
- 오후 3시 30분

터미널을 닫거나 프로세스를 종료하면 자동 수집도 멈춥니다.

## 자동 수집 CSV 누적 방식

자동 수집은 [core/news_collector.py](core/news_collector.py)의 `collect_news()`를 사용합니다.

작동 흐름:

1. [core/settings.py](core/settings.py)의 `DEFAULT_QUERY`를 읽습니다.
2. `RSS_LOOKBACK_DAYS` 값으로 `when:30d` 검색 조건을 붙입니다.
3. Google News RSS에서 기사를 가져옵니다.
4. 기존 `data/news_archive.csv`가 있으면 읽습니다.
5. 기존 기사와 새 기사를 합칩니다.
6. `제목 + 링크` 기준으로 중복을 제거합니다.
7. `날짜`, `수집시각` 기준으로 최신순 정렬합니다.
8. 다시 `data/news_archive.csv`에 저장합니다.

저장 컬럼:

```text
날짜, 제목, 출처, 링크, 수집시각
```

## 설정 변경

고정값은 [core/settings.py](core/settings.py)에 모아두었습니다.

```python
DEFAULT_QUERY = """
(디지털자산 OR 가상자산 OR 코인)
AND
(기업 OR 기관 OR 법인)
"""

RSS_LOOKBACK_DAYS = 30

NEWS_ARCHIVE_FILE = "data/news_archive.csv"

AUTO_COLLECT_TIMES = [
    "09:15",
    "15:30",
]
```

자주 바꿀 수 있는 값:

- 검색어: `DEFAULT_QUERY`
- 조회 범위: `RSS_LOOKBACK_DAYS`
- 자동 수집 시간: `AUTO_COLLECT_TIMES`
- 자동 누적 파일 위치: `NEWS_ARCHIVE_FILE`

## 파일 저장 방식

브라우저 다운로드 방식은 프로젝트 폴더에 파일을 남기지 않습니다. 파일 생성 후 화면에 표시되는 다운로드 버튼을 눌러 저장합니다.

프로젝트 폴더 저장 방식은 입력한 폴더에 파일을 생성합니다.

예:

```text
exports/파일명.xlsx
exports/파일명.html
```

`~/Downloads`처럼 홈 디렉터리를 포함한 경로도 사용할 수 있습니다.

## 출력 파일

프로젝트 폴더 저장 결과:

```text
exports/파일명.xlsx
exports/파일명.html
```

자동 수집 누적 결과:

```text
data/news_archive.csv
```

수동 조회 이력:

```text
data/history.json
```

## 테스트

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

문법 체크:

```bash
python3 -m py_compile app.py scheduler.py core/*.py
```

## 운영 메모

현재 자동 수집 방식은 `scheduler.py` 프로세스를 계속 켜두는 방식입니다. CPU를 계속 쓰는 구조는 아니고 대부분의 시간은 대기 상태입니다.

더 안정적으로 운영하려면 macOS `launchd`를 사용해 정해진 시간에만 한 번 실행하고 종료하는 방식으로 바꿀 수 있습니다. 그 경우 터미널을 계속 열어둘 필요가 없습니다.
