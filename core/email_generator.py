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
HEADER_IMAGE_URL = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781750322/header_blue_oguscv.svg"
)
FOOTER_IMAGE_URL = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781763779/footer_ver1.4_vual7u.png"
)
BIZ_BUTTON_IMAGE_URL = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781758969/BIZ-Btn_scm0dh.png"
)
BITHUMB_BIZ_URL = "https://www.bithumb.com/react/biz/intro"
TEMPLATE_DIR = os.path.join(
    PROJECT_ROOT,
    "templates"
)
KOREAN_WEEKDAYS = [
    "월",
    "화",
    "수",
    "목",
    "금",
    "토",
    "일",
]


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


def get_image_data_uri(
    image_file
):

    if not os.path.exists(image_file):
        return ""

    extension = os.path.splitext(
        image_file
    )[1].lower()
    mime_type = "image/png"

    if extension in [
        ".jpg",
        ".jpeg",
    ]:
        mime_type = "image/jpeg"

    with open(
        image_file,
        "rb"
    ) as f:
        encoded_image = base64.b64encode(
            f.read()
        ).decode("ascii")

    return f"data:{mime_type};base64,{encoded_image}"


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
        f"{parsed_date.year}."
        f"{parsed_date.month}."
        f"{parsed_date.day}"
        f" ({KOREAN_WEEKDAYS[parsed_date.weekday()]})"
    )


def parse_date_value(
    date_value
):

    if isinstance(
        date_value,
        datetime
    ):
        return date_value.date()

    if isinstance(
        date_value,
        date
    ):
        return date_value

    for date_format in [
        "%Y.%m.%d",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]:
        try:
            return datetime.strptime(
                str(date_value),
                date_format
            ).date()
        except ValueError:
            pass

    return None


def format_article_date(
    article_date
):

    parsed_date = parse_date_value(
        article_date
    )

    if parsed_date is None:
        return article_date

    return (
        f"({parsed_date.month}/"
        f"{parsed_date.day})"
    )


def build_articles(news_df):

    articles = []

    for _, row in news_df.iterrows():

        articles.append(
            {
                "title": row["제목"],
                "source": row["출처"],
                "date": format_article_date(
                    row["날짜"]
                ),
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
        header_image_url=HEADER_IMAGE_URL,
        footer_image_url=FOOTER_IMAGE_URL,
        biz_button_image_url=BIZ_BUTTON_IMAGE_URL,
        bithumb_biz_url=BITHUMB_BIZ_URL,
        articles=build_articles(news_df)
    )

    return html


def generate_email_body_html(
    news_df,
    report_date
):

    return render_news_template(
        "daily_news_email.html",
        news_df,
        report_date
    )
