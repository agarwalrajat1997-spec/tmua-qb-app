# Frozen Physics review guard

The release contains ten timed papers, 219 questions, 218 written parts and 170 unparted multiple-choice marking groups: 388 independently reviewed groups and 640 marks. Three HL sets use a shared 120-minute Paper1A/1B and 150-minute Paper2. Two SL sets use a shared90-minute Paper1A/1B and90-minute,50-mark Paper2.

`node scripts/verify-ib-physics-mock-reviews.mjs` is read-only. It validates current content, scientific evidence, final PDF build/render/visual records, portal checks and actual-role database evidence, then compares every protected file with the frozen manifest. It never regenerates a question, approves a review or refreshes a hash.

The explicit one-time finalizer is `node scripts/finalize-ib-physics-mock-reviews.mjs`. All author checks, separate independent reviews and final visual reviews must already pass. It validates an in-memory candidate before writing the manifest atomically, and verifies the written manifest again. If a manifest already exists, the finalizer only verifies it. A changed release therefore fails instead of silently accepting new hashes.

The guard checks exact question IDs, every part label/mark total, independent substantive reasoning, one uniquely matched correct option text, numerical values against their stated absolute tolerances, source-page bounds, syllabus references and SL exclusions. It rejects short repeating answer-key cycles, severe position bias, duplicate stems, broken Markdown tables, unsafe SVGs and missing evidence. Numerical tolerance bounds account for physical units and scales; they do not substitute for the independently worked reasoning.

Scientific figures are bound by original SVG hashes and the native-image review records. The renderer binds the canonical paper, SVG and raster hashes; the PDF builder independently verifies the actual intermediate bytes and records the digest of that exact portable asset report. The guard binds that digest, each final PDF hash/page count, its question-content hash, bookmarks and completed visual review. It checks that questions precede the solution book.

The manifest protects all ten canonical papers and PDFs, the catalogue, scientific/research/provenance/release ledgers, review scripts, rendering scripts, database verification and migration, and supporting screenshots. Original user-supplied source PDFs remain private and read-only. Their hashes and page provenance are recorded; their pages are not part of the release.

These checks provide reproducible evidence and prevent unnoticed changes after review. They do not establish human IB examiner moderation, official grade boundaries or an empirical difficulty calibration. A new substantive content change requires fresh scientific and visual review and an explicitly managed new freeze; normal builds cannot rebaseline the existing release.
