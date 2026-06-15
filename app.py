import os
import streamlit as st
import pandas as pd

from datetime import datetime
from datetime import date
from datetime import timedelta

from core.export_manager import (
    build_export_download,
    save_articles_file,
)
from core.news_collector import build_rss_query
from core.settings import DEFAULT_QUERY
from core.rss_fetcher import fetch_news
from core.history_manager import (
    save_history,
    load_history
)

st.set_page_config(
    page_title="디지털자산 뉴스 클리핑",
    layout="wide"
)

if "news_df" not in st.session_state:
    st.session_state.news_df = pd.DataFrame()

if "selected_df" not in st.session_state:
    st.session_state.selected_df = pd.DataFrame()

if "generated_files" not in st.session_state:
    st.session_state.generated_files = []

if "generated_download" not in st.session_state:
    st.session_state.generated_download = None

st.title("📰 디지털자산 뉴스 클리핑")

# --------------------
# 파일 저장 모달
# --------------------

def render_save_dialog(file_type):

    default_file_name = (
        datetime.now().strftime("%Y%m%d")
        + "_daily_news"
    )

    file_name = st.text_input(
        "저장 파일명",
        value=default_file_name
    )

    extension = "xlsx" if file_type == "excel" else "html"

    save_mode = st.radio(
        "저장 방식",
        [
            "브라우저로 다운로드",
            "프로젝트 폴더에 저장",
        ],
        horizontal=True,
        key=f"save_mode_{file_type}"
    )

    output_dir = "exports"

    if save_mode == "프로젝트 폴더에 저장":
        output_dir = st.text_input(
            "저장 폴더",
            value="exports",
            key=f"output_dir_{file_type}"
        )

        st.caption(f"저장 경로: {output_dir}/{file_name}.{extension}")
    else:
        st.caption(
            "파일 생성 후 다운로드 버튼을 누르면 브라우저 기본 "
            "다운로드 폴더에 저장됩니다."
        )

    if st.button("파일 생성", type="primary"):

        selected_df = st.session_state.selected_df.copy()

        if selected_df.empty:
            st.warning("선택된 기사가 없습니다.")
            return

        file_name = file_name.strip()

        if not file_name:
            st.warning("저장 파일명을 입력하세요.")
            return

        output_dir = output_dir.strip()

        if save_mode == "프로젝트 폴더에 저장" and not output_dir:
            st.warning("저장 폴더를 입력하세요.")
            return

        with st.status(
            "파일 생성 중입니다.",
            expanded=True
        ) as status:
            st.write("원문 링크 확인 및 파일 생성 중...")

            try:
                if save_mode == "브라우저로 다운로드":
                    download = build_export_download(
                        selected_df,
                        file_name=file_name,
                        file_type=file_type
                    )
                else:
                    output_file = save_articles_file(
                        selected_df,
                        file_name=file_name,
                        file_type=file_type,
                        output_dir=output_dir
                    )
            except Exception as error:
                status.update(
                    label="파일 생성 실패",
                    state="error",
                    expanded=True
                )
                st.error(f"파일 생성 중 오류가 발생했습니다: {error}")
                return

            status.update(
                label="파일 생성 완료",
                state="complete",
                expanded=False
            )

        if save_mode == "브라우저로 다운로드":
            st.session_state.generated_download = download
            st.session_state.generated_files = []

            st.success("파일 생성 완료. 아래 다운로드 버튼을 눌러 저장하세요.")
            st.download_button(
                label=f"다운로드: {download['file_name']}",
                data=download["data"],
                file_name=download["file_name"],
                mime=download["mime"],
                key=f"download_{file_type}_{file_name}"
            )
        else:
            st.session_state.generated_download = None
            st.session_state.generated_files = [output_file]

            st.success(
                f"{output_file} 저장 완료"
            )


@st.dialog("엑셀 파일 저장")
def save_excel_dialog():

    render_save_dialog("excel")


@st.dialog("HTML 파일 저장")
def save_html_dialog():

    render_save_dialog("html")

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

# --------------------
# 뉴스 수집
# --------------------

if st.button("뉴스 수집"):

    with st.spinner("뉴스 수집 중..."):

        rss_query = build_rss_query(query)

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

        col_save_excel, col_save_html = st.columns(2)

        with col_save_excel:
            if st.button("엑셀로 저장하기"):
                save_excel_dialog()

        with col_save_html:
            if st.button("HTML로 저장하기"):
                save_html_dialog()

    else:

        st.warning("엑셀 또는 템플릿으로 뽑을 기사를 체크하세요.")

# --------------------
# 다운로드 버튼
# --------------------

if st.session_state.generated_download:

    download = st.session_state.generated_download

    st.subheader("생성 파일 다운로드")

    st.download_button(
        label=f"다운로드: {download['file_name']}",
        data=download["data"],
        file_name=download["file_name"],
        mime=download["mime"],
        key="latest_generated_download"
    )

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
