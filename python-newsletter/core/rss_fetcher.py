import json
import re
from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd

KNOWN_MEDIA_NAMES = [
    "연합뉴스",
    "한국경제",
    "매일경제",
    "동아일보",
    "조선일보",
    "중앙일보",
    "이데일리",
    "전자신문",
    "뉴스1",
    "머니투데이",
    "서울경제",
    "아시아경제",
    "파이낸셜뉴스",
    "조선비즈",
    "블록미디어",
    "디지털애셋",
    "코인데스크코리아",
    "데일리안",
    "뉴시스",
    "헤럴드경제",
    "디지털타임스",
    "매경이코노미",
]

DAUM_SOURCES = {
    "v.daum.net",
    "daum.net",
    "Daum",
    "다음뉴스",
}
SOURCE_NAME_OVERRIDES = {
    "2news.co.kr": "에너지 뉴스",
    "www.2news.co.kr": "에너지 뉴스",
}


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


def clean_source_name(source):

    return str(source or "").strip()


def normalize_known_media_source(source):

    cleaned_source = clean_source_name(source)
    override_source = SOURCE_NAME_OVERRIDES.get(
        cleaned_source.lower()
    )

    if override_source:
        return override_source

    for media_name in KNOWN_MEDIA_NAMES:
        if (
            cleaned_source == media_name
            or cleaned_source.startswith(f"{media_name} ")
        ):
            return media_name

    return cleaned_source


def extract_publisher_from_html(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    meta_selectors = [
        {
            "property": "og:article:author",
        },
        {
            "name": "article:author",
        },
        {
            "property": "dable:item_id",
        },
        {
            "property": "og:site_name",
        },
    ]

    for selector in meta_selectors:
        meta = soup.find(
            "meta",
            attrs=selector
        )

        if (
            meta
            and meta.get("content")
        ):
            publisher = normalize_known_media_source(
                meta.get("content")
            )

            if publisher and publisher not in DAUM_SOURCES:
                return publisher

    for selector in [
        ".info_cp",
        ".txt_cp",
        ".link_cp",
        ".cp_name",
    ]:
        node = soup.select_one(selector)

        if node:
            publisher = normalize_known_media_source(
                node.get_text(
                    " ",
                    strip=True
                )
            )

            if publisher and publisher not in DAUM_SOURCES:
                return publisher

    return ""


def resolve_daum_source(
    link,
    original_url_resolver=None,
    requester=requests.get
):

    if not link:
        return ""

    if original_url_resolver is None:
        original_url_resolver = get_original_url

    original_url = original_url_resolver(link)

    try:
        response = requester(
            original_url,
            timeout=10,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        return extract_publisher_from_html(
            response.text
        )

    except Exception:
        return ""


def normalize_source(
    source,
    link="",
    original_url_resolver=None,
    requester=requests.get
):

    normalized_source = normalize_known_media_source(
        source
    )
    link_host = urlparse(
        str(link or "")
    ).netloc.lower()

    if link_host in SOURCE_NAME_OVERRIDES:
        return SOURCE_NAME_OVERRIDES[link_host]

    if normalized_source not in DAUM_SOURCES:
        return normalized_source

    daum_source = resolve_daum_source(
        link,
        original_url_resolver=original_url_resolver,
        requester=requester
    )

    if daum_source:
        return daum_source

    return normalized_source


def extract_google_news_tokens(soup, html):

    token_node = soup.find(
        attrs={
            "data-n-a-id": True,
            "data-n-a-ts": True,
            "data-n-a-sg": True,
        }
    )

    if token_node:
        return {
            "article_id": token_node.get("data-n-a-id"),
            "timestamp": token_node.get("data-n-a-ts"),
            "signature": token_node.get("data-n-a-sg"),
        }

    article_id_match = re.search(
        r'data-n-a-id="([^"]+)"',
        html
    )
    timestamp_match = re.search(
        r'data-n-a-ts="([^"]+)"',
        html
    )
    signature_match = re.search(
        r'data-n-a-sg="([^"]+)"',
        html
    )

    if (
        article_id_match
        and timestamp_match
        and signature_match
    ):
        return {
            "article_id": article_id_match.group(1),
            "timestamp": timestamp_match.group(1),
            "signature": signature_match.group(1),
        }

    return None


def parse_batchexecute_response(response_text):

    payload = response_text

    if payload.startswith(")]}'"):
        payload = payload.split(
            "\n",
            1
        )[1]

    rows = json.loads(payload)

    for row in rows:
        if (
            len(row) >= 3
            and row[0] == "wrb.fr"
            and row[1] == "Fbv4je"
        ):
            result = json.loads(row[2])

            if (
                len(result) >= 2
                and result[0] == "garturlres"
                and is_http_url(result[1])
            ):

                return result[1]

    return None


def decode_google_news_url(
    article_id,
    timestamp,
    signature,
    post_requester=requests.post
):

    request_payload = [
        "garturlreq",
        [
            [
                "en-US",
                "US",
                [
                    "FINANCE_TOP_INDICES",
                    "GENESIS_PUBLISHER_SECTION",
                    "WEB_TEST_1_0_0",
                ],
                None,
                None,
                1,
                1,
                "US:en",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                False,
            ],
            "en-US",
            "US",
            True,
            [
                3,
                5,
                9,
                19,
            ],
            1,
            True,
            "929622352",
            None,
            None,
            None,
            False,
        ],
        article_id,
        int(timestamp),
        signature,
    ]

    batch_payload = [
        [
            [
                "Fbv4je",
                json.dumps(
                    request_payload,
                    separators=(",", ":")
                ),
                None,
                "generic",
            ]
        ]
    ]

    response = post_requester(
        "https://news.google.com/_/DotsSplashUi/data/batchexecute",
        data={
            "f.req": json.dumps(
                batch_payload,
                separators=(",", ":")
            )
        },
        timeout=10,
        headers={
            "Content-Type":
            "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent":
            "Mozilla/5.0",
        }
    )

    return parse_batchexecute_response(
        response.text
    )


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
                "출처": normalize_source(
                    source,
                    link=item.link
                ),
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
    requester=requests.get,
    post_requester=requests.post
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

        tokens = extract_google_news_tokens(
            soup,
            response.text
        )

        if tokens:
            decoded_url = decode_google_news_url(
                tokens["article_id"],
                tokens["timestamp"],
                tokens["signature"],
                post_requester=post_requester
            )

            if decoded_url:
                return decoded_url

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
