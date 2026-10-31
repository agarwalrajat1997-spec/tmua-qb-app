import { loadMathJax } from "./mathjax";

let warming: Promise<void> | undefined;
// Local rendering assets only. This never uploads work or calls the tutor.
export function warmFeedbackAssets() {
  if (warming) return warming;
  warming = Promise.all([
    loadMathJax(),
    document.fonts?.load('400 18px "Kalam"'),
    document.fonts?.load('700 18px "Kalam"'),
  ]).then(() => {});
  void warming.catch(() => {
    warming = undefined;
  });
  return warming;
}

export function scheduleFeedbackWarmup() {
  const warm = () => {
    void warmFeedbackAssets().catch(() => {});
  };
  if ("requestIdleCallback" in window) {
    const id = window.requestIdleCallback(warm, { timeout: 2000 });
    return () => window.cancelIdleCallback(id);
  }
  const id = setTimeout(warm, 250);
  return () => clearTimeout(id);
}
