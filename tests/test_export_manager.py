import os
import tempfile
import unittest

import pandas as pd

from core.export_manager import (
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


if __name__ == "__main__":
    unittest.main()
