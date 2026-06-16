import unittest
import os
import tempfile

import pandas as pd

from core.email_generator import (
    generate_email_html,
    get_logo_data_uri,
)


class EmailGeneratorTest(unittest.TestCase):

    def test_generate_email_html_formats_report_date_for_newsletter_body(self):

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

        html = generate_email_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            "[6/16]",
            html
        )
        self.assertNotIn(
            "2026.06.16",
            html
        )
        self.assertNotIn(
            "6월 16일",
            html
        )

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

    def test_generate_email_html_keeps_footer_below_a_tall_body(self):

        news_df = pd.DataFrame(
            columns=[
                "날짜",
                "제목",
                "출처",
                "링크",
            ]
        )

        html = generate_email_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            "min-height:calc(100vh + 120px)",
            html
        )
        self.assertIn(
            "flex:0 0 auto",
            html
        )

    def test_generate_email_html_uses_full_width_web_layout(self):

        news_df = pd.DataFrame(
            columns=[
                "날짜",
                "제목",
                "출처",
                "링크",
            ]
        )

        html = generate_email_html(
            news_df,
            "2026.06.16"
        )

        expected_styles = [
            "--page-x:clamp(40px, 7vw, 144px)",
            "max-width:none",
            "padding:clamp(42px, 5vw, 72px) var(--page-x) 0",
            "width:clamp(150px, 11vw, 212px)",
            "font-size:clamp(36px, 4vw, 64px)",
            "padding:34px var(--page-x) 64px",
        ]

        for expected_style in expected_styles:
            self.assertIn(
                expected_style,
                html
            )

    def test_generate_email_html_vertically_centers_footer_content(self):

        news_df = pd.DataFrame(
            columns=[
                "날짜",
                "제목",
                "출처",
                "링크",
            ]
        )

        html = generate_email_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            "justify-content:center",
            html
        )
        self.assertIn(
            "padding:24px var(--page-x)",
            html
        )

    def test_generate_email_html_omits_figma_placeholder_shapes(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": "뉴스 기사 제목",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        html = generate_email_html(
            news_df,
            "2026.06.16"
        )

        self.assertNotIn(
            "▲",
            html
        )
        self.assertNotIn(
            "date-pill",
            html
        )
        self.assertNotIn(
            "article-marker",
            html
        )
        self.assertIn(
            "article-meta-line",
            html
        )


if __name__ == "__main__":
    unittest.main()
