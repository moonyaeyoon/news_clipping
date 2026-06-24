import os
from datetime import datetime

import pandas as pd

from core.rss_fetcher import fetch_news
from core.settings import (
    DEFAULT_QUERY,
    NEWS_ARCHIVE_FILE,
    RSS_LOOKBACK_DAYS,
)

NEWS_COLUMNS = [
    "날짜",
    "제목",
    "출처",
    "링크",
    "수집시각",
]


def build_rss_query(query=DEFAULT_QUERY):

    return f"{query} when:{RSS_LOOKBACK_DAYS}d"


def load_news_archive(archive_path=NEWS_ARCHIVE_FILE):

    if not os.path.exists(archive_path):
        return pd.DataFrame(columns=NEWS_COLUMNS)

    return pd.read_csv(archive_path)


def prepare_news_df(news_df, collected_at=None):

    if collected_at is None:
        collected_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    prepared_df = news_df.copy()

    for column in NEWS_COLUMNS:
        if column not in prepared_df.columns:
            prepared_df[column] = ""

    prepared_df["수집시각"] = collected_at

    return prepared_df[NEWS_COLUMNS]


def append_news_archive(
    news_df,
    archive_path=NEWS_ARCHIVE_FILE,
    collected_at=None
):

    existing_df = load_news_archive(
        archive_path=archive_path
    )
    incoming_df = prepare_news_df(
        news_df,
        collected_at=collected_at
    )

    archive_df = pd.concat(
        [
            existing_df,
            incoming_df,
        ],
        ignore_index=True
    )

    if len(archive_df):
        archive_df["_order"] = range(len(archive_df))
        archive_df = (
            archive_df
            .drop_duplicates(
                subset=[
                    "제목",
                    "링크",
                ],
                keep="last"
            )
            .sort_values(
                [
                    "날짜",
                    "수집시각",
                    "_order",
                ],
                ascending=False
            )
            .drop(
                columns=["_order"]
            )
            .reset_index(drop=True)
        )

    os.makedirs(
        os.path.dirname(archive_path),
        exist_ok=True
    )

    archive_df.to_csv(
        archive_path,
        index=False,
        encoding="utf-8-sig"
    )

    return archive_df


def collect_news(
    query=DEFAULT_QUERY,
    archive_path=NEWS_ARCHIVE_FILE,
    fetcher=fetch_news,
    collected_at=None
):

    news_df = fetcher(
        build_rss_query(query)
    )

    return append_news_archive(
        news_df,
        archive_path=archive_path,
        collected_at=collected_at
    )
