def build_query(
    asset_keyword,
    entity_keyword,
    optional_keywords
):
    query = (
        f"{asset_keyword}"
        f"{entity_keyword}"
    )
    if optional_keywords:
        query += (
            " "
            + " ".join(
                optional_keywords
            )
        )
    return query