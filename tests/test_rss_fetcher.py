import unittest

from core.rss_fetcher import get_original_url


class FakeResponse:

    def __init__(
        self,
        text,
        url="https://news.google.com/rss/articles/example"
    ):

        self.text = text
        self.url = url


class RssFetcherTest(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
