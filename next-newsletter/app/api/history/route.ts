import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase";

export async function GET() {
  const supabase = createSupabaseServerClient({ admin: true });

  const { data, error } = await supabase
    .from("history")
    .select(
      `
      id,
      start_date,
      end_date,
      article_count,
      created_at
    `,
    )
    .order("created_at", {
      ascending: false,
    })
    .limit(20);

  if (error) {
    return NextResponse.json(
      {
        ok: false,
        message: error.message,
      },
      { status: 500 },
    );
  }

  return NextResponse.json({
    ok: true,
    histories: data,
  });
}

