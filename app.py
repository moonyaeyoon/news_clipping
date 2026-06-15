import os
import streamlit as st
import pandas as pd

from datetime import datetime
from datetime import date
from datetime import timedelta

from core.email_generator import generate_email_html
from core.rss_fetcher import (
    fetch_news,
    get_original_url
)
from core.history_manager import (
    save_history,
    load_history
)

st.set_page_config(
    page_title="디지털자산 뉴스 클리핑",
    layout="wide"
)

MEDIA_LIST = [
    "연합뉴스",
    "한국경제",
    "매일경제",
    "동아일보",
    "조선일보",
    "중앙일보",
    "이데일리",
    "전자신문",
    "뉴스1",
    "머니투데이",
    "서울경제",
    "아시아경제",
    "파이낸셜뉴스",
    "조선비즈",
    "블록미디어",
    "디지털애셋",
    "코인데스크코리아",
    "데일리안",
    "뉴시스",
    "헤럴드경제",
    "디지털타임스"
]

DEFAULT_QUERY = """
(디지털자산 OR 가상자산 OR 코인)
AND
(기업 OR 기관 OR 법인)
"""

if "news_df" not in st.session_state:
    st.session_state.news_df = pd.DataFrame()

if "selected_df" not in st.session_state:
    st.session_state.selected_df = pd.DataFrame()

if "generated_files" not in st.session_state:
    st.session_state.generated_files = []

st.title("📰 디지털자산 뉴스 클리핑")

# --------------------
# 파일 저장 모달
# --------------------

@st.dialog("선택 기사 저장")
def save_selected_articles_dialog():

    default_file_name = (
        datetime.now().strftime("%Y%m%d")
        + "_daily_news"
    )

    file_name = st.text_input(
        "저장 파일명",
        value=default_file_name
    )

    output_options = st.multiselect(
        "생성할 파일",
        [
            "Excel",
            "HTML 이메일"
        ],
        default=[
            "Excel",
            "HTML 이메일"
        ]
    )

    st.caption(f"엑셀 저장 경로: exports/{file_name}.xlsx")
    st.caption(f"HTML 저장 경로: exports/{file_name}.html")

    if st.button("저장 실행"):

        selected_df = st.session_state.selected_df.copy()

        if selected_df.empty:
            st.warning("선택된 기사가 없습니다.")
            return

        if not output_options:
            st.warning("생성할 파일 형식을 선택하세요.")
            return

        os.makedirs(
            "exports",
            exist_ok=True
        )

        generated_files = []

        export_base_df = selected_df.copy()

        export_base_df["링크"] = (
            export_base_df["링크"]
            .apply(get_original_url)
        )

        export_base_df = (
            export_base_df
            .astype(str)
        )

        if "Excel" in output_options:

            excel_file = f"exports/{file_name}.xlsx"

            export_base_df.to_excel(
                excel_file,
                index=False
            )

            generated_files.append(excel_file)

        if "HTML 이메일" in output_options:

            html_content = generate_email_html(
                export_base_df,
                datetime.now().strftime("%Y.%m.%d")
            )

            html_file = f"exports/{file_name}.html"

            with open(
                html_file,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(html_content)

            generated_files.append(html_file)

        st.session_state.generated_files = generated_files

        st.success(
            f"{len(generated_files)}개 파일 생성 완료"
        )

# --------------------
# 사이드바
# --------------------

st.sidebar.title("검색 이력")

history = load_history()

for item in history:
    st.sidebar.caption(item["time"])
    st.sidebar.write(item["title"])
    st.sidebar.divider()

# --------------------
# 검색 조건
# --------------------

query = DEFAULT_QUERY

with st.expander(
    "현재 검색 조건",
    expanded=False
):
    st.code(DEFAULT_QUERY)

# --------------------
# 언론사 선택
# --------------------

st.subheader("언론사 선택")

selected_media = []

media_cols = st.columns(4)

for idx, media in enumerate(MEDIA_LIST):
    with media_cols[idx % 4]:
        if st.checkbox(
            media,
            value=media in [
                "연합뉴스",
                "한국경제",
                "매일경제",
                "동아일보",
                "조선일보",
                "중앙일보",
                "이데일리",
                "뉴스1"
            ],
            key=f"media_{media}"
        ):
            selected_media.append(media)

# --------------------
# 기간 설정
# --------------------

st.subheader("기간 설정")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "시작일",
        value=date.today() - timedelta(days=7)
    )

with col2:
    end_date = st.date_input(
        "종료일",
        value=date.today()
    )

max_articles = st.number_input(
    "최대 기사 수",
    min_value=10,
    max_value=150,
    value=30,
    step=10
)

# --------------------
# 뉴스 수집
# --------------------

if st.button("뉴스 수집"):

    with st.spinner("뉴스 수집 중..."):

        rss_query = query + " when:30d"

        news_df = fetch_news(rss_query)

    if len(news_df):

        news_df["filter_date"] = pd.to_datetime(
            news_df["날짜"],
            errors="coerce"
        )

        news_df = news_df[
            (
                news_df["filter_date"].dt.date >= start_date
            )
            &
            (
                news_df["filter_date"].dt.date <= end_date
            )
        ]

        news_df = news_df.drop(
            columns=["filter_date"]
        )

        if selected_media:
            news_df = news_df[
                news_df["출처"].isin(selected_media)
            ]

        news_df = news_df.head(max_articles)

    news_df = news_df.copy()

    if "선택" not in news_df.columns:
        news_df.insert(0, "선택", False)

    st.session_state.news_df = news_df
    st.session_state.selected_df = pd.DataFrame()
    st.session_state.generated_files = []

    save_history(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": f"{len(news_df)}건 수집"
        }
    )

    st.success(f"{len(news_df)}건 수집")

# --------------------
# 수집 결과 선택
# --------------------

if not st.session_state.news_df.empty:

    st.subheader("수집 기사 선택")

    col_select_all, col_unselect_all = st.columns(2)

    with col_select_all:
        if st.button("전체 선택"):
            temp_df = st.session_state.news_df.copy()
            temp_df["선택"] = True
            st.session_state.news_df = temp_df
            st.rerun()

    with col_unselect_all:
        if st.button("전체 해제"):
            temp_df = st.session_state.news_df.copy()
            temp_df["선택"] = False
            st.session_state.news_df = temp_df
            st.rerun()

    edited_df = st.data_editor(
        st.session_state.news_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "선택": st.column_config.CheckboxColumn(
                "선택",
                help="엑셀 또는 이메일 템플릿에 포함할 기사를 선택하세요."
            ),
            "링크": st.column_config.LinkColumn("링크")
        },
        disabled=[
            "날짜",
            "제목",
            "출처",
            "링크"
        ]
    )

    st.session_state.news_df = edited_df

    selected_df = edited_df[
        edited_df["선택"] == True
    ].drop(
        columns=["선택"]
    )

    st.session_state.selected_df = selected_df

    st.info(f"선택된 기사 수: {len(selected_df)}건")

    if len(selected_df):

        if st.button("선택 기사 저장"):
            save_selected_articles_dialog()

    else:

        st.warning("엑셀 또는 템플릿으로 뽑을 기사를 체크하세요.")

# --------------------
# 다운로드 버튼
# --------------------

if st.session_state.generated_files:

    st.subheader("생성 파일 다운로드")

    for file_path in st.session_state.generated_files:

        with open(
            file_path,
            "rb"
        ) as f:

            st.download_button(
                label=f"다운로드: {os.path.basename(file_path)}",
                data=f.read(),
                file_name=os.path.basename(file_path)
            )