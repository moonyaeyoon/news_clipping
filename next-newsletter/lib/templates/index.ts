import type { NewsArticle } from "@/lib/news";

export type NewsletterTemplate = "blue-basic" | "orange-card";

type GenerateNewsletterHtmlInput = {
  template: NewsletterTemplate;
  reportDate: string;
  articles: NewsArticle[];
};

const BIZ_BUTTON_IMAGE_URL =
  "https://res.cloudinary.com/dys1jifiy/image/upload/v1782117221/BIZ-Btn_rw8rux.png";
const BITHUMB_BIZ_URL = "https://www.bithumb.com/react/biz/intro";

export function generateNewsletterHtml({
  template,
  reportDate,
  articles,
}: GenerateNewsletterHtmlInput) {
  if (template === "orange-card") {
    return generateOrangeCardHtml(reportDate, articles);
  }

  return generateBlueBasicHtml(reportDate, articles);
}

export function formatReportDate(date = new Date()) {
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
  return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()} (${weekdays[date.getDay()]})`;
}

function generateOrangeCardHtml(reportDate: string, articles: NewsArticle[]) {
  const articleRows = articles
    .map((article) => articleRow(article, "#252525", "#777777"))
    .join("");

  return emailDocument(`
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#ffffff;">
      <tr>
        <td align="center" style="padding:0;">
          <table role="presentation" width="760" cellpadding="0" cellspacing="0" style="width:760px;border-collapse:collapse;background:#ffffff;">
            <tr>
              <td style="padding:0;">
                <table role="presentation" width="760" cellpadding="0" cellspacing="0" style="width:760px;border-collapse:collapse;background:#10141f;color:#ffffff;">
                  <tr>
                    <td style="padding:36px 52px 34px;font-family:'SUIT',sans-serif;">
                      <div style="font-size:18px;font-weight:800;color:#ff6b00;line-height:24px;">빗썸 biz</div>
                      <div style="font-size:34px;font-weight:800;line-height:46px;margin-top:4px;">법인 디지털자산 시장 동향</div>
                    </td>
                    <td align="right" style="padding:0 42px 24px 0;font-family:'SUIT',sans-serif;font-size:16px;font-weight:500;color:#ffffff;vertical-align:bottom;">${escapeHtml(reportDate)}</td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td align="center" style="padding:54px 0 46px;background:#ffffff;">
                <table role="presentation" width="620" cellpadding="0" cellspacing="0" style="width:620px;border-collapse:collapse;">
                  ${articleRows}
                  ${bizButtonRow()}
                </table>
              </td>
            </tr>
            ${footerRow()}
          </table>
        </td>
      </tr>
    </table>
  `);
}

function generateBlueBasicHtml(reportDate: string, articles: NewsArticle[]) {
  const articleRows = articles
    .map((article) => articleRow(article, "#252525", "#777777"))
    .join("");

  return emailDocument(`
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#ffffff;">
      <tr>
        <td align="center">
          <table role="presentation" width="680" cellpadding="0" cellspacing="0" style="width:680px;border-collapse:collapse;background:#ffffff;">
            <tr>
              <td style="padding:30px 42px;background:#202530;color:#ffffff;font-family:'SUIT',sans-serif;">
                <div style="font-size:18px;font-weight:800;color:#ff6b00;">빗썸 biz</div>
                <div style="font-size:30px;font-weight:800;line-height:42px;">뉴스레터</div>
                <div style="font-size:14px;font-weight:500;margin-top:8px;">${escapeHtml(reportDate)}</div>
              </td>
            </tr>
            <tr>
              <td align="center" style="padding:42px 0;">
                <table role="presentation" width="540" cellpadding="0" cellspacing="0" style="width:540px;border-collapse:collapse;">
                  ${articleRows}
                  ${bizButtonRow()}
                </table>
              </td>
            </tr>
            ${footerRow()}
          </table>
        </td>
      </tr>
    </table>
  `);
}

function articleRow(article: NewsArticle, titleColor: string, metaColor: string) {
  return `
    <tr>
      <td style="padding:16px 0 15px;border-bottom:1px solid #d8d8d8;font-family:'SUIT',sans-serif;">
        <div style="font-size:13px;line-height:19px;color:${metaColor};font-weight:400;margin-bottom:5px;">
          ${escapeHtml(article.source)}&nbsp;&nbsp;${formatArticleDate(article.date)}
        </div>
        <a href="${escapeAttribute(article.link)}" target="_blank" rel="noopener noreferrer" style="font-size:19px;line-height:28px;font-weight:500;color:${titleColor};text-decoration:none;">
          ${escapeHtml(article.title)}
        </a>
      </td>
    </tr>
  `;
}

function bizButtonRow() {
  return `
    <tr>
      <td align="center" style="padding:34px 0 0;">
        <a href="${BITHUMB_BIZ_URL}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">
          <img src="${BIZ_BUTTON_IMAGE_URL}" alt="빗썸 BIZ 바로가기" width="123" height="42" style="display:block;border:0;width:123px;height:42px;" />
        </a>
      </td>
    </tr>
  `;
}

function footerRow() {
  return `
    <tr>
      <td style="padding:24px 56px;background:#292d32;color:#ffffff;font-family:'SUIT',sans-serif;font-size:12px;line-height:19px;">
        본 뉴스레터는 신뢰할 수 있는 정보 제공을 목적으로 작성되었으며, 어떠한 경우에도 투자 조언 또는 법률·세무 자문을 구성하지 않습니다.<br />
        투자 결정에 따른 책임은 투자자 본인에게 있습니다. 더 깊이 있는 인사이트와 귀사에 최적화된 솔루션이 필요하시면 빗썸 BIZ를 찾아주세요.<br /><br />
        문의하기: 1661-5566 (2번, 법인 전용 상담 창구)<br />
        이메일: <a href="mailto:biz@bithumbcorp.com" style="color:#ffffff;">biz@bithumbcorp.com</a>
      </td>
    </tr>
  `;
}

function emailDocument(body: string) {
  return `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link href="https://cdn.jsdelivr.net/gh/sun-typeface/SUIT@2/fonts/static/woff2/SUIT.css" rel="stylesheet" />
<title>빗썸 BIZ 뉴스레터</title>
</head>
<body style="margin:0;padding:0;background:#ffffff;font-family:'SUIT',sans-serif;">
${body.trim()}
</body>
</html>`;
}

function formatArticleDate(date: string) {
  const [, month, day] = date.split("-");

  if (!month || !day) {
    return "";
  }

  return `(${Number(month)}/${Number(day)})`;
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeAttribute(value: string) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

