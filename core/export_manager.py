import os
from io import BytesIO
from datetime import datetime

from core.email_generator import generate_email_html
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
    url_resolver=get_original_url
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
        html_content = generate_email_html(
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
    url_resolver=get_original_url
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
        url_resolver=url_resolver
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
