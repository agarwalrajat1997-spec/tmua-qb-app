export const PRACTICE_TESTS = [
  {
    exam: "10",
    title: "AMC 10 Topical Test 1",
    level: "AMC 10 · Number Theory",
    detail: "Focused number theory practice covering factors, divisibility and sequences.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-mock-test-1/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Topical Test 2",
    level: "AMC 10 · Number Theory",
    detail: "A second focused paper covering number patterns, factors and reasoning.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-2/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Topical Test 3",
    level: "AMC 10 · Algebra",
    detail: "Arithmetic and algebra questions with original notation preserved.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-3/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Topical Test 4",
    level: "AMC 10 · Algebra",
    detail: "A second arithmetic and algebra paper for timed contest practice.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-4/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Topical Test 5",
    level: "AMC 10 · Geometry",
    detail: "Geometry practice covering angles, circles and spatial reasoning.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-5/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Topical Test 6",
    level: "AMC 10 · Geometry",
    detail: "A second geometry paper covering angles, circles and spatial reasoning.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-6/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Topical Test 7",
    level: "AMC 10 · Combinatorics",
    detail: "Timed combinatorics and probability practice with instant scoring.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-7/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Topical Test 8",
    level: "AMC 10 · Logic",
    detail: "Logic and structured reasoning questions with full worked solutions.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-8/index.html",
  },
  {
    exam: "8",
    title: "AMC 8 Full Mock Test 1",
    level: "AMC 8 · All Topics",
    detail: "A 40-minute challenge paper. Some later problems go beyond typical AMC 8 topics.",
    tags: ["25 questions", "40 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-8-full-mock-test-1/index.html",
  },
  {
    exam: "8",
    title: "AMC 8 Full Mock Test 2",
    level: "AMC 8 · All Topics",
    detail: "A second 40-minute challenge paper, including advanced geometry and series in the later questions.",
    tags: ["25 questions", "40 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-8-full-mock-test-2/index.html",
  },
  {
    exam: "8",
    title: "Pre-AMC 8 Mock Test",
    level: "AMC 8 Foundations",
    detail: "A full timed foundation paper for students building toward AMC 8.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/pre-amc-8-mock-test/index.html",
  },
  {
    exam: "10",
    title: "AMC 10 Diagnostic Test",
    level: "AMC 10 · All Topics",
    detail: "Identify strengths, missed topics and the highest-priority areas to review.",
    tags: ["25 questions", "75 minutes", "Topic analysis"],
    href: "/amc-practice-tests/tests/amc-10-diagnostic-test/index.html",
  },
] as const;

export const AMC_RESOURCE_SECTIONS = [
  {
    heading: "AMC 8",
    description: "Quick revision and a deep archive for the AMC 8 syllabus.",
    resources: [
      {
        title: "AMC 8 Comprehensive Cheat Sheet",
        description:
          "An 11-page Thriving Scholars quick reference covering core knowledge, high-yield methods and contest strategy.",
        kind: "Quick reference",
        pages: 11,
        href: "/amc-resources/amc-8-comprehensive-cheat-sheet-thriving-scholars.pdf",
      },
      {
        title: "AMC 8 Compendium",
        description:
          "A 307-page AMC 8 problem compendium spanning 1985–2026 for structured long-form practice.",
        kind: "Problem archive",
        pages: 307,
        href: "/amc-resources/amc-8-compendium.pdf",
      },
    ],
  },
  {
    heading: "AMC 10",
    description: "Formula review and an extensive AMC 10 competition archive.",
    resources: [
      {
        title: "AMC 10 Comprehensive Cheat Sheet",
        description:
          "A 10-page Thriving Scholars reference for formulas, recurring structures and late-question techniques.",
        kind: "Quick reference",
        pages: 10,
        href: "/amc-resources/amc-10-comprehensive-cheat-sheet-thriving-scholars.pdf",
      },
      {
        title: "AMC 10 Compendium",
        description:
          "A comprehensive 757-page AMC 10 problem collection for sustained contest preparation.",
        kind: "Problem archive",
        pages: 757,
        href: "/amc-resources/amc-10-compendium.pdf",
      },
    ],
  },
  {
    heading: "AMC 12",
    description: "Advanced revision and past-problem practice for AMC 12.",
    resources: [
      {
        title: "AMC 12 Comprehensive Cheat Sheet",
        description:
          "A 10-page Thriving Scholars toolkit covering algebra, trigonometry, geometry, number theory and combinatorics.",
        kind: "Quick reference",
        pages: 10,
        href: "/amc-resources/amc-12-comprehensive-cheat-sheet-thriving-scholars.pdf",
      },
      {
        title: "AMC 12 Compendium",
        description:
          "A 471-page AMC 12 problem compendium covering the 2008–2025 competition years.",
        kind: "Problem archive",
        pages: 471,
        href: "/amc-resources/amc-12-compendium.pdf",
      },
    ],
  },
] as const;


export const AMC12_ARCHIVE = [
  { title: "2025 AMC 12B", page: 463, keyPage: 471 },
  { title: "2025 AMC 12A", page: 453, keyPage: 462, note: "Question 25 has no correct listed option. Leave it unscored." },
  { title: "2024 AMC 12B", page: 444, keyPage: 452 },
  { title: "2024 AMC 12A", page: 435, keyPage: 443 },
] as const;
