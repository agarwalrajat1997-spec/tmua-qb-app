# IB grouped categories and multi-select filters

Related subtopics are now presented as study categories throughout the portal overview and every question bank. Original questions, subtopic labels, syllabus codes, mark schemes and authentication remain intact. The taxonomy is in `content/ib/topic-groups.json`; SL overrides avoid presenting HL-only material as an SL category. Each published question belongs to exactly one category. Newly added topics remain discoverable as standalone categories until curated.

| Course | Previous subtopics | Study categories |
| --- | ---: | ---: |
| Maths AA SL | 100 | 50 |
| Maths AA HL | 174 | 90 |
| Maths AI SL | 100 | 51 |
| Maths AI HL | 125 | 66 |
| Physics SL | 19 | 10 |
| Physics HL | 24 | 12 |
| Chemistry SL | 21 | 10 |
| Chemistry HL | 22 | 10 |
| Biology SL | 34 | 17 |
| Biology HL | 40 | 20 |
| Economics SL | 27 | 14 |
| Economics HL | 31 | 16 |
| Business management SL | 26 | 13 |
| Business management HL | 37 | 19 |

Checkbox filters support multiple study categories, difficulties, response styles or exam papers, question types, content levels and calculator options wherever applicable. Options within a filter are combined with OR; different filters are combined with AND. No checked options means all. Applied choices have individual remove links, and Reset clears the filters while retaining the course.

Repeated query parameters survive pagination and sign-in returns. Existing `syllabus` and `subtopic` bookmarks remain exact and can be combined. When changed again, their selections become explicit specific-topic choices in the category filter. SL/HL switches map selected groups to the eligible categories in the destination course.

## Validation

- `npm run verify:ib-grouped-filters`: checks every course and all 45 collections, unique question membership, syllabus coverage, category counts, reduction ratios, combined filters, legacy bookmarks, pagination, sign-in returns, invalid values and SL boundaries.
- `npm run verify:ib-grouped-filters-browser`: uses the real automatic form, checkbox/search components and server question-bank component with a synthetic local account and asynchronous router adapter. Exercises immediate repeated parameters, delayed/out-of-order responses, no document reloads, search debouncing, page reset, back/forward restoration, server results, pagination, reset, mobile width, keyboard selection, Escape/focus and facet clearing. Screenshots are written to `/tmp/ib-filter-screenshots` or `IB_FILTER_SCREENSHOTS`. Requires a Playwright Chromium installation, or `IB_BROWSER_EXECUTABLE` pointing to a compatible Chromium binary.
- Existing IB portal, expansion and Physics mock regressions passed.
- TypeScript, targeted ESLint and the Next.js production build passed.

Browser verification uses isolated authentication fixtures. Production verification checks deployment readiness and unauthenticated redirects; it does not use a real student session or send email.

## Instant filters and loading performance

Every checkbox selection and facet Clear applies immediately through client navigation; no Apply button is shown. Search waits 300 ms after typing stops, and Enter submits immediately. Changing filters resets pagination and keeps the page position. Menus and inputs remain mounted during requests so multiple selections are possible without losing focus. The URL remains the source for bookmarks and back/forward navigation.

The overview uses generated metadata and sends only the selected subject to the client. Question and mark-scheme routes load and validate only the requested collection, once per server instance; concurrent requests share the same promise and failed loads can retry. The ID index contains no question bodies or answers. All 45 collection imports are separate server chunks. After changing question content or topic categories, run `npm run generate:ib-content-index`; prebuild rejects a stale index.

IB links prefetch on hover, keyboard focus or touch intent, avoiding requests for every link in long category lists. A loading boundary provides immediate navigation feedback. The IB proxy verifies and refreshes signed JWT claims (the project uses ES256) instead of making a duplicate remote user lookup; every protected page retains its authoritative `getUser` check. Other programme entitlement checks are unchanged. Cached objects contain deployment-bundled content only, never student sessions.

Local isolated measurements (TypeScript module harness; not live page or network latency): loading the old all-course content module took about 505 ms; the new module plus first Physics topic took about 70 ms (43 + 27 ms). Warm summary generation fell from about 14.5 ms to a metadata lookup. The Physics overview summary is 5,525 bytes rather than 103,374 bytes for all courses. These measurements demonstrate reduced server work/payload; actual student latency also depends on network and authentication.

`npm run verify:ib-content-loading` checks lazy imports, concurrent reuse, validation/cache retry, all 5,122 ID mappings, question order and SL access boundaries. `npm run verify:ib-content-index` verifies generated metadata against the source. The browser fixture tests the real components and server results with a transport adapter, not a signed-in production session. The production build, TypeScript, targeted ESLint, existing IB/content/mock tests and access/reliability tests also passed.
