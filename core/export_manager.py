import os
from datetime import datetime

from core.email_generator import generate_email_html
from core.rss_fetcher import get_original_url


def prepare_export_df(
    selected_df,
    url_resolver=get_original_url
):

    export_df = selected_df.copy()

    export_df["링크"] = (
        export_df["링크"]
        .apply(url_resolver)
    )

    return export_df.astype(str)


def save_articles_file(
    selected_df,
    file_name,
    file_type,
    output_dir="exports",
    url_resolver=get_original_url
):

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    export_df = prepare_export_df(
        selected_df,
        url_resolver=url_resolver
    )

    if file_type == "excel":
        output_file = os.path.join(
            output_dir,
            f"{file_name}.xlsx"
        )

        export_df.to_excel(
            output_file,
            index=False
        )

        return output_file

    if file_type == "html":
        output_file = os.path.join(
            output_dir,
            f"{file_name}.html"
        )

        html_content = generate_email_html(
            export_df,
            datetime.now().strftime("%Y.%m.%d")
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(html_content)

        return output_file

    raise ValueError(f"지원하지 않는 파일 형식입니다: {file_type}")
