import { createClient } from "@supabase/supabase-js";
import {
  getSupabasePublicKey,
  getSupabaseServerKey,
  getSupabaseUrl,
} from "./env";

type SupabaseServerClientOptions = {
  admin?: boolean;
};

export function createSupabaseServerClient(
  options: SupabaseServerClientOptions = {},
) {
  return createClient(
    getSupabaseUrl(),
    options.admin ? getSupabaseServerKey() : getSupabasePublicKey(),
    {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
    },
  );
}

