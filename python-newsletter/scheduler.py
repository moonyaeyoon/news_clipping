import time
from datetime import datetime
from datetime import timedelta

from core.news_collector import collect_news
from core.settings import AUTO_COLLECT_TIMES


def get_next_run(now=None, schedule_times=None):

    if now is None:
        now = datetime.now()

    if schedule_times is None:
        schedule_times = AUTO_COLLECT_TIMES

    candidates = []

    for schedule_time in schedule_times:
        hour, minute = schedule_time.split(":")
        candidates.append(
            now.replace(
                hour=int(hour),
                minute=int(minute),
                second=0,
                microsecond=0
            )
        )

    future_candidates = [
        candidate
        for candidate in sorted(candidates)
        if candidate > now
    ]

    if future_candidates:
        return future_candidates[0]

    return sorted(candidates)[0] + timedelta(days=1)


def run_once():

    archive_df = collect_news()

    print(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"자동 수집 완료: 누적 {len(archive_df)}건",
        flush=True
    )

    return archive_df


def run_forever():

    print(
        "뉴스 자동 수집 스케줄러 시작 "
        f"(실행 시간: {', '.join(AUTO_COLLECT_TIMES)})",
        flush=True
    )

    while True:
        next_run = get_next_run()
        wait_seconds = max(
            0,
            (next_run - datetime.now()).total_seconds()
        )

        print(
            f"다음 자동 수집: {next_run.strftime('%Y-%m-%d %H:%M')}",
            flush=True
        )

        time.sleep(wait_seconds)

        try:
            run_once()
        except Exception as error:
            print(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                f"자동 수집 실패: {error}",
                flush=True
            )


if __name__ == "__main__":
    run_forever()
