import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { isMissingSession } from "@/lib/auth/service-recovery";
import {
  ERASABLE_NOTEPAD_ACCESS_PRODUCTS,
  ERASABLE_NOTEPAD_CAMPAIGN_KEYS,
  ERASABLE_NOTEPAD_MAX_DISMISSALS,
} from "@/lib/erasable-notepad-popup";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type PopupResponse = {
  show: boolean;
  dismissed: boolean;
  dismissals: number;
  remaining: number;
};

function response(
  data: Partial<PopupResponse>,
  status = 200,
) {
  const dismissals = Math.max(
    0,
    Math.min(
      ERASABLE_NOTEPAD_MAX_DISMISSALS,
      Number(data.dismissals ?? 0),
    ),
  );

  return NextResponse.json(
    {
      show: data.show === true,
      dismissed: data.dismissed === true,
      dismissals,
      remaining: Math.max(
        0,
        ERASABLE_NOTEPAD_MAX_DISMISSALS - dismissals,
      ),
    } satisfies PopupResponse,
    {
      status,
      headers: {
        "Cache-Control": "private, no-store",
      },
    },
  );
}

function validAccessExpiry(value: unknown) {
  if (value == null) return true;
  const expires = Date.parse(String(value));
  return Number.isFinite(expires) && expires > Date.now();
}

async function hasEligiblePortalAccess(
  supabase: Awaited<ReturnType<typeof createSupabaseServerClient>>,
) {
  const { data, error } = await supabase
    .from("student_access")
    .select("product,approved,expires_at")
    .eq("approved", true)
    .in("product", [...ERASABLE_NOTEPAD_ACCESS_PRODUCTS]);

  if (error) throw error;

  return (data ?? []).some(
    (row) =>
      row.approved === true &&
      ERASABLE_NOTEPAD_ACCESS_PRODUCTS.includes(
        String(row.product) as
          (typeof ERASABLE_NOTEPAD_ACCESS_PRODUCTS)[number],
      ) &&
      validAccessExpiry(row.expires_at),
  );
}

async function readDismissedKeys(
  supabase: Awaited<ReturnType<typeof createSupabaseServerClient>>,
  userId: string,
) {
  const { data, error } = await supabase
    .from("student_popup_receipts")
    .select("campaign_key")
    .eq("user_id", userId)
    .in("campaign_key", [...ERASABLE_NOTEPAD_CAMPAIGN_KEYS]);

  if (error) throw error;

  return new Set(
    (data ?? []).map((row) => String(row.campaign_key)),
  );
}

export async function GET() {
  try {
    const supabase = await createSupabaseServerClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError) {
      return response(
        {},
        isMissingSession(authError) ? 401 : 503,
      );
    }
    if (!user) return response({}, 401);

    const eligible = await hasEligiblePortalAccess(supabase);
    if (!eligible) return response({});

    const dismissedKeys = await readDismissedKeys(
      supabase,
      user.id,
    );
    const dismissals = dismissedKeys.size;

    return response({
      show: dismissals < ERASABLE_NOTEPAD_MAX_DISMISSALS,
      dismissed: dismissals >= ERASABLE_NOTEPAD_MAX_DISMISSALS,
      dismissals,
    });
  } catch (error) {
    console.error(
      "Erasable-notepad popup eligibility failed",
      error instanceof Error ? error.message : error,
    );
    return response({}, 503);
  }
}

export async function POST(request: Request) {
  const origin = request.headers.get("origin");
  let sameOrigin = false;

  try {
    const parsed = new URL(origin || "");
    const host =
      request.headers.get("host") ||
      new URL(request.url).host;

    sameOrigin =
      (parsed.protocol === "https:" || parsed.protocol === "http:") &&
      parsed.origin === origin &&
      parsed.host.toLowerCase() === host.toLowerCase();
  } catch {
    // Missing or malformed origins are not browser portal requests.
  }

  if (!sameOrigin) return response({}, 403);

  const body = await request.json().catch(() => null);
  if (body?.action !== "dismiss") return response({}, 400);

  try {
    const supabase = await createSupabaseServerClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError) {
      return response(
        {},
        isMissingSession(authError) ? 401 : 503,
      );
    }
    if (!user) return response({}, 401);

    const eligible = await hasEligiblePortalAccess(supabase);
    if (!eligible) return response({}, 403);

    const dismissedKeys = await readDismissedKeys(
      supabase,
      user.id,
    );

    const nextKey = ERASABLE_NOTEPAD_CAMPAIGN_KEYS.find(
      (key) => !dismissedKeys.has(key),
    );

    if (nextKey) {
      const { error } = await supabase
        .from("student_popup_receipts")
        .insert({
          user_id: user.id,
          campaign_key: nextKey,
        });

      if (error && error.code !== "23505") {
        console.error(
          "Erasable-notepad popup dismissal could not be saved",
          error.code,
        );
        return response(
          { dismissals: dismissedKeys.size },
          503,
        );
      }
    }

    const finalKeys = await readDismissedKeys(
      supabase,
      user.id,
    );

    return response({
      dismissed: true,
      dismissals: finalKeys.size,
    });
  } catch (error) {
    console.error(
      "Erasable-notepad popup dismissal failed",
      error instanceof Error ? error.message : error,
    );
    return response({}, 503);
  }
}
