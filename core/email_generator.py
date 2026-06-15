from jinja2 import (
    Environment,
    FileSystemLoader
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
        report_date=report_date,
        articles=articles
    )

    return html