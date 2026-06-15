from urllib.parse import quote

import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_news(query):

    rss_url = (
        "https://news.google.com/rss/search?q="
        + quote(query)
        + "&hl=ko&gl=KR&ceid=KR:ko"
    )
    #Todo
    #영문기사
    #중복제거
    #카테고리화
    #키워드 고민 ...

    feed = feedparser.parse(rss_url)

    rows = []

    for item in feed.entries:

        title = item.title
        source = ""

        if " - " in title:
            title, source = title.rsplit(
                " - ",
                1
            )

        published = getattr(
            item,
            "published",
            ""
        )

        try:

            published = (
                pd.to_datetime(
                    published,
                    utc=True
                )
                .strftime(
                    "%Y-%m-%d"
                )
            )

        except Exception:

            pass

        rows.append(
            {
                "날짜": published,
                "제목": title,
                "출처": source,
                "링크": item.link,
            }
        )

    df = pd.DataFrame(rows)

    if len(df):

        df = (
            df
            .drop_duplicates(
                subset=["제목"]
            )
            .sort_values(
                "날짜",
                ascending=False
            )
        )

    return df


def get_original_url(
    google_url
):

    try:

        response = requests.get(
            google_url,
            timeout=10,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        canonical = soup.find(
            "link",
            rel="canonical"
        )

        if canonical:

            return canonical.get(
                "href"
            )

    except Exception:

        pass

    return google_url