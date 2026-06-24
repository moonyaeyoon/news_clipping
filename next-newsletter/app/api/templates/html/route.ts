import { NextResponse } from "next/server";
import type { NewsArticle } from "@/lib/news";
import {
  formatReportDate,
  generateNewsletterHtml,
  type NewsletterTemplate,
} from "@/lib/templates";

type GenerateHtmlRequestBody = {
  template?: NewsletterTemplate;
  articles?: NewsArticle[];
};

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as GenerateHtmlRequestBody;
    const articles = body.articles ?? [];

    const html = generateNewsletterHtml({
      template: body.template ?? "default",
      reportDate: formatReportDate(),
      articles,
    });

    return NextResponse.json({
      ok: true,
      html,
    });
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}
