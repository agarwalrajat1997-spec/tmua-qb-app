export type MathJaxApi = {
  startup: { promise: Promise<void> };
  typesetPromise: (elements: HTMLElement[]) => Promise<void>;
  typesetClear: (elements: HTMLElement[]) => void;
};
export function mathJaxConfig() {
  return {
    loader: {
      paths: { mathjax: "/tmua-studio/vendor/mathjax" },
      load: ["ui/safe", "[tex]/mathtools"],
    },
    startup: { typeset: false },
    tex: {
      inlineMath: [["\\(", "\\)"]],
      displayMath: [
        ["\\[", "\\]"],
        ["$$", "$$"],
      ],
      processEscapes: true,
      packages: { "[-]": ["require", "autoload"], "[+]": ["ams", "mathtools"] },
      maxMacros: 1000,
      maxBuffer: 20000,
    },
    svg: { fontCache: "local" },
    output: { font: "mathjax-newcm", fontPath: "/tmua-studio/vendor/mathjax/newcm" },
    options: {
      enableMenu: false,
      safeOptions: {
        allow: {
          URLs: "none",
          classes: "none",
          cssIDs: "none",
          styles: "none",
        },
      },
    },
  };
}
let loading: Promise<MathJaxApi> | undefined;
export function loadMathJax(): Promise<MathJaxApi> {
  if (loading) return loading;
  loading = new Promise((resolve, reject) => {
    const win = window as unknown as { MathJax: any };
    win.MathJax = mathJaxConfig();
    const script = document.createElement("script");
    script.src = "/tmua-studio/vendor/mathjax/tex-svg.js";
    script.async = true;
    script.onload = () => {
      if (!win.MathJax?.startup?.promise) {
        reject(Error("Math renderer unavailable"));
        return;
      }
      win.MathJax.startup.promise.then(() => resolve(win.MathJax), reject);
    };
    script.onerror = () => {
      script.remove();
      loading = undefined;
      reject(
        Error("Math renderer could not load. Reopen the question to retry."),
      );
    };
    document.head.appendChild(script);
  });
  return loading;
}
// Serialize DOM replacement as well as typesetting so rapid navigation cannot
// leave MathJax references pointing at replaced or unmounted content.
let tasks = Promise.resolve();
export function queueMath(action: (math: MathJaxApi) => Promise<void> | void) {
  const task = tasks.then(async () => action(await loadMathJax()));
  tasks = task.catch(() => {});
  return task;
}
