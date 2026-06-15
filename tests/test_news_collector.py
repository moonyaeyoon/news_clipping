import os
import tempfile
import unittest

import pandas as pd

from scheduler import get_next_run

from core.news_collector import (
    append_news_archive,
    collect_news,
)
from core.settings import RSS_LOOKBACK_DAYS


class NewsCollectorTest(unittest.TestCase):

    def test_get_next_run_returns_later_time_today_or_first_time_tomorrow(self):

        self.assertEqual(
            pd.Timestamp("2026-06-15 15:30").to_pydatetime(),
            get_next_run(
                now=pd.Timestamp("2026-06-15 10:00").to_pydatetime(),
                schedule_times=["09:15", "15:30"]
            )
        )
        self.assertEqual(
            pd.Timestamp("2026-06-16 09:15").to_pydatetime(),
            get_next_run(
                now=pd.Timestamp("2026-06-15 16:00").to_pydatetime(),
                schedule_times=["09:15", "15:30"]
            )
        )

    def test_append_news_archive_creates_file_and_removes_duplicates(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = os.path.join(
                temp_dir,
                "news_archive.csv"
            )

            first_batch = pd.DataFrame(
                [
                    {
                        "날짜": "2026-06-15",
                        "제목": "첫 기사",
                        "출처": "언론A",
                        "링크": "https://example.com/a",
                    }
                ]
            )

            second_batch = pd.DataFrame(
                [
                    {
                        "날짜": "2026-06-15",
                        "제목": "첫 기사",
                        "출처": "언론A",
                        "링크": "https://example.com/a",
                    },
                    {
                        "날짜": "2026-06-15",
                        "제목": "두번째 기사",
                        "출처": "언론B",
                        "링크": "https://example.com/b",
                    },
                ]
            )

            append_news_archive(
                first_batch,
                archive_path=archive_path,
                collected_at="2026-06-15 09:15"
            )
            result = append_news_archive(
                second_batch,
                archive_path=archive_path,
                collected_at="2026-06-15 15:30"
            )

            saved = pd.read_csv(archive_path)

            self.assertEqual(2, len(result))
            self.assertEqual(2, len(saved))
            self.assertEqual(
                ["두번째 기사", "첫 기사"],
                saved["제목"].tolist()
            )
            self.assertIn(
                "수집시각",
                saved.columns
            )

    def test_collect_news_reuses_query_and_appends_to_archive(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = os.path.join(
                temp_dir,
                "news_archive.csv"
            )
            requested_queries = []

            def fake_fetcher(query):

                requested_queries.append(query)

                return pd.DataFrame(
                    [
                        {
                            "날짜": "2026-06-15",
                            "제목": "자동 수집 기사",
                            "출처": "언론A",
                            "링크": "https://example.com/auto",
                        }
                    ]
                )

            result = collect_news(
                archive_path=archive_path,
                fetcher=fake_fetcher,
                collected_at="2026-06-15 09:15"
            )

            self.assertEqual(1, len(result))
            self.assertEqual(1, len(requested_queries))
            self.assertIn(
                f"when:{RSS_LOOKBACK_DAYS}d",
                requested_queries[0]
            )
            self.assertTrue(
                os.path.exists(archive_path)
            )


if __name__ == "__main__":
    unittest.main()
