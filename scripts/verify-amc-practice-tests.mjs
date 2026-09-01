import { access, readFile, stat } from "node:fs/promises";

const dashboardPath = "app/dashboard/AMCDashboardClient.tsx";
const proxyPath = "proxy.ts";
const emailReportPath = "public/amc-practice-tests/email-report.js";
const tests = [
  {
    title: "Pre-AMC 8 Mock Test",
    slug: "pre-amc-8-mock-test",
    htmlTitle: "Pre-AMC 8 Mock Test",
    solution: "98f2c5_d71abefa5d324789867cf4eee34262ab.pdf",
    timer: "75:00",
  },
  {
    title: "AMC 10 Diagnostic Test",
    slug: "amc-10-diagnostic-test",
    htmlTitle: "AMC 10 Diagnostic Test",
    solution: "98f2c5_baae373bc18b47daafe42e24e61476ae.pdf",
    timer: "75:00",
  },
  {
    title: "AMC 10 Topical Test 1",
    slug: "amc-10-mock-test-1",
    htmlTitle: "AMC 10 MOCK TEST 1",
    solution: "98f2c5_0918321e79a145038286a73fbfb3129f.pdf",
    timer: "75:00",
  },
  ...[
    [2, "98f2c5_0235cce2a36c49fba54fb5af93fbae57.pdf"],
    [3, "98f2c5_69d6293577104a948660692af847e340.pdf"],
    [4, "98f2c5_73e59d53606548e688638b81d8edad96.pdf"],
    [5, "98f2c5_c7f69247d2e84c2eb26af76e75ac8d75.pdf"],
    [6, "98f2c5_dc0d5feedb0b4832bd490d524fd4a0d4.pdf"],
    [7, "98f2c5_a1ea26a7a38a4cf3b8e672285744dde5.pdf"],
    [8, "98f2c5_56a85d6e34454f879240fbd5fe72d919.pdf"],
  ].map(([number, solution]) => ({
    title: `AMC 10 Topical Test ${number}`,
    slug: `amc-10-topical-test-${number}`,
    htmlTitle: `AMC 10 Topical Test ${number}`,
    solution,
    timer: "75:00",
    questionImages: true,
  })),
  {
    title: "AMC 8 Full Mock Test 1",
    slug: "amc-8-full-mock-test-1",
    htmlTitle: "AMC 8 Full Mock Test 1",
    solution: "98f2c5_be5e05b4b67d490fa58a618bd43dce7f.pdf",
    timer: "40:00",
    questionImages: true,
  },
  {
    title: "AMC 8 Full Mock Test 2",
    slug: "amc-8-full-mock-test-2",
    htmlTitle: "AMC 8 Full Mock Test 2",
    solution: "98f2c5_3ea7e91a0f3141d380c7d37c053488ab.pdf",
    timer: "40:00",
    questionImages: true,
  },
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const [dashboard, proxy, emailReport] = await Promise.all([
  readFile(dashboardPath, "utf8"),
  readFile(proxyPath, "utf8"),
  readFile(emailReportPath, "utf8"),
]);

assert(
  proxy.includes('{ prefix: "/amc-practice-tests", product: "amc-question-bank" }'),
  "AMC practice-test routes must use the existing AMC entitlement.",
);
assert(
  proxy.includes('"/amc-practice-tests/:path*"'),
  "AMC practice-test routes must be included in the proxy matcher.",
);

for (const test of tests) {
  const href = `/amc-practice-tests/tests/${test.slug}/index.html`;
  const filePath = `public/amc-practice-tests/tests/${test.slug}/index.html`;
  const [html, file] = await Promise.all([readFile(filePath, "utf8"), stat(filePath)]);
  assert(file.size > 10_000, `${test.title} is unexpectedly small.`);
  assert(dashboard.includes(test.title), `${test.title} is missing from the AMC catalogue.`);
  assert(dashboard.includes(href), `${test.title} has no AMC catalogue link.`);
  assert(
    html.toLowerCase().includes(test.htmlTitle.toLowerCase()),
    `${test.title} title is missing.`,
  );
  assert(html.includes(test.solution), `${test.title} solution booklet is missing.`);
  assert(html.includes(test.timer), `${test.title} timer is missing.`);
  assert(
    html.includes('/amc-practice-tests/email-report.js'),
    `${test.title} does not load the shared score-report service.`,
  );
  assert(html.includes("studentEmail"), `${test.title} has no student email field.`);
  assert(
    html.includes("TS_AMC_EMAIL_REPORT"),
    `${test.title} does not send the shared score report.`,
  );
  assert(
    !html.toLowerCase().includes("restored digital practice test"),
    `${test.title} contains migration wording.`,
  );

  for (const [scriptIndex, source] of [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(
    (match) => match[1],
  ).entries()) {
    try {
      new Function(source);
    } catch (error) {
      throw new Error(`${test.title} inline script ${scriptIndex + 1} does not parse: ${error.message}`);
    }
  }

  if (test.questionImages) {
    assert(
      (html.match(/"[A-E]"/g) ?? []).length >= 25,
      `${test.title} answer key is incomplete.`,
    );
    await Promise.all(
      Array.from({ length: 25 }, (_, index) =>
        access(
          `public/amc-practice-tests/tests/${test.slug}/questions/q${String(index + 1).padStart(2, "0")}.png`,
        ),
      ),
    );
  }
}

assert(
  emailReport.includes('ownerEmail: "outreach@thrivingscholars.com"'),
  "Thriving Scholars must receive a copy of every score report.",
);
assert(
  emailReport.includes("Promise.allSettled"),
  "Student and staff report deliveries must be tracked independently.",
);
const deliveries = [];
const reportWindow = {
  emailjs: {
    init() {},
    send(serviceId, templateId, payload) {
      deliveries.push({ serviceId, templateId, payload });
      return Promise.resolve({ status: 200 });
    },
  },
};
const scoreReporter = new Function(
  "window",
  `${emailReport}\nreturn window.TS_AMC_EMAIL_REPORT;`,
)(reportWindow);
await scoreReporter.send({
  name: "Test Student",
  studentEmail: "student@example.com",
  score: "20 / 25",
  incorrect: "2, 7, 14, 19, 24",
  paper1: "Question analysis",
  solutionLink: "https://example.com/solutions.pdf",
  testTitle: "AMC Verification Test",
});
assert(deliveries.length === 2, "Score report must be sent to the student and Thriving Scholars.");
assert(
  deliveries.some(({ payload }) => payload.to_email === "student@example.com"),
  "Student score-report delivery is missing.",
);
assert(
  deliveries.some(({ payload }) => payload.to_email === "outreach@thrivingscholars.com"),
  "Thriving Scholars score-report copy is missing.",
);
await access("public/amc-practice-tests/email-report.css");

for (const heading of [
  "Diagnostic Tests",
  "Pre-AMC 8 & AMC 10",
  "AMC 8 Full-Length Practice",
  "Full Mock Tests",
  "AMC 10 Topical Practice Tests",
  "Number Theory",
  "Algebra",
  "Geometry",
  "Combinatorics & Logic",
]) {
  assert(dashboard.includes(heading), `Catalogue heading is missing: ${heading}`);
}

const diagnosticPosition = dashboard.indexOf('heading: "Diagnostic Tests"');
const amc8Position = dashboard.indexOf('heading: "AMC 8 Full-Length Practice"');
const amc10Position = dashboard.indexOf('heading: "AMC 10 Topical Practice Tests"');
assert(
  diagnosticPosition < amc8Position && amc8Position < amc10Position,
  "Catalogue order must be Diagnostic Tests, AMC 8, then AMC 10.",
);

assert(
  dashboard.includes('<a className={styles.go} href={test.href}>'),
  "Start test controls must be real links to the standalone test pages.",
);

for (const internalPhrase of ["restored", "original Wix", "preserved exactly"]) {
  assert(
    !dashboard.toLowerCase().includes(internalPhrase.toLowerCase()),
    `Student-facing catalogue contains internal wording: ${internalPhrase}`,
  );
}

console.log(
  `Verified ${tests.length} AMC practice tests, email reports, solution links, timers, answer keys and protected catalogue routes.`,
);

