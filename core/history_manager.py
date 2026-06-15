import json
import os

HISTORY_FILE = "data/history.json"


def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

            if not content:
                return []

            return json.loads(content)

    except Exception:

        return []


def save_history(item):

    history = load_history()

    history.insert(
        0,
        item
    )

    history = history[:30]

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=2
        )