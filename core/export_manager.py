import os
from io import BytesIO
from datetime import datetime

from core.email_generator import (
    generate_email_body_html,
    generate_large_email_body_html,
    generate_orange_card_email_body_html,
    generate_orange_email_body_html,
    generate_orange_no_sidebar_email_body_html,
)
from core.rss_fetcher import (
    get_original_url,
    normalize_source,
)


EXPORT_TYPES = {
    "excel": {
        "extension": "xlsx",
        "mime": (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    },
    "html": {
        "extension": "html",
        "mime": "text/html",
    },
}
REQUIRED_ARTICLE_COLUMNS = [
    "날짜",
    "제목",
    "출처",
    "링크",
]


def normalize_article_upload_df(uploaded_df):

    article_df = uploaded_df.copy()
    article_df.columns = [
        str(column).strip()
        for column in article_df.columns
    ]

    missing_columns = [
        column
        for column in REQUIRED_ARTICLE_COLUMNS
        if column not in article_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "엑셀에 필요한 컬럼이 없습니다: "
            + ", ".join(missing_columns)
        )

    article_df = (
        article_df[REQUIRED_ARTICLE_COLUMNS]
        .dropna(how="all")
        .copy()
    )

    if article_df.empty:
        raise ValueError("변환할 기사가 없습니다.")

    article_df = article_df.fillna("")

    required_value_columns = [
        "제목",
        "링크",
    ]
    empty_required_values = (
        article_df[required_value_columns]
        .astype(str)
        .apply(lambda column: column.str.strip() == "")
        .any(axis=1)
    )

    if empty_required_values.any():
        raise ValueError("제목 또는 링크가 비어 있는 행이 있습니다.")

    return article_df.astype(str)


def prepare_export_df(
    selected_df,
    url_resolver=get_original_url,
    source_normalizer=normalize_source
):

    export_df = selected_df.copy()

    export_df["링크"] = (
        export_df["링크"]
        .apply(url_resolver)
    )

    if "출처" in export_df.columns:
        export_df["출처"] = export_df.apply(
            lambda row: source_normalizer(
                row["출처"],
                row["링크"]
            ),
            axis=1
        )

    return export_df.astype(str)


def get_export_file_name(
    file_name,
    file_type
):

    if file_type not in EXPORT_TYPES:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {file_type}")

    extension = EXPORT_TYPES[file_type]["extension"]

    return f"{file_name}.{extension}"


def build_export_download(
    selected_df,
    file_name,
    file_type,
    url_resolver=get_original_url,
    template_size="default"
):

    export_df = prepare_export_df(
        selected_df,
        url_resolver=url_resolver
    )

    if file_type == "excel":
        buffer = BytesIO()

        export_df.to_excel(
            buffer,
            index=False
        )

        data = buffer.getvalue()

    elif file_type == "html":
        if template_size in [
            "orange",
            "orange_sidebar",
        ]:
            html_generator = generate_orange_email_body_html
        elif template_size == "orange_no_sidebar":
            html_generator = generate_orange_no_sidebar_email_body_html
        elif template_size == "orange_card":
            html_generator = generate_orange_card_email_body_html
        elif template_size == "large":
            html_generator = generate_large_email_body_html
        elif template_size == "default":
            html_generator = generate_email_body_html
        else:
            raise ValueError(
                f"지원하지 않는 이메일 템플릿 크기입니다: {template_size}"
            )

        html_content = html_generator(
            export_df,
            datetime.now().strftime("%Y.%m.%d")
        )

        data = html_content.encode("utf-8")

    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {file_type}")

    return {
        "file_name": get_export_file_name(
            file_name,
            file_type
        ),
        "data": data,
        "mime": EXPORT_TYPES[file_type]["mime"],
    }


def save_articles_file(
    selected_df,
    file_name,
    file_type,
    output_dir="exports",
    url_resolver=get_original_url,
    template_size="default"
):

    output_dir = os.path.expanduser(output_dir)

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    download = build_export_download(
        selected_df,
        file_name=file_name,
        file_type=file_type,
        url_resolver=url_resolver,
        template_size=template_size
    )

    output_file = os.path.join(
        output_dir,
        download["file_name"]
    )

    with open(
        output_file,
        "wb"
    ) as f:
        f.write(download["data"])

    return output_file
