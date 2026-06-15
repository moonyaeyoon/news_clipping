from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd


def is_google_url(url):

    host = urlparse(url).netloc.lower()

    return (
        "google." in host
        or host.endswith("gstatic.com")
        or host.endswith("googleusercontent.com")
    )


def is_http_url(url):

    return urlparse(url).scheme in [
        "http",
        "https",
    ]


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
    google_url,
    requester=requests.get
):

    try:

        response = requester(
            google_url,
            timeout=10,
            allow_redirects=True,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        if (
            response.url
            and is_http_url(response.url)
            and not is_google_url(response.url)
        ):

            return response.url

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        canonical = soup.find(
            "link",
            rel="canonical"
        )

        if canonical:

            canonical_url = canonical.get(
                "href"
            )

            if (
                canonical_url
                and is_http_url(canonical_url)
                and not is_google_url(canonical_url)
            ):

                return canonical_url

        for link in soup.find_all(
            "a",
            href=True
        ):

            href = urljoin(
                google_url,
                link.get("href")
            )

            if (
                is_http_url(href)
                and not is_google_url(href)
            ):

                return href

    except Exception:

        pass

    return google_url
