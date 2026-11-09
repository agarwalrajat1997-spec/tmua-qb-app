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

    const receipt = report.receipt || await window.TS_AMC_ATTEMPT.finish();
    window.TS_AMC_ATTEMPT.mount(receipt);
    const pdf = new URL(receipt.solutionPath, location.origin).href;
    const pointsLine = receipt.points + " / " + receipt.maximum;
    const counts = receipt.correct + " correct · " + receipt.incorrect + " incorrect · " + receipt.blanks + " blank";
    const details = "Saved attempt: " + receipt.id + "\nAMC score: " + pointsLine + " (" + counts + ")\nWorked solutions (PDF): " + pdf + "\n\n" + text(report.paper1);
    initialise();

    const basePayload = {
      name: text(report.name) || "Student",
      session: text(report.session) || "Independent practice",
      score: pointsLine,
      timestamp: text(report.timestamp) || new Date().toLocaleString(),
      incorrect: receipt.answers.flatMap((a,i)=>a===receipt.key[i]?[]:[i+1]).join(", ") || "None",
      paper1: details,
      to_email: studentEmail,
      student_email: studentEmail,
      solution_link: pdf,
      test_title: text(report.testTitle) || "AMC Practice Test",
      report_recipient: "Student",
    };

    await window.emailjs.send(EMAIL_CONFIG.serviceId, EMAIL_CONFIG.templateId, basePayload);
    // The provider rate-limits consecutive sends. A student delivery never depends on the staff copy.
    const isControlledCheck = Boolean(receipt.testMailbox) && studentEmail.toLowerCase() === receipt.testMailbox;
    if (!isControlledCheck && studentEmail.toLowerCase() !== EMAIL_CONFIG.ownerEmail.toLowerCase()) {
      await new Promise(resolve => setTimeout(resolve, 1200));
      try { await window.emailjs.send(EMAIL_CONFIG.serviceId, EMAIL_CONFIG.templateId, {...basePayload, to_email:EMAIL_CONFIG.ownerEmail, paper1:"Student email: "+studentEmail+"\\n\\n"+details, report_recipient:"Thriving Scholars"}); }
      catch (error) { console.error("Thriving Scholars score-report copy failed",error); return {studentSent:true,ownerSent:false}; }
    }
    return {studentSent:true,ownerSent:!isControlledCheck};
  }

  window.TS_AMC_EMAIL_REPORT = Object.freeze({
    ownerEmail: EMAIL_CONFIG.ownerEmail,
    send,
    validEmail,
  });
})();
