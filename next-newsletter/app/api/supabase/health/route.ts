import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function GET() {
  try {
    const supabase = createSupabaseServerClient();

    const { count, error } = await supabase
      .from("history")
      .select("id", {
        count: "exact",
        head: true,
      });

    if (error) {
      return NextResponse.json(
        {
          ok: false,
          connected: true,
          tableReady: false,
          message:
            "Supabase connection works, but the history table is not ready.",
          detail: error.message,
        },
        { status: 200 },
      );
    }

    return NextResponse.json({
      ok: true,
      connected: true,
      tableReady: true,
      historyCount: count ?? 0,
    });
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        connected: false,
        tableReady: false,
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

