import hashlib

SELECTED_COLUMN = "선택"
ARTICLE_ID_COLUMN = "_article_id"


def build_article_id(row):

    raw_value = "|".join(
        [
            str(row.get("날짜", "")),
            str(row.get("제목", "")),
            str(row.get("출처", "")),
            str(row.get("링크", "")),
        ]
    )

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def ensure_article_ids(news_df):

    result_df = news_df.copy()

    if ARTICLE_ID_COLUMN not in result_df.columns:
        result_df[ARTICLE_ID_COLUMN] = result_df.apply(
            build_article_id,
            axis=1
        )

    return result_df


def apply_selection(
    news_df,
    selected_article_ids
):

    result_df = ensure_article_ids(news_df)

    if SELECTED_COLUMN not in result_df.columns:
        result_df.insert(
            0,
            SELECTED_COLUMN,
            False
        )

    result_df[SELECTED_COLUMN] = (
        result_df[ARTICLE_ID_COLUMN]
        .isin(selected_article_ids)
        .astype(bool)
    )

    return result_df


def get_selected_article_ids(edited_df):

    if (
        SELECTED_COLUMN not in edited_df.columns
        or ARTICLE_ID_COLUMN not in edited_df.columns
    ):
        return set()

    selected_df = edited_df[
        edited_df[SELECTED_COLUMN] == True
    ]

    return set(
        selected_df[ARTICLE_ID_COLUMN]
        .astype(str)
        .tolist()
    )


def get_selected_articles(
    edited_df,
    ordered_article_ids=None
):

    selected_df = edited_df[
        edited_df[SELECTED_COLUMN] == True
    ].copy()

    if ordered_article_ids:
        order_map = {
            str(article_id): index
            for index, article_id in enumerate(ordered_article_ids)
        }
        selected_df["_selection_order"] = (
            selected_df[ARTICLE_ID_COLUMN]
            .astype(str)
            .map(order_map)
            .fillna(len(order_map))
        )
        selected_df = selected_df.sort_values(
            "_selection_order",
            kind="stable"
        )

    return selected_df.drop(
        columns=[
            SELECTED_COLUMN,
            ARTICLE_ID_COLUMN,
            "_selection_order",
        ],
        errors="ignore"
    )
