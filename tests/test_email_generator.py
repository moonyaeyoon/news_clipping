import unittest
import os
import tempfile

import pandas as pd

from core.email_generator import (
    BIZ_BUTTON_IMAGE_URL,
    BITHUMB_BIZ_URL,
    FOOTER_IMAGE_URL,
    HEADER_IMAGE_URL,
    generate_email_body_html,
    get_logo_data_uri,
)

OLD_HEADER_IMAGE_URL = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781742248/header_et3xsa.svg"
)
OLD_HEADER_IMAGE_URL_2 = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781742563/header_blue_bi5huo.svg"
)
OLD_FOOTER_BUILDING_IMAGE_URL = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781742442/newsletter_footer_building_l1kag5.png"
)
OLD_FOOTER_IMAGE_URL = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781744219/footer_ldydod.svg"
)
OLD_FOOTER_IMAGE_URL_2 = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781748226/footer_oqhuia.svg"
)
OLD_FOOTER_IMAGE_URL_3 = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781749139/footer_b9lbxk.svg"
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
            "26.6.16 (화)",
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
            "2026.6.16(화)",
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
            "26.6.16 (화)",
            html
        )
        self.assertIn(
            "메일용 기사 제목",
            html
        )
        self.assertIn(
            "(6/16)",
            html
        )
        self.assertNotIn(
            "2026-06-16",
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
            "<script",
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

    def test_generate_email_body_html_uses_figma_header_layout(self):

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
            "cdn.jsdelivr.net/gh/sun-typeface/SUIT",
            html
        )
        self.assertIn(
            "cdn.jsdelivr.net/gh/ungveloper/web-fonts/SCoreDream",
            html
        )
        self.assertIn(
            "법인 디지털자산 시장 동향",
            html
        )
        self.assertIn(
            'height="100"',
            html
        )
        self.assertIn(
            HEADER_IMAGE_URL,
            html
        )
        self.assertIn(
            "background-color:#ffffff; background-image",
            html
        )
        self.assertIn(
            "background-size:680px 102px",
            html
        )
        self.assertNotIn(
            "background-color:#242424",
            html
        )
        self.assertNotIn(
            OLD_HEADER_IMAGE_URL,
            html
        )
        self.assertNotIn(
            OLD_HEADER_IMAGE_URL_2,
            html
        )
        self.assertNotIn(
            "data:image/png;base64",
            html
        )
        self.assertIn(
            "font-size:18px; font-weight:500",
            html
        )
        self.assertNotIn(
            "font-size:38px",
            html
        )
        self.assertIn(
            "26.6.16 (화)",
            html
        )

    def test_generate_email_body_html_uses_figma_body_spacing_and_cta(self):

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
            'width="520"',
            html
        )
        self.assertIn(
            "font-size:12px; font-weight:400; line-height:18px; color:#777777",
            html
        )
        self.assertIn(
            "언론A&nbsp;&nbsp;(6/16)",
            html
        )
        self.assertIn(
            "font-family:'SUIT',sans-serif; font-size:18px; font-weight:500; line-height:26px",
            html
        )
        self.assertNotIn(
            "font-weight:600; line-height:26px",
            html
        )
        self.assertIn(
            "빗썸 BIZ 바로가기",
            html
        )
        self.assertIn(
            f'href="{BITHUMB_BIZ_URL}"',
            html
        )
        self.assertIn(
            BIZ_BUTTON_IMAGE_URL,
            html
        )
        self.assertIn(
            'alt="빗썸 BIZ 바로가기"',
            html
        )
        self.assertIn(
            'width="110"',
            html
        )
        self.assertIn(
            'height="38"',
            html
        )
        self.assertIn(
            'alt="빗썸 BIZ 안내 푸터"',
            html
        )
        self.assertIn(
            FOOTER_IMAGE_URL,
            html
        )
        self.assertNotIn(
            OLD_FOOTER_BUILDING_IMAGE_URL,
            html
        )
        self.assertNotIn(
            OLD_FOOTER_IMAGE_URL,
            html
        )
        self.assertNotIn(
            OLD_FOOTER_IMAGE_URL_2,
            html
        )
        self.assertNotIn(
            OLD_FOOTER_IMAGE_URL_3,
            html
        )


if __name__ == "__main__":
    unittest.main()
