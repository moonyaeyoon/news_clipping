import unittest
import os
import tempfile

import pandas as pd

from core.email_generator import (
    BIZ_BUTTON_IMAGE_URL,
    BITHUMB_BIZ_URL,
    CARD_SKY_BACKGROUND_IMAGE_URL,
    FOOTER_IMAGE_URL,
    HEADER_IMAGE_URL,
    ORANGE_BUILDING_IMAGE_URL,
    ORANGE_HEADER_IMAGE_URL,
    ORANGE_SIDEBAR_IMAGE_URL,
    generate_email_body_html,
    generate_large_email_body_html,
    generate_orange_card_email_body_html,
    generate_orange_email_body_html,
    generate_orange_no_sidebar_email_body_html,
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
OLD_FOOTER_IMAGE_URL_4 = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781749398/footer_cz81co.png"
)
OLD_FOOTER_IMAGE_URL_5 = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781751590/footer_ver1.2_qimxow.png"
)
OLD_FOOTER_IMAGE_URL_6 = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781758835/footer_ver1.2_3_gsrovb.png"
)
OLD_BIZ_BUTTON_IMAGE_URL = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781742268/BizButton_k7fsjr.png"
)
OLD_BIZ_BUTTON_IMAGE_URL_2 = (
    "https://res.cloudinary.com/dys1jifiy/image/upload/"
    "v1781758969/BIZ-Btn_scm0dh.png"
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
            "2026.6.16 (화)",
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
            "\n26.6.16 (화)\n",
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
            "2026.6.16 (화)",
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
            'height="76"',
            html
        )
        self.assertIn(
            "height:76px; font-size:0; line-height:0",
            html
        )
        self.assertIn(
            "height:17px; padding-top:0; padding-right:16px; padding-bottom:0; padding-left:0",
            html
        )
        self.assertIn(
            'height="7"',
            html
        )
        self.assertIn(
            "height:7px; font-size:0; line-height:0",
            html
        )
        self.assertNotIn(
            "height:100px; padding-top:0; padding-right:16px; padding-bottom:15px; padding-left:0",
            html
        )
        self.assertIn(
            "font-family:'SUIT',sans-serif; font-size:13px; font-weight:600; line-height:15px",
            html
        )
        self.assertNotIn(
            "Apple SD Gothic Neo",
            html
        )
        self.assertNotIn(
            "Malgun Gothic",
            html
        )
        self.assertNotIn(
            "Arial",
            html
        )
        self.assertNotIn(
            "font-family:'S-Core Dream','SUIT','Apple SD Gothic Neo','Malgun Gothic',Arial,sans-serif; font-size:18px; font-weight:500",
            html
        )
        self.assertIn(
            "2026.6.16 (화)",
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
        self.assertNotIn(
            OLD_BIZ_BUTTON_IMAGE_URL,
            html
        )
        self.assertNotIn(
            OLD_BIZ_BUTTON_IMAGE_URL_2,
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
        self.assertNotIn(
            "본 뉴스레터는 신뢰할 수 있는 정보 제공을 목적으로 작성되었으며",
            html
        )
        self.assertIn(
            "1661-5566 (2번, 법인 전용 상담 창구)",
            html
        )
        self.assertIn(
            "biz@bithumbcorp.com",
            html
        )
        self.assertIn(
            'height="77"',
            html
        )
        self.assertIn(
            "background-size:680px 77px",
            html
        )
        self.assertIn(
            "width:489px; padding-top:43.5px; padding-right:0; padding-bottom:0; padding-left:86px",
            html
        )
        self.assertIn(
            "font-family:'SUIT',sans-serif; font-size:8px; font-weight:400; line-height:10px; color:#7c7c7c",
            html
        )
        self.assertIn(
            "padding-top:1px; padding-right:0; padding-bottom:0; padding-left:0; font-family:'SUIT',sans-serif; font-size:8px; font-weight:400; line-height:10px; color:#7c7c7c",
            html
        )
        self.assertNotIn(
            "font-family:'SUIT',sans-serif; font-size:13px; font-weight:400; line-height:20px",
            html
        )
        self.assertNotIn(
            "line-height:11px; color:#7c7c7c",
            html
        )
        self.assertIn(
            FOOTER_IMAGE_URL,
            html
        )
        self.assertIn(
            f'background="{FOOTER_IMAGE_URL}"',
            html
        )
        self.assertNotIn(
            'alt="빗썸 BIZ 안내 푸터"',
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
        self.assertNotIn(
            OLD_FOOTER_IMAGE_URL_4,
            html
        )
        self.assertNotIn(
            OLD_FOOTER_IMAGE_URL_5,
            html
        )
        self.assertNotIn(
            OLD_FOOTER_IMAGE_URL_6,
            html
        )

    def test_generate_large_email_body_html_uses_wider_layout(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": "큰 사이즈 기사 제목",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        html = generate_large_email_body_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            'width="860"',
            html
        )
        self.assertIn(
            'height="127"',
            html
        )
        self.assertIn(
            "background-size:860px 129px",
            html
        )
        self.assertIn(
            'width="720"',
            html
        )
        self.assertIn(
            "font-size:20px; font-weight:500; line-height:30px",
            html
        )
        self.assertIn(
            "background-size:860px 98px",
            html
        )
        self.assertIn(
            "큰 사이즈 기사 제목",
            html
        )
        self.assertNotIn(
            'width="680"',
            html
        )
        self.assertNotIn(
            'width="760"',
            html
        )

    def test_generate_orange_email_body_html_uses_responsive_sidebar_layout(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": f"오렌지 템플릿 기사 {index}",
                    "출처": "언론A",
                    "링크": f"https://example.com/article/{index}",
                }
                for index in range(1, 9)
            ]
        )

        html = generate_orange_email_body_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            ORANGE_HEADER_IMAGE_URL,
            html
        )
        self.assertIn(
            ORANGE_BUILDING_IMAGE_URL,
            html
        )
        self.assertNotIn(
            ORANGE_SIDEBAR_IMAGE_URL,
            html
        )
        self.assertIn(
            'width="90%"',
            html
        )
        self.assertIn(
            "max-width:1200px",
            html
        )
        self.assertIn(
            "font-family:Arial,sans-serif",
            html
        )
        self.assertIn(
            'width="21%"',
            html
        )
        self.assertIn(
            'width="79%"',
            html
        )
        self.assertIn(
            "linear-gradient(to bottom",
            html
        )
        self.assertIn(
            "#f5f5f5 52%",
            html
        )
        self.assertIn(
            "rgba(189, 223, 245, 0.95) 100%",
            html
        )
        self.assertIn(
            'alt=""',
            html
        )
        self.assertIn(
            "mailto:biz@bithumbcorp.com",
            html
        )
        self.assertIn(
            'width="100%"',
            html
        )
        self.assertIn(
            "display:block; width:100%; height:auto",
            html
        )
        self.assertIn(
            "background-color:#292d32",
            html
        )
        self.assertNotIn("2026.6.16 (화)", html)
        self.assertEqual(
            8,
            sum(
                f"오렌지 템플릿 기사 {index}" in html
                for index in range(1, 9)
            )
        )
        self.assertNotIn(
            'height="624"',
            html
        )
        self.assertNotIn(
            "position:absolute",
            html
        )

    def test_generate_orange_no_sidebar_email_body_html_uses_single_column_layout(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": f"사이드바 없는 템플릿 기사 {index}",
                    "출처": "언론A",
                    "링크": f"https://example.com/article/{index}",
                }
                for index in range(1, 6)
            ]
        )

        html = generate_orange_no_sidebar_email_body_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            ORANGE_HEADER_IMAGE_URL,
            html
        )
        self.assertIn(
            'width="90%"',
            html
        )
        self.assertIn(
            "max-width:1200px",
            html
        )
        self.assertIn(
            'width="75%"',
            html
        )
        self.assertIn(
            "padding-top:44px",
            html
        )
        self.assertIn(
            "padding-bottom:168px",
            html
        )
        self.assertIn(
            "mailto:biz@bithumbcorp.com",
            html
        )
        self.assertNotIn(
            ORANGE_BUILDING_IMAGE_URL,
            html
        )
        self.assertNotIn(
            ORANGE_SIDEBAR_IMAGE_URL,
            html
        )
        self.assertNotIn(
            "2026.6.16 (화)",
            html
        )
        self.assertEqual(
            5,
            sum(
                f"사이드바 없는 템플릿 기사 {index}" in html
                for index in range(1, 6)
            )
        )

    def test_generate_orange_card_email_body_html_uses_sky_card_layout(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-16",
                    "제목": f"카드 템플릿 기사 {index}",
                    "출처": "언론A",
                    "링크": f"https://example.com/article/{index}",
                }
                for index in range(1, 9)
            ]
        )

        html = generate_orange_card_email_body_html(
            news_df,
            "2026.06.16"
        )

        self.assertIn(
            ORANGE_HEADER_IMAGE_URL,
            html
        )
        self.assertIn(
            CARD_SKY_BACKGROUND_IMAGE_URL,
            html
        )
        self.assertIn(
            ORANGE_BUILDING_IMAGE_URL,
            html
        )
        self.assertIn(
            'width="74%"',
            html
        )
        self.assertIn(
            "border:1px solid #d9d9d9",
            html
        )
        self.assertIn(
            "background-color:rgba(255,255,255,0.90)",
            html
        )
        self.assertIn(
            "background-size:100% 100%",
            html
        )
        self.assertIn(
            "padding-top:70px",
            html
        )
        self.assertIn(
            "padding-bottom:78px",
            html
        )
        self.assertIn(
            "2026.6.16 (화)",
            html
        )
        self.assertIn(
            "font-size:22px; font-weight:400; line-height:28px",
            html
        )
        self.assertIn(
            "margin-top:-250px",
            html
        )
        self.assertIn(
            "mailto:biz@bithumbcorp.com",
            html
        )
        self.assertEqual(
            8,
            sum(
                f"카드 템플릿 기사 {index}" in html
                for index in range(1, 9)
            )
        )


if __name__ == "__main__":
    unittest.main()
