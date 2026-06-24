export type NewsArticle = {
  id: string;
  title: string;
  source: string;
  date: string;
  link: string;
};

const DEFAULT_QUERY = `
(디지털자산 OR 가상자산 OR 코인)
AND
(기업 OR 기관 OR 법인)
`;

const SOURCE_ALIASES: Record<string, string> = {
  "2news.co.kr": "에너지 뉴스",
  "www.2news.co.kr": "에너지 뉴스",
  "v.daum.net": "다음뉴스",
};

const SOURCE_PREFIXES = ["매일경제"];
const GOOGLE_NEWS_BATCH_URL =
  "https://news.google.com/_/DotsSplashUi/data/batchexecute";

export function getDefaultQuery() {
  return DEFAULT_QUERY.trim();
}

export function buildGoogleNewsRssUrl(query: string) {
  const url = new URL("https://news.google.com/rss/search");
  url.searchParams.set("q", query);
  url.searchParams.set("hl", "ko");
  url.searchParams.set("gl", "KR");
  url.searchParams.set("ceid", "KR:ko");

  return url;
}

export function normalizeSource(source: string, link = "") {
  const trimmed = source.trim();
  const linkHost = getUrlHost(link);

  if (SOURCE_ALIASES[trimmed]) {
    return SOURCE_ALIASES[trimmed];
  }

  if (linkHost && SOURCE_ALIASES[linkHost]) {
    return SOURCE_ALIASES[linkHost];
  }

  const matchingPrefix = SOURCE_PREFIXES.find((prefix) =>
    trimmed.startsWith(prefix),
  );

  if (matchingPrefix) {
    return matchingPrefix;
  }

  return trimmed;
}

export function parseGoogleNewsRss(rssText: string) {
  const itemMatches = rssText.matchAll(/<item>([\s\S]*?)<\/item>/g);
  const articles: NewsArticle[] = [];
  const seenTitles = new Set<string>();

  for (const match of itemMatches) {
    const item = match[1];
    const rawTitle = readXmlTag(item, "title");
    const link = readXmlTag(item, "link");
    const pubDate = readXmlTag(item, "pubDate");

    if (!rawTitle || !link) {
      continue;
    }

    const { title, source } = splitTitleAndSource(rawTitle);
    const normalizedTitle = title.trim();

    if (seenTitles.has(normalizedTitle)) {
      continue;
    }

    seenTitles.add(normalizedTitle);

    articles.push({
      id: createArticleId(link, normalizedTitle),
      title: normalizedTitle,
      source: normalizeSource(source, link),
      date: formatRssDate(pubDate),
      link,
    });
  }

  return articles.sort((a, b) => b.date.localeCompare(a.date));
}

export function filterArticlesByDate(
  articles: NewsArticle[],
  startDate?: string,
  endDate?: string,
) {
  return articles.filter((article) => {
    if (startDate && article.date < startDate) {
      return false;
    }

    if (endDate && article.date > endDate) {
      return false;
    }

    return true;
  });
}

export async function fetchNewsArticles({
  startDate,
  endDate,
}: {
  startDate?: string;
  endDate?: string;
}) {
  const rssUrl = buildGoogleNewsRssUrl(`${getDefaultQuery()} when:30d`);
  const response = await fetch(rssUrl, {
    headers: {
      "User-Agent": "Mozilla/5.0",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Google News RSS request failed: ${response.status}`);
  }

  const rssText = await response.text();
  const filteredArticles = filterArticlesByDate(
    parseGoogleNewsRss(rssText),
    startDate,
    endDate,
  );

  return resolveOriginalArticleLinks(filteredArticles);
}

export async function getOriginalUrl(link: string, fetcher = fetch) {
  if (!isHttpUrl(link)) {
    return link;
  }

  try {
    const response = await fetcher(link, {
      headers: {
        "User-Agent": "Mozilla/5.0",
      },
      redirect: "follow",
      cache: "no-store",
    });

    if (response.url && isHttpUrl(response.url) && !isGoogleUrl(response.url)) {
      return response.url;
    }

    const html = await response.text();
    const canonicalUrl = extractCanonicalUrl(html);

    if (canonicalUrl && isHttpUrl(canonicalUrl) && !isGoogleUrl(canonicalUrl)) {
      return canonicalUrl;
    }

    const tokens = extractGoogleNewsTokens(html);

    if (tokens) {
      const decodedUrl = await decodeGoogleNewsUrl(tokens, fetcher);

      if (decodedUrl) {
        return decodedUrl;
      }
    }

    const externalUrl = extractFirstExternalUrl(html, link);

    if (externalUrl) {
      return externalUrl;
    }
  } catch {
    return link;
  }

  return link;
}

function splitTitleAndSource(rawTitle: string) {
  const title = decodeXml(rawTitle);
  const separatorIndex = title.lastIndexOf(" - ");

  if (separatorIndex === -1) {
    return {
      title,
      source: "",
    };
  }

  return {
    title: title.slice(0, separatorIndex),
    source: title.slice(separatorIndex + 3),
  };
}

function readXmlTag(xml: string, tagName: string) {
  const match = xml.match(new RegExp(`<${tagName}[^>]*>([\\s\\S]*?)<\\/${tagName}>`));

  if (!match) {
    return "";
  }

  return decodeXml(match[1].replace(/^<!\[CDATA\[/, "").replace(/\]\]>$/, ""));
}

function decodeXml(value: string) {
  return value
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function formatRssDate(pubDate: string) {
  const date = new Date(pubDate);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toISOString().slice(0, 10);
}

async function resolveOriginalArticleLinks(articles: NewsArticle[]) {
  const resolvedArticles: NewsArticle[] = [];

  for (const article of articles) {
    const originalLink = await getOriginalUrl(article.link);

    resolvedArticles.push({
      ...article,
      link: originalLink,
      source: normalizeSource(article.source, originalLink),
    });
  }

  return resolvedArticles;
}

function isHttpUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

function isGoogleUrl(value: string) {
  const host = getUrlHost(value);

  return (
    host.includes("google.") ||
    host.endsWith("gstatic.com") ||
    host.endsWith("googleusercontent.com")
  );
}

function getUrlHost(value: string) {
  try {
    return new URL(value).hostname.toLowerCase();
  } catch {
    return "";
  }
}

function extractCanonicalUrl(html: string) {
  const canonicalMatch = html.match(
    /<link[^>]+rel=["']canonical["'][^>]+href=["']([^"']+)["']/i,
  );

  if (canonicalMatch) {
    return decodeXml(canonicalMatch[1]);
  }

  const reversedCanonicalMatch = html.match(
    /<link[^>]+href=["']([^"']+)["'][^>]+rel=["']canonical["']/i,
  );

  return reversedCanonicalMatch ? decodeXml(reversedCanonicalMatch[1]) : "";
}

function extractGoogleNewsTokens(html: string) {
  const articleIdMatch = html.match(/data-n-a-id=["']([^"']+)["']/);
  const timestampMatch = html.match(/data-n-a-ts=["']([^"']+)["']/);
  const signatureMatch = html.match(/data-n-a-sg=["']([^"']+)["']/);

  if (!articleIdMatch || !timestampMatch || !signatureMatch) {
    return null;
  }

  return {
    articleId: articleIdMatch[1],
    timestamp: timestampMatch[1],
    signature: signatureMatch[1],
  };
}

async function decodeGoogleNewsUrl(
  tokens: {
    articleId: string;
    timestamp: string;
    signature: string;
  },
  fetcher = fetch,
) {
  const requestPayload = [
    "garturlreq",
    [
      [
        "en-US",
        "US",
        ["FINANCE_TOP_INDICES", "GENESIS_PUBLISHER_SECTION", "WEB_TEST_1_0_0"],
        null,
        null,
        1,
        1,
        "US:en",
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        false,
      ],
      "en-US",
      "US",
      true,
      [3, 5, 9, 19],
      1,
      true,
      "929622352",
      null,
      null,
      null,
      false,
    ],
    tokens.articleId,
    Number(tokens.timestamp),
    tokens.signature,
  ];

  const batchPayload = [
    [["Fbv4je", JSON.stringify(requestPayload), null, "generic"]],
  ];

  try {
    const response = await fetcher(GOOGLE_NEWS_BATCH_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
      },
      body: new URLSearchParams({
        "f.req": JSON.stringify(batchPayload),
      }),
      cache: "no-store",
    });

    return parseBatchExecuteResponse(await response.text());
  } catch {
    return "";
  }
}

function parseBatchExecuteResponse(responseText: string) {
  const payload = responseText.startsWith(")]}'")
    ? responseText.split("\n", 2)[1]
    : responseText;

  try {
    const rows = JSON.parse(payload) as unknown[];

    for (const row of rows) {
      if (!Array.isArray(row) || row[0] !== "wrb.fr" || row[1] !== "Fbv4je") {
        continue;
      }

      const result = JSON.parse(String(row[2])) as unknown[];

      if (result[0] === "garturlres" && typeof result[1] === "string") {
        return result[1];
      }
    }
  } catch {
    return "";
  }

  return "";
}

function extractFirstExternalUrl(html: string, baseUrl: string) {
  const linkMatches = html.matchAll(/<a[^>]+href=["']([^"']+)["']/gi);

  for (const linkMatch of linkMatches) {
    let href = "";

    try {
      href = new URL(decodeXml(linkMatch[1]), baseUrl).toString();
    } catch {
      continue;
    }

    if (isHttpUrl(href) && !isGoogleUrl(href)) {
      return href;
    }
  }

  return "";
}

function createArticleId(link: string, title: string) {
  const base = `${link}:${title}`;
  let hash = 0;

  for (let index = 0; index < base.length; index += 1) {
    hash = (hash * 31 + base.charCodeAt(index)) >>> 0;
  }

  return `article-${hash.toString(16)}`;
}
