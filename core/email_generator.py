import base64
import os
from datetime import date
from datetime import datetime

from jinja2 import (
    Environment,
    FileSystemLoader
)

LOGO_IMAGE_FILE = "assets/bithumb_biz_logo.png"


def get_logo_data_uri(
    logo_file=LOGO_IMAGE_FILE
):

    if not os.path.exists(logo_file):
        return ""

    with open(
        logo_file,
        "rb"
    ) as f:
        encoded_logo = base64.b64encode(
            f.read()
        ).decode("ascii")

    return f"data:image/png;base64,{encoded_logo}"


def format_report_date(
    report_date
):

    if isinstance(
        report_date,
        datetime
    ):
        parsed_date = report_date.date()

    elif isinstance(
        report_date,
        date
    ):
        parsed_date = report_date

    else:
        parsed_date = None

        for date_format in [
            "%Y.%m.%d",
            "%Y-%m-%d",
            "%Y/%m/%d",
        ]:
            try:
                parsed_date = datetime.strptime(
                    str(report_date),
                    date_format
                ).date()
                break
            except ValueError:
                pass

    if parsed_date is None:
        return report_date

    return (
        f"[{parsed_date.month}/"
        f"{parsed_date.day}]"
    )


def generate_email_html(
    news_df,
    report_date
):

    env = Environment(
        loader=FileSystemLoader(
            "templates"
        )
    )

    template = env.get_template(
        "daily_news.html"
    )

    articles = []

    for _, row in news_df.iterrows():

        articles.append(
            {
                "title": row["제목"],
                "source": row["출처"],
                "date": row["날짜"],
                "link": row["링크"]
            }
        )

    html = template.render(
        report_date=format_report_date(
            report_date
        ),
        logo_data_uri=get_logo_data_uri(),
        articles=articles
    )

    return html
