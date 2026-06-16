import unittest

from core.rss_fetcher import (
    get_original_url,
    normalize_source,
)


class FakeResponse:

    def __init__(
        self,
        text,
        url="https://news.google.com/rss/articles/example"
    ):

        self.text = text
        self.url = url


def build_google_news_page():

    return """
    <html>
        <body>
            <div
                data-n-a-id="ARTICLE_ID"
                data-n-a-ts="1781506943"
                data-n-a-sg="SIGNATURE">
            </div>
        </body>
    </html>
    """


class RssFetcherTest(unittest.TestCase):

    def test_normalize_source_removes_known_section_suffix(self):

        self.assertEqual(
            "매일경제",
            normalize_source("매일경제 마켓")
        )
        self.assertEqual(
            "한국경제",
            normalize_source("한국경제 증권")
        )

    def test_get_original_url_prefers_non_google_canonical_url(self):

        def fake_get(url, **kwargs):

            return FakeResponse(
                """
                <html>
                    <head>
                        <link rel="canonical"
                              href="https://example.com/original-article">
                    </head>
                </html>
                """
            )

        self.assertEqual(
            "https://example.com/original-article",
            get_original_url(
                "https://news.google.com/rss/articles/example",
                requester=fake_get
            )
        )

    def test_normalize_source_resolves_daum_publisher_from_article_meta(self):

        def fake_original_url_resolver(url):

            return "https://v.daum.net/v/20260616090000000"

        def fake_get(url, **kwargs):

            return FakeResponse(
                """
                <html>
                    <head>
                        <meta property="og:article:author"
                              content="매일경제">
                    </head>
                </html>
                """,
                url="https://v.daum.net/v/20260616090000000"
            )

        self.assertEqual(
            "매일경제",
            normalize_source(
                "v.daum.net",
                link="https://news.google.com/rss/articles/example",
                original_url_resolver=fake_original_url_resolver,
                requester=fake_get
            )
        )

    def test_get_original_url_finds_non_google_article_link(self):

        def fake_get(url, **kwargs):

            return FakeResponse(
                """
                <html>
                    <body>
                        <a href="https://news.google.com/home">Google News</a>
                        <a href="https://example.com/original-article">
                            Original
                        </a>
                    </body>
                </html>
                """
            )

        self.assertEqual(
            "https://example.com/original-article",
            get_original_url(
                "https://news.google.com/rss/articles/example",
                requester=fake_get
            )
        )

    def test_get_original_url_decodes_google_news_article_tokens(self):

        def fake_get(url, **kwargs):

            return FakeResponse(
                build_google_news_page()
            )

        def fake_post(url, **kwargs):

            return FakeResponse(
                """)]}'\n\n"""
                + """[["wrb.fr","Fbv4je","[\\"garturlres\\",\\"https://example.com/article?id\\\\u003d1\\",1]",null,null,null,"generic"]]"""
            )

        self.assertEqual(
            "https://example.com/article?id=1",
            get_original_url(
                "https://news.google.com/rss/articles/example",
                requester=fake_get,
                post_requester=fake_post
            )
        )


if __name__ == "__main__":
    unittest.main()
