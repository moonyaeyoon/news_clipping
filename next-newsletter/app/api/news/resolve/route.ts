import { NextResponse } from "next/server";
import { resolveOriginalArticle, type NewsArticle } from "@/lib/news";

type ResolveRequestBody = {
  articles?: NewsArticle[];
};

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as ResolveRequestBody;
    const articles = await Promise.all(
      (body.articles ?? []).map((article) => resolveOriginalArticle(article)),
    );

    return NextResponse.json({
      ok: true,
      articles,
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
