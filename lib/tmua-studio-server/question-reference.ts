import { parseDocument } from "htmlparser2";
type AnyNode = ReturnType<typeof parseDocument>["children"][number];
export type SourceQuestion = {
  exam?: string;
  difficulty?: number;
  qid: string;
  prompt_html: string;
  options: unknown;
  answer: string;
  solution_html: string;
  nice_tip_html?: string | null;
  shortcut_available?: boolean;
  updated_at?: string;
  content_version?: string;
  audited_reference?: unknown;
};
export function questionImages(q: SourceQuestion) {
  const images: { url: string; label: string }[] = [];
  const sources = [
    ["Question diagram", q.prompt_html],
    ...(Array.isArray(q.options)
      ? q.options.map((o) => [`Option ${o.label}`, o.html ?? ""])
      : []),
    ["Reference solution diagram", q.solution_html],
  ];
  for (const [label, html] of sources) {
    const walk = (node: AnyNode) => {
      if ("name" in node && node.name === "img" && "attribs" in node) {
        const url = node.attribs.src ?? "";
        const inline =
          /^data:image\/(png|jpeg|webp|gif);base64,[A-Za-z0-9+/]+=*$/.test(url);
        let remote = false;
        try {
          const u = new URL(url);
          remote =
            u.protocol === "https:" &&
            !u.username &&
            !u.password &&
            !/^(localhost|127\.|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.|\[)/.test(
              u.hostname,
            ) &&
            !/\.(local|internal)$/.test(u.hostname) &&
            !/\.svg(?:$|\?)/i.test(u.pathname);
        } catch {
          /* Invalid/missing visual is rejected, never silently omitted. */
        }
        if ((!inline && !remote) || url.length > 4_500_000)
          throw Error(
            "A question diagram needs a supported PNG, JPEG, WebP or GIF source before this question can be reviewed.",
          );
        if (!images.some((i) => i.url === url))
          images.push({
            url,
            label: `${label}${node.attribs.alt ? `: ${node.attribs.alt}` : ""}`,
          });
      }
      if ("name" in node && node.name === "svg")
        throw Error(
          "This question's vector diagram needs a raster reference before AI review. Your working is saved.",
        );
      if ("children" in node) node.children.forEach(walk);
    };
    parseDocument(html).children.forEach(walk);
  }
  if (images.length > 12)
    throw Error(
      "This question has too many reference diagrams for one review. Please report the question.",
    );
  return images;
}
export function referenceText(html: string): string {
  const visit = (node: AnyNode): string => {
    if (node.type === "text") return node.data;
    if ("name" in node && ["script", "style", "iframe"].includes(node.name))
      return "";
    const inner = "children" in node ? node.children.map(visit).join("") : "";
    if (!("name" in node)) return inner;
    if (node.name === "sup") return `^{${inner}}`;
    if (node.name === "sub") return `_{${inner}}`;
    if (node.name === "img" && "attribs" in node)
      return node.attribs.alt
        ? ` [Diagram: ${node.attribs.alt}] `
        : " [Question contains a diagram] ";
    if (["br", "p", "div", "li", "tr"].includes(node.name)) return inner + "\n";
    return inner;
  };
  return visit(parseDocument(html, { decodeEntities: true }))
    .replace(/[ \t]+/g, " ")
    .replace(/ *\n */g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
const cache = new WeakMap<SourceQuestion, ReturnType<typeof buildReference>>();
function buildReference(q: SourceQuestion) {
  return {
    qid: q.qid,
    question: referenceText(q.prompt_html),
    options: Array.isArray(q.options)
      ? q.options.map((o) => ({
          label: o.label,
          text: referenceText(o.html ?? ""),
        }))
      : q.options,
    answer: q.answer,
    solution: referenceText(q.solution_html),
    ...(q.audited_reference
      ? {
          audited_reference: q.audited_reference,
          content_version: q.content_version,
        }
      : {}),
    ...(q.shortcut_available && q.nice_tip_html
      ? { shortcut: referenceText(q.nice_tip_html) }
      : {}),
  };
}
export function questionReference(q: SourceQuestion) {
  let r = cache.get(q);
  if (!r) {
    r = buildReference(q);
    cache.set(q, r);
  }
  return r;
}
