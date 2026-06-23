import hashlib

SELECTED_COLUMN = "선택"
ARTICLE_ID_COLUMN = "_article_id"

ARTICLE_SORTABLE_STYLE = """
.sortable-component {
    width: 100%;
    font-family: 'SUIT', sans-serif;
}

.sortable-component.vertical {
    display: block;
}

.sortable-component.vertical .sortable-container {
    width: 100% !important;
    min-width: 0;
    margin: 0;
    padding: 0;
}

.sortable-container-body {
    box-sizing: border-box;
    width: 100%;
    min-height: 0;
    padding: 8px;
    border-radius: 10px;
    background: #f2f6fc;
}

.sortable-item,
.sortable-item:hover {
    position: relative;
    box-sizing: border-box;
    display: block !important;
    min-height: 70px;
    margin: 0 0 8px 0;
    padding: 12px 18px 11px 54px;
    border: 1px solid #d7dce3;
    border-radius: 10px;
    background: #ffffff;
    color: #7b7b7b;
    box-shadow: none;
    font-family: 'SUIT', sans-serif;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.45;
    text-align: left;
    white-space: pre-line;
    overflow-wrap: anywhere;
    cursor: grab;
    user-select: none;
}

.sortable-item:last-child {
    margin-bottom: 0;
}

.sortable-item::before {
    content: "⠿";
    position: absolute;
    top: 50%;
    left: 18px;
    transform: translateY(-50%);
    color: #111111;
    font-size: 22px;
    font-weight: 700;
    line-height: 1;
    pointer-events: none;
}

.sortable-item::first-line {
    color: #111111;
    font-size: 16px;
    font-weight: 700;
    line-height: 1.5;
}

.sortable-item:hover {
    border-color: #b7c8df;
    box-shadow: 0 6px 16px rgba(31, 55, 88, 0.10);
}

.sortable-item:active,
.sortable-item.dragging {
    border-color: #91afe0;
    box-shadow: 0 10px 22px rgba(31, 55, 88, 0.18);
    cursor: grabbing;
    opacity: 1;
}

.sortable-item.active {
    opacity: 1;
}
"""


def build_invisible_article_key(article_id):

    if not article_id:
        return ""

    digest = hashlib.sha256(
        str(article_id).encode("utf-8")
    ).hexdigest()[:8]
    bits = "".join(
        f"{int(character, 16):04b}"
        for character in digest
    )

    return "\u2063" + "".join(
        "\u200b" if bit == "0" else "\u200c"
        for bit in bits
    )


def build_article_order_label(row):

    title = str(row.get("제목", "")).strip()

    if len(title) > 72:
        title = title[:69] + "..."

    metadata = " · ".join(
        value
        for value in [
            str(row.get("출처", "")).strip(),
            str(row.get("날짜", "")).strip(),
        ]
        if value
    )
    visible_label = (
        f"{title}\n{metadata}"
        if metadata
        else title
    )

    return visible_label + build_invisible_article_key(
        row.get(ARTICLE_ID_COLUMN, "")
    )


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
