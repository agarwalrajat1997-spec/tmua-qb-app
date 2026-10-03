import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const publicRoot = path.join(root, "public");
const archiveRoot = path.join(publicRoot, "amc-past-paper-practice");
const contentRoot = path.join(archiveRoot, "content");
const assetRoot = path.join(archiveRoot, "assets");
const localAssetPrefix = "/amc-past-paper-practice/assets/";
const knownImportedRichTags = new Set([
  "a", "b", "strong", "i", "em", "u", "br", "p", "div", "span", "ul", "ol", "li",
  "table", "thead", "tbody", "tr", "td", "th", "img", "sup", "sub",
]);

const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function listFilesRecursive(directory) {
  if (!fs.existsSync(directory)) return [];

  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(directory, entry.name);
    return entry.isDirectory() ? listFilesRecursive(entryPath) : [entryPath];
  });
}

function assertNonemptyRichText(value, label) {
  assert(typeof value === "string" && value.trim().length > 0, `${label} must be nonempty`);
  const visibleText = value
    .replace(/<[^>]*>/g, " ")
    .replace(/&(?:nbsp|#160);/gi, " ")
    .replace(/\\[()[\]]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  assert(visibleText.length > 0 || /<img\b/i.test(value), `${label} has no readable content`);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function extractImageSources(fragment, label) {
  const sources = [];
  for (const tag of fragment.match(/<img\b[^>]*>/gi) ?? []) {
    const source = tag.match(/\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/i);
    assert(source, `${label} contains an image without a src attribute`);
    sources.push(source[1] ?? source[2] ?? source[3]);
  }
  return sources;
}

function assertKnownRichMarkup(fragment, label) {
  const tagPattern = /<\/?\s*([A-Za-z][\w:-]*)\b[^>]*>/g;
  let cursor = 0;

  for (const match of fragment.matchAll(tagPattern)) {
    const precedingText = fragment.slice(cursor, match.index);
    assert(!precedingText.includes("<"), `${label} contains an unescaped less-than sign`);

    const tag = match[1].toLowerCase();
    assert(knownImportedRichTags.has(tag), `${label} contains an unknown HTML tag: <${tag}>`);
    cursor = match.index + match[0].length;
  }

  assert(!fragment.slice(cursor).includes("<"), `${label} contains an unescaped less-than sign`);
}

function assertSafeRichText(fragment, label, referencedAssets) {
  assertKnownRichMarkup(fragment, label);
  assert(!/<\s*(?:script|iframe|object|embed|style|link|meta|base)\b/i.test(fragment), `${label} contains a forbidden embed`);
  assert(!/\son[a-z]+\s*=/i.test(fragment), `${label} contains an inline event handler`);
  assert(!/(?:src|href)\s*=\s*["']?\s*javascript:/i.test(fragment), `${label} contains a javascript URL`);

  for (const source of extractImageSources(fragment, label)) {
    assert(source.startsWith(localAssetPrefix), `${label} embeds a non-local image: ${source}`);
    assert(!source.includes("\\") && !source.includes(".."), `${label} contains an unsafe image path: ${source}`);

    const pathname = source.split(/[?#]/, 1)[0];
    let decodedPath;
    try {
      decodedPath = decodeURIComponent(pathname);
    } catch {
      throw new Error(`${label} contains an invalid encoded image path: ${source}`);
    }

    const relativePath = decodedPath.replace(/^\/+/, "");
    const absolutePath = path.resolve(publicRoot, relativePath);
    const allowedPrefix = `${path.resolve(assetRoot)}${path.sep}`;
    assert(absolutePath.startsWith(allowedPrefix), `${label} image escapes the AMC asset directory: ${source}`);
    assert(fs.existsSync(absolutePath) && fs.statSync(absolutePath).isFile(), `${label} references a missing image: ${source}`);
    referencedAssets.add(absolutePath);
  }
}

function assertSafeSvg(file) {
  if (path.extname(file).toLowerCase() !== ".svg") return;
  const svg = fs.readFileSync(file, "utf8");
  const label = path.relative(root, file);
  assert(!/<\s*(?:script|iframe|object|embed|foreignObject)\b/i.test(svg), `${label} contains unsafe SVG markup`);
  assert(!/\son[a-z]+\s*=/i.test(svg), `${label} contains an SVG event handler`);
  assert(!/(?:href|xlink:href)\s*=\s*["']?\s*(?:https?:|\/\/|javascript:|data:)/i.test(svg), `${label} contains an unsafe SVG reference`);
}

const archive = JSON.parse(read("public/amc-past-paper-practice/archive.json"));
const html = read("public/amc-past-paper-practice/index.html");
const dashboard = read("app/dashboard/AMCDashboardClient.tsx");
const portal = read("app/amc/page.tsx");
const normalizedDashboard = dashboard.replace(/\s+/g, " ");

const allowedClientTags = html.match(/const ALLOWED_RICH_TAGS = new Set\(\[([\s\S]*?)\]\);/)?.[1] ?? "";
const clientAllowsAnchors = /["']a["']/.test(allowedClientTags);
const clientUnwrapsUnknownTags =
  html.includes("if (!ALLOWED_RICH_TAGS.has(tag))") &&
  html.includes("const unwrapped = document.createDocumentFragment();");
assert(
  !clientAllowsAnchors && clientUnwrapsUnknownTags,
  "AMC client sanitizer must safely unwrap imported anchor tags rather than preserve their links",
);

assert(archive.counts.problems === 2325, "AMC archive must contain 2,325 problems");
assert(archive.counts.amc8 === 1025, "AMC 8 archive must contain 1,025 problems");
assert(archive.counts.amc10 === 1300, "AMC 10 archive must contain 1,300 problems");
assert(archive.counts.papers === 93, "AMC archive must contain 93 papers");
assert(archive.problems.length === 2325, "AMC archive count and payload differ");
assert(new Set(archive.problems.map((problem) => problem.id)).size === 2325, "AMC problem IDs must be unique");
assert(archive.problems.every((problem) => Array.isArray(problem.topics) && problem.topics.length > 0), "Every AMC problem needs a topic");
assert(
  archive.problems.every((problem) => /^https:\/\/live\.poshenloh\.com\/past-contests\/(?:amc8|amc10)\//.test(problem.sourceUrl)),
  "Every AMC problem must link to its credited archive source",
);

const archiveById = new Map(archive.problems.map((problem) => [problem.id, problem]));
const expectedShardNames = new Set(
  archive.problems.map((problem) => `${problem.contest === "AMC 8" ? "amc8" : "amc10"}-${String(problem.paper).toLowerCase()}.json`),
);
assert(expectedShardNames.size === 93, "AMC metadata must resolve to exactly 93 paper shards");

assert(fs.existsSync(contentRoot), "Missing AMC inline content directory");
const manifestPath = path.join(contentRoot, "manifest.json");
assert(fs.existsSync(manifestPath), "Missing AMC inline content manifest");
const manifest = readJson(manifestPath);

assert(manifest.schemaVersion === 1, "AMC content manifest must use schema version 1");
assert(manifest.totalPapers === 93, "AMC content manifest must list 93 papers");
assert(manifest.totalProblems === 2325, "AMC content manifest must list 2,325 problems");
assert(Number.isInteger(manifest.totalAssets) && manifest.totalAssets > 0, "AMC content manifest must report its local figure assets");
assert(Array.isArray(manifest.papers) && manifest.papers.length === 93, "AMC content manifest paper list must contain 93 entries");

const actualShardNames = fs
  .readdirSync(contentRoot, { withFileTypes: true })
  .filter((entry) => entry.isFile() && entry.name.endsWith(".json") && entry.name !== "manifest.json")
  .map((entry) => entry.name)
  .sort();
assert(actualShardNames.length === 93, `Expected 93 AMC content shards, found ${actualShardNames.length}`);
assert(
  actualShardNames.every((name) => expectedShardNames.has(name)) && expectedShardNames.size === actualShardNames.length,
  "AMC content shard filenames do not match the 93 indexed papers",
);

const manifestFiles = new Set();
const inlineById = new Map();
const referencedAssets = new Set();

for (const entry of manifest.papers) {
  assert(entry && typeof entry === "object", "Every AMC manifest paper entry must be an object");
  assert(typeof entry.file === "string" && path.basename(entry.file) === entry.file, "AMC manifest shard filenames must be local basenames");
  assert(expectedShardNames.has(entry.file), `Unexpected AMC manifest shard: ${entry.file}`);
  assert(!manifestFiles.has(entry.file), `Duplicate AMC manifest shard: ${entry.file}`);
  manifestFiles.add(entry.file);
  assert(entry.contest === "AMC 8" || entry.contest === "AMC 10", `${entry.file} has an invalid contest`);
  assert(typeof entry.paper === "string" && entry.paper.length > 0, `${entry.file} is missing its paper code`);
  assert(entry.problemCount === 25, `${entry.file} must contain 25 problems`);
  assert(Number.isInteger(entry.assetCount) && entry.assetCount >= 0, `${entry.file} has an invalid asset count`);
  assert(/^[a-f0-9]{64}$/i.test(entry.sha256), `${entry.file} is missing a valid SHA-256 checksum`);
  assert(/^https:\/\/live\.poshenloh\.com\/past-contests\/(?:amc8|amc10)\//.test(entry.sourceUrl), `${entry.file} has an invalid credited source URL`);

  const shardPath = path.join(contentRoot, entry.file);
  assert(fs.existsSync(shardPath), `Missing AMC content shard: ${entry.file}`);
  assert(sha256(shardPath) === entry.sha256.toLowerCase(), `${entry.file} does not match its manifest checksum`);
  const shard = readJson(shardPath);

  assert(shard.schemaVersion === 1, `${entry.file} must use schema version 1`);
  assert(shard.contest === entry.contest, `${entry.file} contest differs from the manifest`);
  assert(String(shard.paper) === entry.paper, `${entry.file} paper code differs from the manifest`);
  assert(shard.sourceUrl === entry.sourceUrl, `${entry.file} source URL differs from the manifest`);
  assert(Array.isArray(shard.problems) && shard.problems.length === 25, `${entry.file} must contain exactly 25 problems`);

  for (const problem of shard.problems) {
    const label = `${entry.file}:${problem?.id ?? "unknown problem"}`;
    assert(problem && typeof problem === "object", `${entry.file} contains an invalid problem record`);
    assert(typeof problem.id === "string" && archiveById.has(problem.id), `${label} is not present in archive.json`);
    assert(!inlineById.has(problem.id), `Duplicate inline AMC problem: ${problem.id}`);

    const indexed = archiveById.get(problem.id);
    assert(indexed.contest === shard.contest, `${label} contest does not match archive.json`);
    assert(String(indexed.paper) === String(shard.paper), `${label} paper does not match archive.json`);
    assert(problem.number === indexed.number, `${label} question number does not match archive.json`);
    assert(problem.sourceUrl === indexed.sourceUrl, `${label} credited source URL does not match archive.json`);
    assertNonemptyRichText(problem.question, `${label} question`);
    assertNonemptyRichText(problem.solution, `${label} solution`);

    assert(Array.isArray(problem.options) && problem.options.length === 5, `${label} must contain five answer choices`);
    const optionLabels = problem.options.map((option) => option?.label);
    assert(optionLabels.join("") === "ABCDE", `${label} answer choices must be labelled A-E in order`);
    for (const option of problem.options) {
      assertNonemptyRichText(option.content, `${label} option ${option.label}`);
    }
    assert(typeof problem.answer === "string" && /^[A-E]$/.test(problem.answer), `${label} must have an A-E answer`);
    assert(Array.isArray(problem.hints), `${label} hints must be an array`);
    problem.hints.forEach((hint, index) => assertNonemptyRichText(hint, `${label} hint ${index + 1}`));

    const fragments = [
      [problem.question, `${label} question`],
      [problem.solution, `${label} solution`],
      ...problem.options.map((option) => [option.content, `${label} option ${option.label}`]),
      ...problem.hints.map((hint, index) => [hint, `${label} hint ${index + 1}`]),
    ];
    for (const [fragment, fragmentLabel] of fragments) {
      assertSafeRichText(fragment, fragmentLabel, referencedAssets);
    }

    inlineById.set(problem.id, problem);
  }
}

assert(manifestFiles.size === actualShardNames.length, "AMC manifest does not cover every content shard");
assert(inlineById.size === 2325, `Expected 2,325 unique inline AMC problems, found ${inlineById.size}`);
assert(
  [...archiveById.keys()].every((id) => inlineById.has(id)),
  "Some indexed AMC problems are missing from the inline content shards",
);

for (const id of ["amc-8-1985-q1", "amc-10-2000-q1", "amc-10-2024a-q25"]) {
  assert(inlineById.has(id), `Representative inline AMC problem is missing: ${id}`);
}

const assetFiles = listFilesRecursive(assetRoot).sort();
assert(assetFiles.length === manifest.totalAssets, `Manifest reports ${manifest.totalAssets} assets, but ${assetFiles.length} local files exist`);
assert(referencedAssets.size === assetFiles.length, "Every downloaded AMC figure must be referenced by inline problem content");
for (const file of assetFiles) {
  assert(referencedAssets.has(file), `Unreferenced AMC figure: ${path.relative(root, file)}`);
  assertSafeSvg(file);
}

for (const file of [
  "public/amc-resources/amc-8-compendium.pdf",
  "public/amc-resources/amc-10-compendium.pdf",
]) {
  assert(fs.existsSync(path.join(root, file)), `Missing ${file}`);
}

for (const marker of [
  "2,325",
  "By topic",
  "By paper",
  'id="question-label">Question</p>',
  'id="solution-label">Worked solution</p>',
  "/shared/mathjax-tex-mml-chtml.js?v=3",
  "function contentFile(problem)",
  "const file = contentFile(problem);",
  "fetch(file)",
  "View credited source",
]) {
  assert(html.includes(marker), `AMC index HTML is missing ${marker}`);
}
assert(!html.includes("Open question + explanation"), "AMC index must not use the old external-link-only question action");

for (const marker of [
  "Past Papers",
  "/amc-past-paper-practice/index.html",
  "2,325 indexed problems",
  "Each question, all five answer choices and the worked solution appear together inside the archive",
]) {
  assert(normalizedDashboard.includes(marker), `AMC dashboard is missing ${marker}`);
}
assert(!dashboard.includes("opens the credited original question"), "AMC dashboard still describes the old external-link-only archive");
assert(portal.includes('section === "past-papers"'), "AMC portal must accept the past-papers section");

console.log(
  `AMC past-paper archive verified: ${inlineById.size.toLocaleString("en-GB")} inline questions and solutions, ${manifestFiles.size} papers, ${assetFiles.length} local figures.`,
);
