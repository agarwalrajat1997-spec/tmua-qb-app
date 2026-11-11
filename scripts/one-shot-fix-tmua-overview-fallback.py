from pathlib import Path
import re

component_path = Path("app/dashboard/TmuaPredictionStrip.tsx")
component = component_path.read_text(encoding="utf-8")

import_anchor = 'import ExamCountdown from "@/app/_components/ExamCountdown";\n'
fallback_import = 'import { supabaseBrowser } from "@/utils/supabase/browser";\n'
if fallback_import not in component:
    if import_anchor not in component:
        raise SystemExit("ExamCountdown import anchor not found")
    component = component.replace(import_anchor, import_anchor + fallback_import, 1)

helper_anchor = "function scoreText("
helper_block = r'''
function isOverviewResponse(value: unknown): value is OverviewResponse {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return false;
  }

  const overview = value as OverviewResponse;
  return (
    overview.ok === true &&
    typeof overview.viewerId === "string" &&
    overview.viewerId.length > 0 &&
    !!overview.predictor
  );
}

async function fetchSavedTmuaOverview(): Promise<OverviewResponse | null> {
  try {
    const supabase = supabaseBrowser();
    const { data: sessionData, error: sessionError } =
      await supabase.auth.getSession();
    const viewerId = sessionData.session?.user.id;

    if (sessionError || !viewerId) {
      return null;
    }

    const { data, error } =
      await supabase.rpc("get_my_tmua_overview");

    if (
      error ||
      !isOverviewResponse(data) ||
      data.viewerId !== viewerId
    ) {
      return null;
    }

    return data;
  } catch {
    return null;
  }
}

const tmuaOverviewFetch: typeof fetch = async (input, init) => {
  // Start the server endpoint so it can schedule rank maintenance, but render
  // from the caller-bound RPC immediately. This avoids a blank strip when the
  // Next.js session bridge or function runtime is temporarily unavailable.
  const primary = fetch(input, init).catch(() => null);
  const savedOverview = await fetchSavedTmuaOverview();

  if (savedOverview) {
    void primary;
    return new Response(
      JSON.stringify(savedOverview),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "no-store",
        },
      },
    );
  }

  const primaryResponse = await primary;
  if (primaryResponse) {
    return primaryResponse;
  }

  return new Response(
    JSON.stringify({ ok: false, error: "TMUA overview unavailable" }),
    {
      status: 503,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
      },
    },
  );
};

'''
if "async function fetchSavedTmuaOverview" not in component:
    if helper_anchor not in component:
        raise SystemExit("scoreText helper anchor not found")
    component = component.replace(helper_anchor, helper_block + helper_anchor, 1)

fetcher_old = "        fetcher: fetch,"
fetcher_new = "        fetcher: tmuaOverviewFetch,"
if fetcher_new not in component:
    if component.count(fetcher_old) != 1:
        raise SystemExit("overview fetcher anchor must appear exactly once")
    component = component.replace(fetcher_old, fetcher_new, 1)

silent_pattern = re.compile(
    r'''  if \(\n    !loaded \|\|\n    !overview\?\.predictor\n  \) \{\n    return null;\n  \}'''
)
visible_state = r'''  if (
    !loaded ||
    !overview?.predictor
  ) {
    return (
      <section
        className={styles.strip}
        aria-label="TMUA preparation overview"
        data-preparation-rank-model={PREPARATION_RANK_MODEL_NAME}
      >
        <div className={styles.copy}>
          <span className={styles.label}>TMUA score and rank</span>
          <strong className={styles.building}>
            {!loaded ? "are loading…" : "are temporarily unavailable."}
          </strong>
        </div>
      </section>
    );
  }'''
component, replacements = silent_pattern.subn(visible_state, component, count=1)
if replacements != 1 and "return null;" in component[component.find("export default function TmuaPredictionStrip"):]:
    raise SystemExit("silent TMUA overview state was not replaced")

for required in [
    fallback_import.strip(),
    'supabase.rpc("get_my_tmua_overview")',
    "fetcher: tmuaOverviewFetch",
    'TMUA score and rank',
    'are temporarily unavailable.',
]:
    if required not in component:
        raise SystemExit(f"missing patched component marker: {required}")

component_path.write_text(component, encoding="utf-8")

refresh_test_path = Path("scripts/verify-tmua-predictor-refresh.mjs")
refresh_test = refresh_test_path.read_text(encoding="utf-8")
mock_anchor = '    if (id === "@/app/_components/ExamCountdown") return () => null;\n'
mock_line = '''    if (id === "@/utils/supabase/browser") return { supabaseBrowser: () => ({\n      auth: { getSession: async () => ({ data: { session: null }, error: null }) },\n      rpc: async () => ({ data: null, error: { message: "fallback disabled in controller fixture" } }),\n    }) };\n'''
if mock_line not in refresh_test:
    if mock_anchor not in refresh_test:
        raise SystemExit("predictor refresh test dependency anchor not found")
    refresh_test = refresh_test.replace(mock_anchor, mock_anchor + mock_line, 1)
refresh_test_path.write_text(refresh_test, encoding="utf-8")

print("TMUA saved-overview fallback patch applied.")
