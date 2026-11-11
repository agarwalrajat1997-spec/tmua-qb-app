from pathlib import Path
import re

ROUTE_PATH = Path("app/api/tmua/overview/route.ts")
COMPONENT_PATH = Path("app/dashboard/TmuaPredictionStrip.tsx")

HELPER = r"""
function finiteOverviewNumber(value: unknown): number | null {
  const result = Number(value);
  return Number.isFinite(result) ? result : null;
}

function overviewInteger(value: unknown): number {
  const result = Number(value);
  return Number.isInteger(result) && result >= 0 ? result : 0;
}

function overviewFraction(value: unknown): number {
  const result = finiteOverviewNumber(value);
  return result === null ? 0 : Math.min(1, Math.max(0, result));
}

function predictorFromPreparationRank(preparationRank: any) {
  const score = finiteOverviewNumber(preparationRank?.predictedTmuaScore9);
  const hasEvidence =
    preparationRank?.hasGenuinePreparationEvidence === true &&
    score !== null;
  const broadTestFamilies = overviewInteger(
    preparationRank?.broadOrFullIndependentTestFamilies,
  );
  const recentTestFamilies = overviewInteger(
    preparationRank?.independentRecognisedTestFamilies30d,
  );

  return {
    modelVersion: `${String(
      preparationRank?.modelVersion ?? "tmua-preparation-rank-v1-20260810",
    )}-saved-overview`,
    status: hasEvidence ? "predicted" : "insufficient_evidence",
    score: hasEvidence ? score : null,
    lowerBound: null,
    upperBound: null,
    confidence: null,
    testEvidenceCount: broadTestFamilies,
    independentTestCount: Math.max(
      broadTestFamilies,
      recentTestFamilies,
    ),
    qbUniqueQuestions: overviewInteger(
      preparationRank?.trustedUniqueFirstExposures,
    ),
    qbTopicCoverage: overviewFraction(
      preparationRank?.trustedCanonicalTopicCoverage,
    ),
    calculatedAt:
      typeof preparationRank?.calculatedAt === "string"
        ? preparationRank.calculatedAt
        : new Date().toISOString(),
  };
}

function useSavedTmuaOverview() {
  // Production serves the bounded, already-computed current-user snapshot.
  // Local and verification environments retain the full authoritative path.
  return (
    process.env.VERCEL === "1" &&
    process.env.TMUA_OVERVIEW_FORCE_LIVE !== "1"
  );
}
""".strip()

FAST_PATH = r"""
    if (useSavedTmuaOverview()) {
      const preparationRank = await readPreparationRankSnapshot(
        admin,
        user.id,
        "tmua",
        user.email,
      );

      return json({
        ok: true,
        viewerId: user.id,
        predictor: predictorFromPreparationRank(preparationRank),
        preparationRank,
        countdown: preparationCountdown(new Date()),
      });
    }

"""

route = ROUTE_PATH.read_text(encoding="utf-8")

helper_marker = "function useSavedTmuaOverview()"
get_anchor = "export async function GET(request: Request) {"
if helper_marker not in route:
    if get_anchor not in route:
        raise SystemExit("GET route anchor not found")
    route = route.replace(get_anchor, HELPER + "\n\n" + get_anchor, 1)

fast_marker = "predictor: predictorFromPreparationRank(preparationRank)"
refresh_pattern = re.compile(
    r'(?P<indent>[ \t]*)requestPreparationRankRefresh\(\s*admin\s*,\s*"tmua"\s*,?\s*\);\s*\n'
)
if fast_marker not in route:
    match = refresh_pattern.search(route)
    if not match:
        raise SystemExit("rank refresh anchor not found")
    route = route[:match.end()] + "\n" + FAST_PATH + route[match.end():]

if route.count(helper_marker) != 1:
    raise SystemExit("saved overview helper must appear exactly once")
if route.count(fast_marker) != 1:
    raise SystemExit("saved overview fast path must appear exactly once")

ROUTE_PATH.write_text(route, encoding="utf-8")

component = COMPONENT_PATH.read_text(encoding="utf-8")
component, replacements = re.subn(
    r'\n\s*\|\|\s*\n\s*predictor\.score\s*<\s*\n\s*3\.5',
    '',
    component,
    count=1,
)
if replacements != 1 and re.search(r'predictor\.score\s*<\s*3\.5', component):
    raise SystemExit("low-score display gate was not removed")
COMPONENT_PATH.write_text(component, encoding="utf-8")
