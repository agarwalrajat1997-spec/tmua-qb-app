(function () {
  "use strict";

  const EMAIL_CONFIG = {
    publicKey: "9jjn3yBHl6S88hITy",
    serviceId: "service_5l4w8x2",
    templateId: "template_j1jrs4o",
    ownerEmail: "outreach@thrivingscholars.com",
  };

  let initialised = false;

  function text(value) {
    return String(value ?? "").trim();
  }

  function validEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  function initialise() {
    if (!window.emailjs) {
      throw new Error("The score-report service did not load.");
    }

    if (!initialised) {
      window.emailjs.init(EMAIL_CONFIG.publicKey);
      initialised = true;
    }
  }

  async function send(report) {
    const studentEmail = text(report.studentEmail);
    if (!validEmail(studentEmail)) {
      throw new Error("A valid student email is required.");
    }

    initialise();

    const basePayload = {
      name: text(report.name) || "Student",
      session: text(report.session) || "Independent practice",
      score: text(report.score),
      timestamp: text(report.timestamp) || new Date().toLocaleString(),
      incorrect: text(report.incorrect) || "None",
      paper1: text(report.paper1),
      to_email: studentEmail,
      student_email: studentEmail,
      solution_link: text(report.solutionLink),
      test_title: text(report.testTitle) || "AMC Practice Test",
      report_recipient: "Student",
    };

    const studentDelivery = window.emailjs.send(
      EMAIL_CONFIG.serviceId,
      EMAIL_CONFIG.templateId,
      basePayload,
    );

    const ownerDelivery =
      studentEmail.toLowerCase() === EMAIL_CONFIG.ownerEmail.toLowerCase()
        ? Promise.resolve()
        : window.emailjs.send(EMAIL_CONFIG.serviceId, EMAIL_CONFIG.templateId, {
            ...basePayload,
            to_email: EMAIL_CONFIG.ownerEmail,
            paper1: `Student email: ${studentEmail}\n\n${basePayload.paper1}`,
            report_recipient: "Thriving Scholars",
          });

    const [studentResult, ownerResult] = await Promise.allSettled([
      studentDelivery,
      ownerDelivery,
    ]);

    if (ownerResult.status === "rejected") {
      console.error("Thriving Scholars score-report copy failed", ownerResult.reason);
    }

    if (studentResult.status === "rejected") {
      throw studentResult.reason;
    }

    return {
      studentSent: true,
      ownerSent: ownerResult.status === "fulfilled",
    };
  }

  window.TS_AMC_EMAIL_REPORT = Object.freeze({
    ownerEmail: EMAIL_CONFIG.ownerEmail,
    send,
    validEmail,
  });
})();

