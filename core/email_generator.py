import base64
import os
from datetime import date
from datetime import datetime

from jinja2 import (
    Environment,
    FileSystemLoader
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)
LOGO_IMAGE_FILE = os.path.join(
    PROJECT_ROOT,
    "assets",
    "bithumb_biz_logo.png"
)
TEMPLATE_DIR = os.path.join(
    PROJECT_ROOT,
    "templates"
)


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


def build_articles(news_df):

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

    return articles


def render_news_template(
    template_name,
    news_df,
    report_date
):

    env = Environment(
        loader=FileSystemLoader(
            TEMPLATE_DIR
        )
    )

    template = env.get_template(
        template_name
    )

    html = template.render(
        report_date=format_report_date(
            report_date
        ),
        logo_data_uri=get_logo_data_uri(),
        articles=build_articles(news_df)
    )

    return html


def generate_email_html(
    news_df,
    report_date
):

    return render_news_template(
        "daily_news.html",
        news_df,
        report_date
    )


def generate_email_body_html(
    news_df,
    report_date
):

    return render_news_template(
        "daily_news_email.html",
        news_df,
        report_date
    )
