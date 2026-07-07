import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { AUTH_COOKIE_NAME, verifySessionToken } from "@/lib/auth/session";
import { fetchNewsArticles, getDefaultQuery } from "@/lib/news";
import { createSupabaseServerClient } from "@/lib/supabase/server";

type SearchRequestBody = {
  startDate?: string;
  endDate?: string;
};

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as SearchRequestBody;
    const articles = await fetchNewsArticles({
      startDate: body.startDate,
      endDate: body.endDate,
    });
    const cookieStore = await cookies();
    const session = await verifySessionToken(
      cookieStore.get(AUTH_COOKIE_NAME)?.value,
    );
    const supabase = createSupabaseServerClient({ admin: true });

    const { data: history, error: historyError } = await supabase
      .from("history")
      .insert({
        user_id: session?.sub ?? null,
        start_date: body.startDate || null,
        end_date: body.endDate || null,
        article_count: articles.length,
      })
      .select("id")
      .single();

    if (historyError) {
      return NextResponse.json(
        {
          ok: false,
          message: historyError.message,
        },
        { status: 500 },
      );
    }

    if (articles.length) {
      const { error: detailsError } = await supabase
        .from("history_details")
        .insert(
          articles.map((article) => ({
            history_id: history.id,
            title: article.title,
            source: article.source,
            published_date: article.date || null,
            link: article.link,
          })),
        );

      if (detailsError) {
        return NextResponse.json(
          {
            ok: false,
            message: detailsError.message,
          },
          { status: 500 },
        );
      }
    }

    return NextResponse.json({
      ok: true,
      historyId: history.id,
      query: getDefaultQuery(),
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
