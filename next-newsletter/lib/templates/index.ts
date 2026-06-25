import fs from "node:fs";
import path from "node:path";
import type { NewsArticle } from "@/lib/news";

export type NewsletterTemplate =
  | "default"
  | "large"
  | "orange"
  | "orange_no_sidebar"
  | "orange_card"
  | "blue_card";

type GenerateNewsletterHtmlInput = {
  template: NewsletterTemplate;
  reportDate: string;
  articles: NewsArticle[];
};

const TEMPLATE_FILES: Record<NewsletterTemplate, string> = {
  default: "blue-basic.html",
  large: "blue-large.html",
  orange: "orange-basic.html",
  orange_no_sidebar: "orange-no-sidebar.html",
  orange_card: "orange-card.html",
  blue_card: "blue-card.html",
};

const TEMPLATE_DIR = path.join(process.cwd(), "templates");
const IMAGE_URLS = {
  header_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1781750322/header_blue_oguscv.svg",
  footer_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1781763779/footer_ver1.4_vual7u.png",
  orange_header_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1782197788/header-og_hns352.png",
  card_blue_header_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1781750322/header_blue_oguscv.svg",
  orange_sidebar_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1782175688/sidebar_ebyxau.png",
  orange_building_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1782178324/image_1_tlmvlj.png",
  card_sky_background_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1782201609/bg-sky_hduhxx.png",
  biz_button_image_url:
    "https://res.cloudinary.com/dys1jifiy/image/upload/v1782117221/BIZ-Btn_rw8rux.png",
  bithumb_biz_url: "https://www.bithumb.com/react/biz/intro",
};

export function generateNewsletterHtml({
  template,
  reportDate,
  articles,
}: GenerateNewsletterHtmlInput) {
  const templatePath = path.join(TEMPLATE_DIR, TEMPLATE_FILES[template]);
  const source = fs.readFileSync(templatePath, "utf-8");

  return renderTemplate(source, {
    report_date: reportDate,
    ...IMAGE_URLS,
    articles: articles.map((article) => ({
      title: article.title,
      source: article.source,
      date: formatArticleDate(article.date),
      link: article.link,
    })),
  });
}

export function formatReportDate(date = new Date()) {
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
  return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()} (${weekdays[date.getDay()]})`;
}

function renderTemplate(
  source: string,
  context: Record<string, string | Array<Record<string, string>>>,
) {
  const withLoops = source.replace(
    /{% for article in articles %}([\s\S]*?){% endfor %}/g,
    (_match, articleTemplate: string) =>
      (context.articles as Array<Record<string, string>>)
        .map((article) =>
          articleTemplate.replace(
            /{{\s*article\.(title|source|date|link)\s*}}/g,
            (_articleMatch: string, key: string) =>
              key === "link" ? escapeAttribute(article[key]) : escapeHtml(article[key]),
          ),
        )
        .join(""),
  );

  return withLoops.replace(/{{\s*([a-zA-Z_]+)\s*}}/g, (_match, key: string) => {
    const value = context[key];

    return typeof value === "string" ? escapeAttribute(value) : "";
  });
}

function formatArticleDate(date: string) {
  const [, month, day] = date.split("-");

  if (!month || !day) {
    return date;
  }

  return `(${Number(month)}/${Number(day)})`;
}

function escapeHtml(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeAttribute(value = "") {
  return escapeHtml(value).replace(/`/g, "&#96;");
}
