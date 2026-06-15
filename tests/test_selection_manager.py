import unittest

import pandas as pd

from core.selection_manager import (
    ARTICLE_ID_COLUMN,
    SELECTED_COLUMN,
    apply_selection,
    ensure_article_ids,
    get_selected_article_ids,
    get_selected_articles,
)


class SelectionManagerTest(unittest.TestCase):

    def test_ensure_article_ids_adds_stable_id_column(self):

        news_df = pd.DataFrame(
            [
                {
                    "날짜": "2026-06-15",
                    "제목": "기사",
                    "출처": "언론A",
                    "링크": "https://example.com/article",
                }
            ]
        )

        first_result = ensure_article_ids(news_df)
        second_result = ensure_article_ids(news_df)

        self.assertIn(
            ARTICLE_ID_COLUMN,
            first_result.columns
        )
        self.assertEqual(
            first_result.loc[0, ARTICLE_ID_COLUMN],
            second_result.loc[0, ARTICLE_ID_COLUMN]
        )

    def test_apply_selection_marks_selected_rows_by_id(self):

        news_df = ensure_article_ids(
            pd.DataFrame(
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
        )

        selected_ids = {
            news_df.loc[1, ARTICLE_ID_COLUMN]
        }

        result = apply_selection(
            news_df,
            selected_ids
        )

        self.assertFalse(result.loc[0, SELECTED_COLUMN])
        self.assertTrue(result.loc[1, SELECTED_COLUMN])

    def test_get_selected_articles_drops_ui_columns(self):

        news_df = ensure_article_ids(
            pd.DataFrame(
                [
                    {
                        "날짜": "2026-06-15",
                        "제목": "기사",
                        "출처": "언론A",
                        "링크": "https://example.com/a",
                    }
                ]
            )
        )
        selected_df = apply_selection(
            news_df,
            {
                news_df.loc[0, ARTICLE_ID_COLUMN]
            }
        )

        selected_articles = get_selected_articles(selected_df)

        self.assertEqual(1, len(selected_articles))
        self.assertNotIn(
            SELECTED_COLUMN,
            selected_articles.columns
        )
        self.assertNotIn(
            ARTICLE_ID_COLUMN,
            selected_articles.columns
        )

    def test_get_selected_article_ids_extracts_checked_rows(self):

        news_df = ensure_article_ids(
            pd.DataFrame(
                [
                    {
                        "날짜": "2026-06-15",
                        "제목": "기사",
                        "출처": "언론A",
                        "링크": "https://example.com/a",
                    }
                ]
            )
        )
        selected_df = apply_selection(
            news_df,
            {
                news_df.loc[0, ARTICLE_ID_COLUMN]
            }
        )

        self.assertEqual(
            {
                news_df.loc[0, ARTICLE_ID_COLUMN]
            },
            get_selected_article_ids(selected_df)
        )


if __name__ == "__main__":
    unittest.main()
