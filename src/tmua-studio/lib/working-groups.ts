import type { ReviewRegion, WorkingGroup } from "../types";

// Free geometric preparation. The final model can refine these proposed groups
// after reading the complete argument; no partial mathematical claims are made.
export function workingGroups(regions: ReviewRegion[]): WorkingGroup[] {
  const count = regions.length;
  if (!count) return [];
  const target = Math.min(
    count,
    Math.max(2, Math.min(6, Math.ceil(count / 3))),
  );
  const clusters = regions.map((r) => [r]);
  while (clusters.length > target) {
    let best = 0,
      cost = Infinity;
    for (let i = 0; i < clusters.length - 1; i++) {
      const a = clusters[i],
        b = clusters[i + 1],
        last = a.at(-1)!,
        first = b[0];
      const gap =
        last.kind !== first.kind
          ? 10000
          : last.kind === "typed"
            ? 8
            : Math.max(0, first.box.y - last.box.y - last.box.h);
      const score = gap + Math.pow(a.length + b.length, 1.6) * 8;
      if (score < cost) {
        cost = score;
        best = i;
      }
    }
    clusters.splice(best, 2, [...clusters[best], ...clusters[best + 1]]);
  }
  return clusters.map((rs, i) => ({
    id: `box-${i + 1}`,
    regionIds: rs.map((r) => r.id),
  }));
}
