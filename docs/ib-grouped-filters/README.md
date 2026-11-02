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

Repeated query parameters survive pagination and sign-in returns. Existing `syllabus` and `subtopic` bookmarks remain exact and can be combined. When submitted again, their selections become explicit specific-topic choices in the category filter. SL/HL switches map selected groups to the eligible categories in the destination course.

## Validation

- `npm run verify:ib-grouped-filters`: checks every course and all 45 collections, unique question membership, syllabus coverage, category counts, reduction ratios, combined filters, legacy bookmarks, pagination, sign-in returns, invalid values and SL boundaries.
- `npm run verify:ib-grouped-filters-browser`: uses the real checkbox component and server question-bank component with a synthetic local account. Exercises repeated GET fields, server results, pagination, reset, mobile width, keyboard selection, Escape/focus and facet clearing. Screenshots are written to `/tmp/ib-filter-screenshots` or `IB_FILTER_SCREENSHOTS`. Requires a Playwright Chromium installation, or `IB_BROWSER_EXECUTABLE` pointing to a compatible Chromium binary.
- Existing IB portal, expansion and Physics mock regressions passed.
- TypeScript, targeted ESLint and the Next.js production build passed.

Browser verification uses isolated authentication fixtures. Production verification checks deployment readiness and unauthenticated redirects; it does not use a real student session or send email.
