import os
import tempfile
import unittest

import pandas as pd

from core.export_manager import (
    build_export_download,
    prepare_export_df,
    save_articles_file,
)


class ExportManagerTest(unittest.TestCase):

    def test_prepare_export_df_resolves_links_and_converts_values_to_text(self):

        source_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-15",
                    "제목": "기사",
                    "출처": "언론A",
                    "링크": "https://news.google.com/example",
                }
            ]
        )

        result = prepare_export_df(
            source_df,
            url_resolver=lambda url: url.replace(
                "news.google.com",
                "example.com"
            )
        )

        self.assertEqual(
            "https://example.com/example",
            result.loc[0, "링크"]
        )
        self.assertEqual(
            object,
            result["날짜"].dtype
        )

    def test_prepare_export_df_normalizes_daum_source_after_link_resolution(self):

        source_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-15",
                    "제목": "기사",
                    "출처": "v.daum.net",
                    "링크": "https://news.google.com/example",
                }
            ]
        )

        def fake_source_normalizer(source, link):

            if (
                source == "v.daum.net"
                and link == "https://v.daum.net/v/20260615000000000"
            ):
                return "매일경제"

            return source

        result = prepare_export_df(
            source_df,
            url_resolver=lambda url: (
                "https://v.daum.net/v/20260615000000000"
            ),
            source_normalizer=fake_source_normalizer
        )

        self.assertEqual(
            "매일경제",
            result.loc[0, "출처"]
        )

    def test_save_articles_file_writes_excel_or_html_file(self):

        source_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-15",
                    "제목": "기사",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            excel_path = save_articles_file(
                source_df,
                file_name="daily_news",
                file_type="excel",
                output_dir=temp_dir,
                url_resolver=lambda url: url
            )
            html_path = save_articles_file(
                source_df,
                file_name="daily_news",
                file_type="html",
                output_dir=temp_dir,
                url_resolver=lambda url: url
            )

            self.assertTrue(os.path.exists(excel_path))
            self.assertTrue(os.path.exists(html_path))
            self.assertTrue(excel_path.endswith(".xlsx"))
            self.assertTrue(html_path.endswith(".html"))

            excel_df = pd.read_excel(excel_path)

            self.assertEqual(
                "https://example.com/article",
                excel_df.loc[0, "링크"]
            )

    def test_build_export_download_returns_email_template_html_file_data(self):

        source_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-15",
                    "제목": "메일용 기사",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        download = build_export_download(
            source_df,
            file_name="daily_news",
            file_type="html",
            url_resolver=lambda url: url
        )

        self.assertEqual(
            "daily_news.html",
            download["file_name"]
        )
        self.assertEqual(
            "text/html",
            download["mime"]
        )
        self.assertIn(
            b"border-collapse:collapse",
            download["data"]
        )
        self.assertIn(
            "메일용 기사".encode("utf-8"),
            download["data"]
        )
        self.assertNotIn(
            b"display:flex",
            download["data"]
        )
        self.assertNotIn(
            b"class=",
            download["data"]
        )

    def test_build_export_download_returns_file_data_without_writing_file(self):

        source_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-15",
                    "제목": "기사",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        excel_download = build_export_download(
            source_df,
            file_name="daily_news",
            file_type="excel",
            url_resolver=lambda url: url
        )
        self.assertEqual(
            "daily_news.xlsx",
            excel_download["file_name"]
        )
        self.assertEqual(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            excel_download["mime"]
        )
        self.assertTrue(
            excel_download["data"].startswith(b"PK")
        )


if __name__ == "__main__":
    unittest.main()
