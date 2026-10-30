export type IbSubject = "math-aa-hl" | "physics-hl" | "chemistry";
export type IbCourseLevel = "sl" | "hl";
export type IbView = "questions" | "mocks";
export type IbTopic = { id: string; code: string; title: string; description: string; subtopics: string[] };
export type IbCourse = { id: IbSubject; label: string; title: string; subtitle: string; symbol: string; topics: IbTopic[] };

// Maths: current course (final assessment November 2028).
// Physics: first assessment 2025. Keep IDs stable when content is imported.
export const IB_COURSES: Record<IbSubject, IbCourse> = {
  "math-aa-hl": {
    id: "math-aa-hl", label: "Maths AA HL", title: "Mathematics", subtitle: "Analysis & Approaches · Higher Level", symbol: "ƒ",
    topics: [
      { id: "number-algebra", code: "01", title: "Number & algebra", description: "From sequences to complex numbers.", subtopics: ["Sequences and series", "Exponents and logarithms", "Binomial theorem and counting", "Complex numbers", "Proof and mathematical induction"] },
      { id: "functions", code: "02", title: "Functions", description: "Explore relationships, graphs and transformations.", subtopics: ["Function notation and inverses", "Graph transformations", "Quadratic and polynomial functions", "Rational functions", "Exponential and logarithmic functions"] },
      { id: "geometry-trigonometry", code: "03", title: "Geometry & trigonometry", description: "Connect shapes, angles and vectors.", subtopics: ["Geometry and measurement", "Trigonometric functions and equations", "Trigonometric identities", "Vectors, lines and planes"] },
      { id: "statistics-probability", code: "04", title: "Statistics & probability", description: "Make sense of data and uncertainty.", subtopics: ["Descriptive statistics", "Correlation and regression", "Probability and conditional probability", "Discrete random variables", "Binomial and normal distributions", "Continuous random variables"] },
      { id: "calculus", code: "05", title: "Calculus", description: "Understand change, accumulation and modelling.", subtopics: ["Limits and continuity", "Differentiation", "Applications of differentiation", "Integration", "Applications of integration", "Differential equations", "Maclaurin series"] },
    ],
  },
  "physics-hl": {
    id: "physics-hl", label: "Physics HL", title: "Physics", subtitle: "Diploma Programme · Higher Level", symbol: "λ",
    topics: [
      { id: "space-time-motion", code: "A", title: "Space, time & motion", description: "The principles behind how things move.", subtopics: ["Kinematics", "Forces and momentum", "Work, energy and power", "Rigid body mechanics", "Galilean and special relativity"] },
      { id: "particulate-matter", code: "B", title: "The particulate nature of matter", description: "Energy, matter and the world at particle scale.", subtopics: ["Thermal energy transfers", "Greenhouse effect", "Gas laws", "Thermodynamics", "Current and circuits"] },
      { id: "wave-behaviour", code: "C", title: "Wave behaviour", description: "Oscillations, wave models and interactions.", subtopics: ["Simple harmonic motion", "Wave model", "Wave phenomena", "Standing waves and resonance", "Doppler effect"] },
      { id: "fields", code: "D", title: "Fields", description: "Forces and interactions across space.", subtopics: ["Gravitational fields", "Electric and magnetic fields", "Motion in electromagnetic fields", "Induction"] },
      { id: "nuclear-quantum", code: "E", title: "Nuclear & quantum physics", description: "From the atom to the energy of stars.", subtopics: ["Structure of the atom", "Quantum physics", "Radioactive decay", "Fission", "Fusion and stars"] },
    ],
  },
  chemistry: {
    id: "chemistry", label: "Chemistry", title: "Chemistry", subtitle: "Diploma Programme", symbol: "⚗",
    topics: [
      { id: "structure-1", code: "S1", title: "Models of the particulate nature of matter", description: "Particles, atoms, electrons, the mole and ideal gases.", subtopics: ["Introduction to the particulate nature of matter", "The nuclear atom", "Electron configurations", "Counting particles by mass: The mole", "Ideal gases"] },
      { id: "structure-2", code: "S2", title: "Models of bonding and structure", description: "Ionic, covalent and metallic models and their materials.", subtopics: ["The ionic model", "The covalent model", "The metallic model", "From models to materials"] },
      { id: "structure-3", code: "S3", title: "Classification of matter", description: "Patterns in the periodic table and organic compounds.", subtopics: ["The periodic table: Classification of elements", "Functional groups: Classification of organic compounds"] },
      { id: "reactivity-1", code: "R1", title: "What drives chemical reactions?", description: "Enthalpy, energy cycles, fuels, entropy and spontaneity.", subtopics: ["Measuring enthalpy changes", "Energy cycles in reactions", "Energy from fuels", "Entropy and spontaneity"] },
      { id: "reactivity-2", code: "R2", title: "How much, how fast and how far?", description: "Amounts, rates and equilibria in chemical reactions.", subtopics: ["How much? The amount of chemical change", "How fast? The rate of chemical change", "How far? The extent of chemical change"] },
      { id: "reactivity-3", code: "R3", title: "What are the mechanisms of chemical change?", description: "Proton transfer, electron transfer and reaction mechanisms.", subtopics: ["Proton transfer reactions", "Electron transfer reactions", "Electron sharing reactions", "Electron-pair sharing reactions"] },
    ],
  },
};

export function ibSubject(value: unknown): IbSubject {
  return value === "chemistry" ? "chemistry" : value === "physics-hl" ? "physics-hl" : "math-aa-hl";
}
/** Identify the subject of an authenticated deep link without importing question content into the client. */
export function ibSubjectForPath(pathname: string): IbSubject {
  if (/^\/ib\/(?:question-bank\/chemistry-|(?:questions|mark-scheme)\/ib-chem-)/.test(pathname)) return "chemistry";
  if (/^\/ib\/(?:question-bank\/physics-|(?:questions|mark-scheme)\/ib-phy-)/.test(pathname)) return "physics-hl";
  return "math-aa-hl";
}
export function ibCourseLevel(value: unknown): IbCourseLevel {
  return value === "sl" ? "sl" : "hl";
}
export function ibCourseLabel(subject: IbSubject, course: IbCourseLevel = "hl") {
  return subject === "chemistry" ? `Chemistry ${course.toUpperCase()}` : IB_COURSES[subject].label;
}
export function ibQualification(subject: IbSubject, course: IbCourseLevel = "hl") {
  return subject === "chemistry" && course === "sl" ? "Standard Level" : "Higher Level";
}
/** Preserve existing Math/Physics URLs; only Chemistry has a course choice. */
export function ibCourseHref(pathname: string, subject: IbSubject, course: IbCourseLevel = "hl") {
  if (subject !== "chemistry") return pathname;
  const [path, query = ""] = pathname.split("?");
  const params = new URLSearchParams(query);
  params.set("course", course);
  return `${path}?${params}`;
}
export function ibView(value: unknown): IbView {
  return value === "mocks" ? "mocks" : "questions";
}
export function ibHref(subject: IbSubject, view: IbView = "questions", course: IbCourseLevel = "hl") {
  return ibCourseHref(`/ib?subject=${subject}&view=${view}`, subject, course);
}
const CHEMISTRY_AHL_ONLY = new Set(["R1.4"]);
/** S = Structure and R = Reactivity in the Chemistry course first assessed in 2025. */
export function chemistrySyllabusSubtopics(topicId?: string, course: IbCourseLevel = "hl"): IbSyllabusSubtopic[] {
  return IB_COURSES.chemistry.topics.filter(topic => !topicId || topic.id === topicId)
    .flatMap(topic => topic.subtopics.map((title, index) => {
      const code = `${topic.code}.${index + 1}`;
      return { code, title, additionalHlOnly: CHEMISTRY_AHL_ONLY.has(code) };
    })).filter(topic => course === "hl" || !topic.additionalHlOnly);
}
export function ibSyllabusSubtopics(subject: IbSubject, topicId?: string, course: IbCourseLevel = "hl") {
  return subject === "chemistry" ? chemistrySyllabusSubtopics(topicId, course) : subject === "physics-hl" ? physicsSyllabusSubtopics(topicId) : [];
}
export type IbSyllabusSubtopic = { code: string; title: string; additionalHlOnly: boolean };
const PHYSICS_AHL_ONLY = new Set(["A.4", "A.5", "B.4", "D.4", "E.2"]);
/** The numbered Physics subtopics follow the course first assessed in 2025. */
export function physicsSyllabusSubtopics(topicId?: string): IbSyllabusSubtopic[] {
  return IB_COURSES["physics-hl"].topics.filter(topic => !topicId || topic.id === topicId)
    .flatMap(topic => topic.subtopics.map((title, index) => {
      const code = `${topic.code}.${index + 1}`;
      return { code, title, additionalHlOnly: PHYSICS_AHL_ONLY.has(code) };
    }));
}
export type IbSummary = Record<IbSubject, { questions: number; mocks: number; topics: Record<string, number>; collections: import("./question").IbCollectionSummary[] }>;
