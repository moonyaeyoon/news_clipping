import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  buildGoogleNewsRssUrl,
  filterArticlesByDate,
  getOriginalUrl,
  normalizeSource,
  parseGoogleNewsRss,
} from "@/lib/news";

const sampleRss = `<?xml version="1.0" encoding="UTF-8"?>
<rss>
  <channel>
    <item>
      <title>삼성전자, 비트코인 시총 추월 - 2news.co.kr</title>
      <link>https://news.google.com/rss/articles/abc</link>
      <pubDate>Wed, 24 Jun 2026 01:20:00 GMT</pubDate>
    </item>
    <item>
      <title>가상자산 시장 확대 - 매일경제 마켓</title>
      <link>https://example.com/article</link>
      <pubDate>Tue, 23 Jun 2026 03:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>`;

describe("news utilities", () => {
  it("builds a Google News RSS URL with Korean locale", () => {
    const url = buildGoogleNewsRssUrl("가상자산 when:30d");

    assert.equal(url.hostname, "news.google.com");
    assert.equal(url.pathname, "/rss/search");
    assert.equal(url.searchParams.get("hl"), "ko");
    assert.equal(url.searchParams.get("gl"), "KR");
    assert.equal(url.searchParams.get("ceid"), "KR:ko");
    assert.equal(url.searchParams.get("q"), "가상자산 when:30d");
  });

  it("parses RSS items and normalizes source names", () => {
    const articles = parseGoogleNewsRss(sampleRss);

    assert.equal(articles.length, 2);
    assert.equal(articles[0].title, "삼성전자, 비트코인 시총 추월");
    assert.equal(articles[0].source, "에너지 뉴스");
    assert.equal(articles[0].date, "2026-06-24");
    assert.equal(articles[1].source, "매일경제");
  });

  it("normalizes noisy source labels", () => {
    assert.equal(normalizeSource("매일경제 마켓"), "매일경제");
    assert.equal(normalizeSource("v.daum.net"), "다음뉴스");
    assert.equal(normalizeSource("2news.co.kr"), "에너지 뉴스");
  });

  it("filters articles by inclusive date range", () => {
    const articles = parseGoogleNewsRss(sampleRss);
    const filtered = filterArticlesByDate(articles, "2026-06-24", "2026-06-24");

    assert.equal(filtered.length, 1);
    assert.equal(filtered[0].date, "2026-06-24");
  });

  it("resolves canonical original article links from Google News pages", async () => {
    const fetcher = async () =>
      new Response(
        '<html><head><link rel="canonical" href="https://example.com/original-news" /></head></html>',
        {
          status: 200,
        },
      );

    const originalUrl = await getOriginalUrl(
      "https://news.google.com/rss/articles/abc",
      fetcher,
    );

    assert.equal(originalUrl, "https://example.com/original-news");
  });
});
