import os
import streamlit as st
import pandas as pd

from datetime import datetime
from datetime import date
from datetime import timedelta

try:
    from streamlit_sortables import sort_items
except ImportError:
    sort_items = None

from core.export_manager import (
    build_export_download,
    normalize_article_upload_df,
    save_articles_file,
)
from core.news_collector import build_rss_query
from core.selection_manager import (
    ARTICLE_ID_COLUMN,
    SELECTED_COLUMN,
    apply_selection,
    ensure_article_ids,
    get_selected_article_ids,
    get_selected_articles,
)
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

if "selected_article_ids" not in st.session_state:
    st.session_state.selected_article_ids = set()

if "selected_article_order" not in st.session_state:
    st.session_state.selected_article_order = []

if "news_editor_version" not in st.session_state:
    st.session_state.news_editor_version = 0

if "generated_files" not in st.session_state:
    st.session_state.generated_files = []

if "generated_download" not in st.session_state:
    st.session_state.generated_download = None

if "manual_email_download" not in st.session_state:
    st.session_state.manual_email_download = None

st.title("📰 디지털자산 뉴스 클리핑")


def sync_selected_article_order(
    selected_article_ids,
    selected_rows
):

    selected_article_ids = {
        str(article_id)
        for article_id in selected_article_ids
    }
    current_order = [
        str(article_id)
        for article_id in st.session_state.selected_article_order
        if str(article_id) in selected_article_ids
    ]
    ordered_ids = set(current_order)

    for article_id in (
        selected_rows[ARTICLE_ID_COLUMN]
        .astype(str)
        .tolist()
    ):
        if (
            article_id in selected_article_ids
            and article_id not in ordered_ids
        ):
            current_order.append(article_id)
            ordered_ids.add(article_id)

    return current_order


def build_order_label(row):

    title = str(row.get("제목", ""))

    if len(title) > 72:
        title = title[:69] + "..."

    return (
        f"{row.get('출처', '')} | "
        f"{title} | "
        f"{row.get('날짜', '')} | "
        f"{str(row.get(ARTICLE_ID_COLUMN, ''))[:8]}"
    )


def render_selected_article_order(selected_rows):

    st.subheader("이메일 기사 순서")

    ordered_rows = selected_rows.copy()
    ordered_rows["_order_label"] = ordered_rows.apply(
        build_order_label,
        axis=1
    )
    label_by_id = dict(
        zip(
            ordered_rows[ARTICLE_ID_COLUMN].astype(str),
            ordered_rows["_order_label"]
        )
    )
    id_by_label = {
        label: article_id
        for article_id, label in label_by_id.items()
    }
    order_labels = [
        label_by_id[article_id]
        for article_id in st.session_state.selected_article_order
        if article_id in label_by_id
    ]

    if sort_items:
        sorted_labels = sort_items(
            order_labels,
            direction="vertical",
            key="selected_article_order_sort"
        )
        sorted_article_ids = [
            id_by_label[label]
            for label in sorted_labels
            if label in id_by_label
        ]
    else:
        st.caption(
            "드래그 정렬 컴포넌트가 설치되면 이 영역에서 "
            "기사를 드래그해 순서를 바꿀 수 있습니다."
        )
        fallback_df = ordered_rows[
            [
                ARTICLE_ID_COLUMN,
                "출처",
                "제목",
                "날짜",
            ]
        ].copy()
        fallback_df.insert(
            0,
            "순서",
            range(
                1,
                len(fallback_df) + 1
            )
        )
        edited_order_df = st.data_editor(
            fallback_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "순서": st.column_config.NumberColumn(
                    "순서",
                    min_value=1,
                    step=1
                ),
                ARTICLE_ID_COLUMN: None
            },
            disabled=[
                "출처",
                "제목",
                "날짜",
                ARTICLE_ID_COLUMN
            ],
            key="selected_article_order_editor"
        )
        sorted_article_ids = (
            edited_order_df
            .sort_values(
                "순서",
                kind="stable"
            )[ARTICLE_ID_COLUMN]
            .astype(str)
            .tolist()
        )

    if sorted_article_ids != st.session_state.selected_article_order:
        st.session_state.selected_article_order = sorted_article_ids
        st.session_state.generated_files = []
        st.session_state.generated_download = None
        st.session_state.manual_email_download = None

    return st.session_state.selected_article_order

# --------------------
# 파일 저장 모달
# --------------------

def render_save_dialog(file_type):

    extension_by_type = {
        "excel": "xlsx",
        "html": "html",
    }
    suffix_by_type = {
        "excel": "_daily_news",
        "html": "_daily_news_email",
    }

    default_file_name = (
        datetime.now().strftime("%Y%m%d")
        + suffix_by_type[file_type]
    )

    file_name = st.text_input(
        "저장 파일명",
        value=default_file_name
    )

    extension = extension_by_type[file_type]

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


@st.dialog("이메일 템플릿 저장")
def save_html_dialog():

    render_save_dialog("html")


@st.dialog("엑셀 파일 저장")
def save_excel_dialog():

    render_save_dialog("excel")

# --------------------
# 사이드바
# --------------------

st.sidebar.title("검색 이력")

history = load_history()

for item in history:
    st.sidebar.caption(item["time"])
    st.sidebar.write(item["title"])
    st.sidebar.divider()

manual_tab, upload_tab = st.tabs(
    [
        "뉴스 수집",
        "엑셀로 이메일 HTML 만들기",
    ]
)

# --------------------
# 검색 조건
# --------------------

with manual_tab:

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

        news_df = ensure_article_ids(news_df)

        st.session_state.news_df = news_df
        st.session_state.selected_df = pd.DataFrame()
        st.session_state.selected_article_ids = set()
        st.session_state.selected_article_order = []
        st.session_state.news_editor_version += 1
        st.session_state.generated_files = []
        st.session_state.generated_download = None
        st.session_state.manual_email_download = None

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
                st.session_state.selected_article_ids = set(
                    st.session_state.news_df[ARTICLE_ID_COLUMN]
                    .astype(str)
                    .tolist()
                )
                st.session_state.selected_article_order = (
                    st.session_state.news_df[ARTICLE_ID_COLUMN]
                    .astype(str)
                    .tolist()
                )
                st.session_state.news_editor_version += 1
                st.session_state.generated_files = []
                st.session_state.generated_download = None
                st.session_state.manual_email_download = None
                st.rerun()

        with col_unselect_all:
            if st.button("전체 해제"):
                st.session_state.selected_article_ids = set()
                st.session_state.selected_article_order = []
                st.session_state.news_editor_version += 1
                st.session_state.generated_files = []
                st.session_state.generated_download = None
                st.session_state.manual_email_download = None
                st.rerun()

        editor_df = apply_selection(
            st.session_state.news_df,
            st.session_state.selected_article_ids
        )

        with st.form(
            key=f"news_selection_form_{st.session_state.news_editor_version}"
        ):
            edited_df = st.data_editor(
                editor_df,
                use_container_width=True,
                hide_index=True,
                key=f"news_editor_{st.session_state.news_editor_version}",
                column_config={
                    SELECTED_COLUMN: st.column_config.CheckboxColumn(
                        "선택",
                        help="엑셀 또는 이메일 템플릿에 포함할 기사를 선택하세요."
                    ),
                    "링크": st.column_config.LinkColumn("링크"),
                    ARTICLE_ID_COLUMN: None
                },
                disabled=[
                    "날짜",
                    "제목",
                    "출처",
                    "링크",
                    ARTICLE_ID_COLUMN
                ]
            )

            selection_submitted = st.form_submit_button(
                "선택 적용",
                type="primary"
            )

        if selection_submitted:
            st.session_state.selected_article_ids = get_selected_article_ids(
                edited_df
            )
            st.session_state.generated_files = []
            st.session_state.generated_download = None
            st.session_state.manual_email_download = None
            selected_source_df = edited_df
        else:
            selected_source_df = editor_df

        selected_rows = selected_source_df[
            selected_source_df[SELECTED_COLUMN] == True
        ].copy()
        st.session_state.selected_article_order = sync_selected_article_order(
            st.session_state.selected_article_ids,
            selected_rows
        )

        if len(selected_rows) > 1:
            ordered_article_ids = render_selected_article_order(
                selected_rows
            )
        else:
            ordered_article_ids = st.session_state.selected_article_order

        selected_df = get_selected_articles(
            selected_source_df,
            ordered_article_ids=ordered_article_ids
        )

        if selected_df.empty:
            st.session_state.selected_article_order = []

        st.session_state.selected_df = selected_df

        st.info(f"선택된 기사 수: {len(selected_df)}건")

        if len(selected_df):

            if st.button("이메일 템플릿 만들기", type="primary"):
                st.session_state.generated_files = []
                st.session_state.generated_download = None

                with st.status(
                    "이메일 템플릿 생성 중입니다.",
                    expanded=True
                ) as status:
                    st.write("원문 링크 확인 및 HTML 생성 중...")

                    try:
                        st.session_state.manual_email_download = (
                            build_export_download(
                                selected_df,
                                file_name=(
                                    datetime.now().strftime("%Y%m%d")
                                    + "_daily_news_email"
                                ),
                                file_type="html"
                            )
                        )
                    except Exception as error:
                        status.update(
                            label="이메일 템플릿 생성 실패",
                            state="error",
                            expanded=True
                        )
                        st.error(
                            "이메일 템플릿 생성 중 오류가 발생했습니다: "
                            f"{error}"
                        )
                    else:
                        status.update(
                            label="이메일 템플릿 생성 완료",
                            state="complete",
                            expanded=False
                        )

            if st.session_state.manual_email_download:
                email_download = st.session_state.manual_email_download
                html_code = email_download["data"].decode("utf-8")

                st.code(
                    html_code,
                    language="html"
                )

                col_save_html, col_save_excel = st.columns(2)

                with col_save_html:
                    st.download_button(
                        label="html로 저장하기",
                        data=email_download["data"],
                        file_name=email_download["file_name"],
                        mime=email_download["mime"],
                        key="manual_email_html_download"
                    )

                with col_save_excel:
                    if st.button("엑셀로 저장하기"):
                        save_excel_dialog()

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

with upload_tab:

    uploaded_file = st.file_uploader(
        "엑셀 파일 업로드",
        type=["xlsx"]
    )

    upload_file_name = st.text_input(
        "HTML 파일명",
        value=datetime.now().strftime("%Y%m%d") + "_daily_news_email",
        key="upload_html_file_name"
    )

    if uploaded_file:

        try:
            upload_file_name = upload_file_name.strip()

            if not upload_file_name:
                raise ValueError("HTML 파일명을 입력하세요.")

            uploaded_df = pd.read_excel(
                uploaded_file
            )
            article_df = normalize_article_upload_df(
                uploaded_df
            )
            download = build_export_download(
                article_df,
                file_name=upload_file_name,
                file_type="html",
                url_resolver=lambda url: url
            )
        except Exception as error:
            st.error(f"엑셀 파일을 변환할 수 없습니다: {error}")
        else:
            html_code = download["data"].decode("utf-8")

            st.success(f"{len(article_df)}건을 이메일 HTML로 변환했습니다.")

            st.code(
                html_code,
                language="html"
            )

            st.download_button(
                label="html로 저장하기",
                data=download["data"],
                file_name=download["file_name"],
                mime=download["mime"],
                key="uploaded_excel_html_download"
            )
