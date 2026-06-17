import unittest
import os
import tempfile

import pandas as pd

from core.email_generator import (
    generate_email_body_html,
    get_logo_data_uri,
)


class EmailGeneratorTest(unittest.TestCase):

    def test_get_logo_data_uri_finds_logo_when_working_directory_changes(self):

        original_cwd = os.getcwd()

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                logo_data_uri = get_logo_data_uri()

            finally:
                os.chdir(original_cwd)

        self.assertTrue(
            logo_data_uri.startswith("data:image/png;base64,")
        )

    def test_generate_email_body_html_formats_report_date_with_korean_weekday(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": "기사 제목",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        html = generate_email_body_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            "2026.6.16(화)",
            html
        )
        self.assertNotIn(
            "2026.06.16",
            html
        )
        self.assertNotIn(
            "[6/16]",
            html
        )
        self.assertNotIn(
            "6월 16일",
            html
        )

    def test_generate_email_body_html_links_article_title_directly(self):
        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": "클릭할 기사 제목",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        html = generate_email_body_html(
            news_df,
            "2026.06.16"
        )

        self.assertNotIn(
            "본문 보러가기",
            html
        )
        self.assertNotIn(
            "<svg",
            html
        )
        self.assertIn(
            'href="https://example.com/article"',
            html
        )
        self.assertIn(
            "클릭할 기사 제목",
            html
        )

    def test_generate_email_body_html_uses_email_client_friendly_markup(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": "메일용 기사 제목",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        html = generate_email_body_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"',
            html
        )
        self.assertIn(
            'http-equiv="Content-Type"',
            html
        )
        self.assertIn(
            'width="680"',
            html
        )
        self.assertIn(
            '<table',
            html
        )
        self.assertIn(
            "border-collapse:collapse",
            html
        )
        self.assertIn(
            "2026.6.16(화)",
            html
        )
        self.assertIn(
            "메일용 기사 제목",
            html
        )
        self.assertIn(
            "기사 원문 열기",
            html
        )
        self.assertNotIn(
            "↗",
            html
        )
        self.assertNotIn(
            "class=",
            html
        )
        self.assertNotIn(
            "<div",
            html
        )
        self.assertNotIn(
            "<p",
            html
        )
        self.assertNotIn(
            "<span",
            html
        )
        self.assertNotIn(
            "<style",
            html
        )
        self.assertNotIn(
            "<script",
            html
        )
        self.assertNotIn(
            "<link",
            html
        )
        self.assertNotIn(
            "display:flex",
            html
        )
        self.assertNotIn(
            "<svg",
            html
        )


if __name__ == "__main__":
    unittest.main()
