import { createHash } from "node:crypto";
import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const publicRoot = path.join(repoRoot, "public", "amc-past-paper-practice");
const archivePath = path.join(publicRoot, "archive.json");
const contentTarget = path.join(publicRoot, "content");
const assetsTarget = path.join(publicRoot, "assets");
const stagingRoot = path.join(repoRoot, "tmp", `amc-inline-import-${process.pid}`);
const contentStage = path.join(stagingRoot, "content");
const assetsStage = path.join(stagingRoot, "assets");

const SOURCE_ORIGIN = "https://live.poshenloh.com";
const SOURCE_LABEL = "LIVE by Po-Shen Loh";
const PAGE_CONCURRENCY = 4;
const ASSET_CONCURRENCY = 6;
const FETCH_ATTEMPTS = 5;
const FETCH_TIMEOUT_MS = 45_000;

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function assertInside(parent, child) {
  const relative = path.relative(path.resolve(parent), path.resolve(child));
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`Unsafe generated path: ${child}`);
  }
}

function examSlug(contest) {
  if (contest === "AMC 8") return "amc8";
  if (contest === "AMC 10") return "amc10";
  throw new Error(`Unsupported contest: ${contest}`);
}

function paperSlug(paper) {
  return String(paper).trim().toLowerCase().replace(/[^a-z0-9-]+/g, "-");
}

function paperFileName(contest, paper) {
  return `${examSlug(contest)}-${paperSlug(paper)}.json`;
}

function annualSolutionsUrl(problem) {
  const source = new URL(problem.sourceUrl);
  const match = source.pathname.match(/^\/past-contests\/(amc8|amc10)\/([^/]+)\/problem\/\d+\/?$/i);
  if (!match) throw new Error(`Unexpected problem URL: ${problem.sourceUrl}`);
  return `${SOURCE_ORIGIN}/past-contests/${match[1].toLowerCase()}/${match[2]}/solutions`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchWithRetry(url, { binary = false } = {}) {
  let finalError;
  for (let attempt = 1; attempt <= FETCH_ATTEMPTS; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
    try {
      const response = await fetch(url, {
        headers: {
          Accept: binary ? "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8" : "text/html,application/xhtml+xml",
          "User-Agent": "ThrivingScholars-AMC-Archive/1.0 (+https://www.thrivingscholars.com)",
        },
        redirect: "follow",
        signal: controller.signal,
      });
      if (!response.ok) {
        const retryable = response.status === 408 || response.status === 425 || response.status === 429 || response.status >= 500;
        if (!retryable) throw new Error(`${response.status} ${response.statusText}`);
        throw new Error(`Retryable ${response.status} ${response.statusText}`);
      }
      return binary
        ? { bytes: Buffer.from(await response.arrayBuffer()), contentType: response.headers.get("content-type") || "" }
        : await response.text();
    } catch (error) {
      finalError = error;
      if (attempt === FETCH_ATTEMPTS) break;
      await sleep(Math.min(12_000, 600 * (2 ** (attempt - 1)) + Math.floor(Math.random() * 300)));
    } finally {
      clearTimeout(timer);
    }
  }
  throw new Error(`Failed to fetch ${url} after ${FETCH_ATTEMPTS} attempts: ${finalError?.message || finalError}`);
}

async function mapPool(items, concurrency, worker) {
  const results = new Array(items.length);
  let nextIndex = 0;
  async function runner() {
    while (true) {
      const current = nextIndex;
      nextIndex += 1;
      if (current >= items.length) return;
      results[current] = await worker(items[current], current);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, runner));
  return results;
}

function extractNextData(html, url) {
  const match = html.match(/<script\b[^>]*\bid=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/i);
  if (!match) throw new Error(`Missing __NEXT_DATA__ in ${url}`);
  let json;
  try {
    json = JSON.parse(match[1]);
  } catch (error) {
    throw new Error(`Invalid __NEXT_DATA__ in ${url}: ${error.message}`);
  }
  const questions = json?.props?.pageProps?.baseQuestions;
  if (!Array.isArray(questions)) throw new Error(`Missing props.pageProps.baseQuestions in ${url}`);
  return questions;
}

function normaliseRichText(value, label) {
  const text = Array.isArray(value) ? value.filter(Boolean).join("\n\n") : String(value ?? "");
  const trimmed = text.trim();
  if (!trimmed) throw new Error(`Missing ${label}`);
  if (/<\s*(script|iframe|object|embed|link|meta|form|input|button|textarea|select|video|audio|canvas)\b/i.test(trimmed)) {
    throw new Error(`Unsafe HTML element in ${label}`);
  }
  if (/\son[a-z]+\s*=|javascript\s*:/i.test(trimmed)) {
    throw new Error(`Unsafe HTML attribute in ${label}`);
  }
  // LIVE mixes a small, useful HTML subset with plain mathematical comparison
  // signs (for example, `a_1<a_2`). Escape only less-than signs that are not
  // the start of one of the display tags we intentionally preserve. Without
  // this, assigning the imported text to innerHTML can swallow inequalities as
  // malformed custom elements.
  return trimmed.replace(
    /<(?!\/?(?:a|b|strong|em|i|u|br|p|div|span|ul|ol|li|table|thead|tbody|tr|td|th|sup|sub|img)(?:\s|\/?>))/gi,
    "&lt;",
  );
}

function normaliseHints(value, id) {
  if (value == null) return [];
  const source = Array.isArray(value) ? value : [value];
  return source
    .map((hint) => String(hint ?? "").trim())
    .filter(Boolean)
    .map((hint, index) => normaliseRichText(hint, `${id} hint ${index + 1}`));
}

function normaliseConcepts(value) {
  if (Array.isArray(value)) return value.map(String).map((item) => item.trim()).filter(Boolean);
  return String(value ?? "")
    .split(/\s*;\s*/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function normaliseSourceQuestion(source, archiveProblem) {
  if (!source || typeof source !== "object") throw new Error(`Missing source question for ${archiveProblem.id}`);
  const answer = String(source.answer ?? "").trim().toUpperCase();
  if (!/^[A-E]$/.test(answer)) throw new Error(`Invalid answer for ${archiveProblem.id}: ${answer || "<blank>"}`);
  const options = ["a", "b", "c", "d", "e"].map((key) => ({
    label: key.toUpperCase(),
    content: normaliseRichText(source[key], `${archiveProblem.id} option ${key.toUpperCase()}`),
  }));
  const solveTimeSeconds = Number(source.solveTimeSeconds);
  const sourceDifficulty = Number(source.seedElo);
  return {
    id: archiveProblem.id,
    number: archiveProblem.number,
    question: normaliseRichText(source.question, `${archiveProblem.id} question`),
    options,
    answer,
    hints: normaliseHints(source.hints, archiveProblem.id),
    solution: normaliseRichText(source.solutions, `${archiveProblem.id} solution`),
    sourceConcepts: normaliseConcepts(source.concepts),
    sourceDifficulty: Number.isFinite(sourceDifficulty) ? sourceDifficulty : null,
    solveTimeSeconds: Number.isFinite(solveTimeSeconds) ? solveTimeSeconds : null,
    sourceUrl: archiveProblem.sourceUrl,
  };
}

function imageSources(value) {
  const found = [];
  const regex = /<img\b[^>]*\bsrc\s*=\s*(["'])(.*?)\1[^>]*>/gi;
  let match;
  while ((match = regex.exec(value)) !== null) found.push(match[2].trim());
  return found;
}

function allRichText(problem) {
  return [problem.question, ...problem.options.map((option) => option.content), ...problem.hints, problem.solution];
}

function resolveSourceAssetUrl(source) {
  const decoded = String(source).replaceAll("&amp;", "&").trim();
  let url;
  if (/^https?:\/\//i.test(decoded)) {
    url = new URL(decoded);
  } else if (decoded.startsWith("//")) {
    url = new URL(`https:${decoded}`);
  } else if (decoded.startsWith("/images/past-contests/")) {
    url = new URL(decoded, SOURCE_ORIGIN);
  } else if (/^\/(amc8|amc10)\//i.test(decoded)) {
    url = new URL(`/images/past-contests${decoded}`, SOURCE_ORIGIN);
  } else {
    throw new Error(`Unsupported figure URL: ${source}`);
  }
  if (url.protocol !== "https:" || url.hostname !== "live.poshenloh.com") {
    throw new Error(`Figure is not hosted by LIVE: ${source}`);
  }
  if (!url.pathname.startsWith("/images/past-contests/")) {
    throw new Error(`Figure is outside the LIVE past-contest archive: ${source}`);
  }
  url.hash = "";
  return url.toString();
}

function assetSpec(source, shard, referencedBy) {
  const sourceUrl = resolveSourceAssetUrl(source);
  const sourcePath = new URL(sourceUrl).pathname;
  let baseName;
  try {
    baseName = decodeURIComponent(path.posix.basename(sourcePath));
  } catch {
    baseName = path.posix.basename(sourcePath);
  }
  const ext = path.extname(baseName).toLowerCase();
  if (![".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"].includes(ext)) {
    throw new Error(`Unsupported figure extension in ${sourceUrl}`);
  }
  const safeStem = path.basename(baseName, ext).replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-+|-+$/g, "") || "figure";
  const fileName = `${safeStem}-${sha256(sourceUrl).slice(0, 10)}${ext}`;
  const relativeFile = path.posix.join(examSlug(shard.contest), paperSlug(shard.paper), fileName);
  return {
    key: `${examSlug(shard.contest)}|${paperSlug(shard.paper)}|${source}`,
    source,
    sourceUrl,
    relativeFile,
    publicUrl: `/amc-past-paper-practice/assets/${relativeFile}`,
    referencedBy: new Set(referencedBy),
  };
}

function validateRaster(bytes, ext, sourceUrl) {
  const signatures = {
    ".png": () => bytes.length >= 8 && bytes.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])),
    ".jpg": () => bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff,
    ".jpeg": () => bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff,
    ".gif": () => bytes.length >= 6 && ["GIF87a", "GIF89a"].includes(bytes.subarray(0, 6).toString("ascii")),
    ".webp": () => bytes.length >= 12 && bytes.subarray(0, 4).toString("ascii") === "RIFF" && bytes.subarray(8, 12).toString("ascii") === "WEBP",
  };
  if (!signatures[ext]?.()) throw new Error(`Invalid ${ext} figure from ${sourceUrl}`);
}

function validateSvg(bytes, sourceUrl) {
  const text = bytes.toString("utf8").replace(/^\uFEFF/, "");
  if (!/<svg\b/i.test(text)) throw new Error(`Invalid SVG from ${sourceUrl}`);
  if (/<\s*(script|foreignObject|iframe|object|embed)\b/i.test(text)) throw new Error(`Unsafe SVG element in ${sourceUrl}`);
  if (/<!ENTITY\b|\son[a-z]+\s*=|javascript\s*:/i.test(text)) throw new Error(`Unsafe SVG content in ${sourceUrl}`);
  if (/(?:href|xlink:href)\s*=\s*["']\s*(?:https?:|\/\/|data:)/i.test(text)) throw new Error(`External SVG resource in ${sourceUrl}`);
  if (/url\(\s*["']?\s*(?:https?:|\/\/|data:)/i.test(text)) throw new Error(`External SVG URL in ${sourceUrl}`);
  return Buffer.from(text, "utf8");
}

function validateAsset(bytes, relativeFile, sourceUrl) {
  if (!bytes.length) throw new Error(`Empty figure from ${sourceUrl}`);
  const ext = path.extname(relativeFile).toLowerCase();
  if (ext === ".svg") return validateSvg(bytes, sourceUrl);
  validateRaster(bytes, ext, sourceUrl);
  return bytes;
}

function rewriteImageSources(value, shard, assetMap) {
  return value.replace(/(<img\b[^>]*\bsrc\s*=\s*)(["'])(.*?)\2/gi, (full, prefix, quote, source) => {
    const key = `${examSlug(shard.contest)}|${paperSlug(shard.paper)}|${source.trim()}`;
    const asset = assetMap.get(key);
    if (!asset) throw new Error(`No downloaded figure for ${source} in ${shard.contest} ${shard.paper}`);
    return `${prefix}${quote}${asset.publicUrl}${quote}`;
  });
}

function rewriteProblem(problem, shard, assetMap) {
  return {
    ...problem,
    question: rewriteImageSources(problem.question, shard, assetMap),
    options: problem.options.map((option) => ({ ...option, content: rewriteImageSources(option.content, shard, assetMap) })),
    hints: problem.hints.map((hint) => rewriteImageSources(hint, shard, assetMap)),
    solution: rewriteImageSources(problem.solution, shard, assetMap),
  };
}

async function writeJson(filePath, value) {
  const text = `${JSON.stringify(value, null, 2)}\n`;
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, text, "utf8");
  return { text, bytes: Buffer.byteLength(text), sha256: sha256(text) };
}

async function main() {
  assertInside(repoRoot, stagingRoot);
  assertInside(publicRoot, contentTarget);
  assertInside(publicRoot, assetsTarget);
  await rm(stagingRoot, { recursive: true, force: true });
  await mkdir(contentStage, { recursive: true });
  await mkdir(assetsStage, { recursive: true });

  const archive = JSON.parse(await readFile(archivePath, "utf8"));
  const problems = archive?.problems;
  if (!Array.isArray(problems) || problems.length !== 2325) {
    throw new Error(`Expected 2,325 archive problems, found ${Array.isArray(problems) ? problems.length : "none"}`);
  }

  const grouped = new Map();
  for (const problem of problems) {
    const key = `${problem.contest}|${problem.paper}`;
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(problem);
  }
  const groups = [...grouped.values()]
    .map((items) => items.sort((a, b) => a.number - b.number))
    .sort((a, b) => a[0].contest.localeCompare(b[0].contest, undefined, { numeric: true }) || String(a[0].paper).localeCompare(String(b[0].paper), undefined, { numeric: true }));
  if (groups.length !== 93) throw new Error(`Expected 93 papers, found ${groups.length}`);
  for (const items of groups) {
    if (items.length !== 25 || items.some((item, index) => item.number !== index + 1)) {
      throw new Error(`Paper ${items[0].contest} ${items[0].paper} is not a complete ordered 25-question set`);
    }
  }

  process.stdout.write(`Fetching ${groups.length} annual LIVE solution pages...\n`);
  let fetchedPages = 0;
  const shards = await mapPool(groups, PAGE_CONCURRENCY, async (items) => {
    const sourceUrl = annualSolutionsUrl(items[0]);
    const html = await fetchWithRetry(sourceUrl);
    const sourceQuestions = extractNextData(html, sourceUrl);
    if (sourceQuestions.length !== 25) throw new Error(`Expected 25 questions in ${sourceUrl}, found ${sourceQuestions.length}`);
    const shard = {
      schemaVersion: 1,
      contest: items[0].contest,
      paper: items[0].paper,
      sourceUrl,
      problems: items.map((problem, index) => normaliseSourceQuestion(sourceQuestions[index], problem)),
    };
    fetchedPages += 1;
    if (fetchedPages % 10 === 0 || fetchedPages === groups.length) process.stdout.write(`  fetched ${fetchedPages}/${groups.length}\n`);
    return shard;
  });

  const assetMap = new Map();
  for (const shard of shards) {
    for (const problem of shard.problems) {
      for (const richText of allRichText(problem)) {
        for (const source of imageSources(richText)) {
          const spec = assetSpec(source, shard, [problem.id]);
          const existing = assetMap.get(spec.key);
          if (existing) existing.referencedBy.add(problem.id);
          else assetMap.set(spec.key, spec);
        }
      }
    }
  }

  const assets = [...assetMap.values()].sort((a, b) => a.relativeFile.localeCompare(b.relativeFile, undefined, { numeric: true }));
  process.stdout.write(`Downloading ${assets.length} unique figures...\n`);
  let downloadedAssets = 0;
  await mapPool(assets, ASSET_CONCURRENCY, async (asset) => {
    const response = await fetchWithRetry(asset.sourceUrl, { binary: true });
    const bytes = validateAsset(response.bytes, asset.relativeFile, asset.sourceUrl);
    const destination = path.join(assetsStage, ...asset.relativeFile.split("/"));
    assertInside(assetsStage, destination);
    await mkdir(path.dirname(destination), { recursive: true });
    await writeFile(destination, bytes);
    asset.bytes = bytes.length;
    asset.sha256 = sha256(bytes);
    asset.contentType = response.contentType.split(";", 1)[0].trim().toLowerCase() || null;
    downloadedAssets += 1;
    if (downloadedAssets % 25 === 0 || downloadedAssets === assets.length) process.stdout.write(`  downloaded ${downloadedAssets}/${assets.length}\n`);
  });

  const shardManifest = [];
  let totalContentBytes = 0;
  for (const shard of shards) {
    const rewritten = {
      ...shard,
      problems: shard.problems.map((problem) => rewriteProblem(problem, shard, assetMap)),
    };
    const file = paperFileName(shard.contest, shard.paper);
    const output = await writeJson(path.join(contentStage, file), rewritten);
    totalContentBytes += output.bytes;
    const prefix = `${examSlug(shard.contest)}|${paperSlug(shard.paper)}|`;
    const paperAssets = assets.filter((asset) => asset.key.startsWith(prefix));
    shardManifest.push({
      contest: shard.contest,
      paper: shard.paper,
      file,
      sourceUrl: shard.sourceUrl,
      problemCount: rewritten.problems.length,
      assetCount: paperAssets.length,
      bytes: output.bytes,
      sha256: output.sha256,
    });
  }

  const manifest = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    source: {
      name: SOURCE_LABEL,
      origin: SOURCE_ORIGIN,
      retrieval: "Annual solutions pages; props.pageProps.baseQuestions in __NEXT_DATA__",
    },
    totalPapers: shards.length,
    totalProblems: shards.reduce((sum, shard) => sum + shard.problems.length, 0),
    totalAssets: assets.length,
    totalContentBytes,
    papers: shardManifest,
    assets: assets.map((asset) => ({
      file: asset.relativeFile,
      publicUrl: asset.publicUrl,
      sourceUrl: asset.sourceUrl,
      bytes: asset.bytes,
      sha256: asset.sha256,
      contentType: asset.contentType,
      referencedBy: [...asset.referencedBy].sort(),
    })),
  };
  await writeJson(path.join(contentStage, "manifest.json"), manifest);

  await rm(contentTarget, { recursive: true, force: true });
  await rm(assetsTarget, { recursive: true, force: true });
  await rename(contentStage, contentTarget);
  await rename(assetsStage, assetsTarget);
  await rm(stagingRoot, { recursive: true, force: true });

  const totalAssetBytes = assets.reduce((sum, asset) => sum + asset.bytes, 0);
  process.stdout.write(`Generated ${shards.length} paper shards with ${manifest.totalProblems} questions and ${assets.length} local figures.\n`);
  process.stdout.write(`JSON: ${(totalContentBytes / 1024 / 1024).toFixed(2)} MiB; figures: ${(totalAssetBytes / 1024 / 1024).toFixed(2)} MiB.\n`);
}

main().catch(async (error) => {
  console.error(error?.stack || error);
  try {
    await rm(stagingRoot, { recursive: true, force: true });
  } catch {
    // Preserve the original error.
  }
  process.exitCode = 1;
});
