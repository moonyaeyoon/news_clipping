DEFAULT_QUERY = """
(디지털자산 OR 가상자산 OR 코인)
AND
(기관 OR 법인 OR 빗썸 OR 코인베이스 OR 바이낸스 OR 
규제 OR 가이드 OR 회계 OR 세법 OR 공시 OR 금융위 OR 금감원 OR 
시장 OR 장외거래 OR OTC OR ETF OR 커스터디 OR 프라임브로커리지 OR PBS OR 토큰증권)
"""

RSS_LOOKBACK_DAYS = 10

NEWS_ARCHIVE_FILE = "data/news_archive.csv"

AUTO_COLLECT_TIMES = [
    "09:15",
    "15:30",
]


