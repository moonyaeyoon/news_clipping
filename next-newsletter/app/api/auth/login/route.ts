import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { createSessionToken, AUTH_COOKIE_NAME, SESSION_MAX_AGE_SECONDS } from "@/lib/auth/session";
import { verifyPassword } from "@/lib/auth/password";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const runtime = "nodejs";

type LoginRequestBody = {
  loginId?: string;
  password?: string;
};

export async function POST(request: Request) {
  const body = (await request.json()) as LoginRequestBody;
  const loginId = body.loginId?.trim() ?? "";
  const password = body.password ?? "";

  if (!loginId || !password) {
    return NextResponse.json(
      {
        ok: false,
        message: "아이디와 비밀번호를 입력하세요.",
      },
      { status: 400 },
    );
  }

  const supabase = createSupabaseServerClient({ admin: true });
  const { data: user, error } = await supabase
    .from("users")
    .select("id,login_id,password_hash")
    .eq("login_id", loginId)
    .single();

  if (error || !user || !verifyPassword(password, user.password_hash)) {
    return NextResponse.json(
      {
        ok: false,
        message: "아이디 또는 비밀번호가 올바르지 않습니다.",
      },
      { status: 401 },
    );
  }

  const token = await createSessionToken({
    userId: user.id,
    loginId: user.login_id,
  });
  const cookieStore = await cookies();

  cookieStore.set(AUTH_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE_SECONDS,
  });

  return NextResponse.json({
    ok: true,
  });
}
