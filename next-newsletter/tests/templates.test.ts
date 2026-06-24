import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { generateNewsletterHtml } from "@/lib/templates";

describe("newsletter html generation", () => {
  it("generates email-ready html with selected article links", () => {
    const html = generateNewsletterHtml({
      template: "orange-card",
      reportDate: "2026.6.24 (수)",
      articles: [
        {
          id: "article-1",
          title: "법인 디지털자산 시장 동향",
          source: "뉴스1",
          date: "2026-06-24",
          link: "https://example.com/news",
        },
      ],
    });

    assert.match(html, /법인 디지털자산 시장 동향/);
    assert.match(html, /https:\/\/example\.com\/news/);
    assert.match(html, /2026\.6\.24 \(수\)/);
    assert.match(html, /빗썸 BIZ 바로가기/);
  });
});
