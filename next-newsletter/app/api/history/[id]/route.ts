import { NextResponse } from "next/server";
import { resolveOriginalArticle } from "@/lib/news";
import { createSupabaseServerClient } from "@/lib/supabase";

type RouteContext = {
  params: Promise<{
    id: string;
  }>;
};

export async function GET(_request: Request, context: RouteContext) {
  const { id } = await context.params;
  const supabase = createSupabaseServerClient({ admin: true });

  const { data: history, error: historyError } = await supabase
    .from("history")
    .select("id,start_date,end_date,article_count,created_at")
    .eq("id", id)
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

  const { data: details, error: detailsError } = await supabase
    .from("history_details")
    .select("id,title,source,published_date,link")
    .eq("history_id", id)
    .order("created_at", {
      ascending: true,
    });

  if (detailsError) {
    return NextResponse.json(
      {
        ok: false,
        message: detailsError.message,
      },
      { status: 500 },
    );
  }

  const articles = await Promise.all(
    (details ?? []).map((detail) =>
      resolveOriginalArticle({
        id: detail.id,
        title: detail.title,
        source: detail.source ?? "",
        date: detail.published_date ?? "",
        link: detail.link,
      }),
    ),
  );

  return NextResponse.json({
    ok: true,
    history,
    articles,
  });
}
