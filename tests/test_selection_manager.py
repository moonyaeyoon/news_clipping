import unittest

import pandas as pd

from core.selection_manager import (
    ARTICLE_SORTABLE_STYLE,
    ARTICLE_ID_COLUMN,
    SELECTED_COLUMN,
    apply_selection,
    build_article_order_label,
    ensure_article_ids,
    get_selected_article_ids,
    get_selected_articles,
)


class SelectionManagerTest(unittest.TestCase):

    def test_build_article_order_label_uses_title_and_metadata_lines(self):

        label = build_article_order_label(
            {
                "제목": "가상자산 시장 기사",
                "출처": "뉴스1",
                "날짜": "2026-06-22",
                ARTICLE_ID_COLUMN: "abcdef12",
            }
        )

        self.assertTrue(
            label.startswith(
                "가상자산 시장 기사\n뉴스1 · 2026-06-22"
            )
        )
        self.assertNotIn(
            "abcdef12",
            label
        )

    def test_build_article_order_label_keeps_duplicate_labels_unique(self):

        first_label = build_article_order_label(
            {
                "제목": "같은 기사",
                "출처": "뉴스1",
                "날짜": "2026-06-22",
                ARTICLE_ID_COLUMN: "00000000",
            }
        )
        second_label = build_article_order_label(
            {
                "제목": "같은 기사",
                "출처": "뉴스1",
                "날짜": "2026-06-22",
                ARTICLE_ID_COLUMN: "ffffffff",
            }
        )

        self.assertNotEqual(
            first_label,
            second_label
        )

    def test_article_sortable_style_matches_card_layout(self):

        self.assertIn(
            "min-height: 70px",
            ARTICLE_SORTABLE_STYLE
        )
        self.assertIn(
            "font-size: 16px",
            ARTICLE_SORTABLE_STYLE
        )
        self.assertIn(
            'content: "⠿"',
            ARTICLE_SORTABLE_STYLE
        )
        self.assertIn(
            "white-space: pre-line",
            ARTICLE_SORTABLE_STYLE
        )
        self.assertIn(
            ".sortable-item.dragging",
            ARTICLE_SORTABLE_STYLE
        )

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

    def test_get_selected_articles_uses_requested_order(self):

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
        selected_df = apply_selection(
            news_df,
            set(
                news_df[ARTICLE_ID_COLUMN]
                .astype(str)
                .tolist()
            )
        )

        selected_articles = get_selected_articles(
            selected_df,
            ordered_article_ids=[
                news_df.loc[1, ARTICLE_ID_COLUMN],
                news_df.loc[0, ARTICLE_ID_COLUMN],
            ]
        )

        self.assertEqual(
            [
                "두번째 기사",
                "첫 기사",
            ],
            selected_articles["제목"].tolist()
        )


if __name__ == "__main__":
    unittest.main()
