import { HUMANITIES_COURSES, humanitiesSyllabusSubtopics } from "./humanities-catalog.ts";
export type IbMathSubject = "math-aa-sl" | "math-ai-sl" | "math-aa-hl" | "math-ai-hl";
export type IbSubject = IbMathSubject | "physics-hl" | "chemistry" | "biology" | "economics" | "business-management";
export type IbCourseLevel = "sl" | "hl";
export type IbView = "questions" | "mocks";
export type IbTopic = { id: string; code: string; title: string; description: string; subtopics: string[] };
export type IbCourse = { id: IbSubject; label: string; title: string; subtitle: string; symbol: string; topics: IbTopic[] };

// Maths: current course (final assessment November 2028).
// Physics: first assessment 2025. Keep IDs stable when content is imported.
export const IB_COURSES: Record<IbSubject, IbCourse> = {
  ...HUMANITIES_COURSES,
  "math-ai-hl": {
    id: "math-ai-hl", label: "Maths AI HL", title: "Mathematics", subtitle: "Applications & Interpretation · Higher Level", symbol: "ƒ",
    topics: [
      { id: "number-algebra", code: "01", title: "Number & algebra", description: "Finance, complex numbers, matrices and eigenvalues.", subtopics: ["Sequences and financial models", "Logarithms and series", "Complex numbers", "Matrices and systems", "Eigenvalues and diagonalisation"] },
      { id: "functions", code: "02", title: "Functions", description: "Model, transform and interpret relationships.", subtopics: ["Composite and inverse functions", "Graph transformations", "Exponential and logistic models", "Sinusoidal and piecewise models", "Linearisation and model evaluation"] },
      { id: "geometry-trigonometry", code: "03", title: "Geometry & trigonometry", description: "Vectors, transformations, networks and route algorithms.", subtopics: ["Trigonometry and radians", "Matrix transformations", "Vectors and motion", "Graph theory", "Network algorithms"] },
      { id: "statistics-probability", code: "04", title: "Statistics & probability", description: "Distributions, statistical inference and Markov chains.", subtopics: ["Regression and random variables", "Confidence intervals", "Poisson and normal models", "Hypothesis testing", "Markov chains"] },
      { id: "calculus", code: "05", title: "Calculus", description: "Calculus, differential equations and dynamic models.", subtopics: ["Differentiation and optimisation", "Integration and volume", "Kinematics", "Differential equations", "Coupled systems and phase portraits"] },
    ],
  },
  "math-aa-sl": {
    id: "math-aa-sl", label: "Maths AA SL", title: "Mathematics", subtitle: "Analysis & Approaches · Standard Level", symbol: "ƒ",
    topics: [
      { id: "number-algebra", code: "01", title: "Number & algebra", description: "Sequences, powers, logarithms and binomial expansion.", subtopics: ["Sequences and series", "Exponents and logarithms", "Financial mathematics", "Binomial theorem", "Mathematical proof"] },
      { id: "functions", code: "02", title: "Functions", description: "Graphs, inverses, transformations and equations.", subtopics: ["Function notation and inverses", "Graph transformations", "Quadratic functions", "Rational functions", "Exponential and logarithmic functions"] },
      { id: "geometry-trigonometry", code: "03", title: "Geometry & trigonometry", description: "Triangles, circular measure and trigonometric models.", subtopics: ["Geometry and measurement", "Trigonometric ratios", "Radians and circular measure", "Trigonometric identities and equations", "Sinusoidal models"] },
      { id: "statistics-probability", code: "04", title: "Statistics & probability", description: "Data, regression, probability and distributions.", subtopics: ["Descriptive statistics", "Correlation and regression", "Probability and conditional probability", "Discrete random variables", "Binomial and normal distributions"] },
      { id: "calculus", code: "05", title: "Calculus", description: "Differentiation, integration, motion and optimisation.", subtopics: ["Differentiation", "Tangents and normals", "Optimisation", "Integration and area", "Kinematics"] },
    ],
  },
  "math-ai-sl": {
    id: "math-ai-sl", label: "Maths AI SL", title: "Mathematics", subtitle: "Applications & Interpretation · Standard Level", symbol: "ƒ",
    topics: [
      { id: "number-algebra", code: "01", title: "Number & algebra", description: "Numerical reasoning, sequences and financial mathematics.", subtopics: ["Accuracy and approximation", "Sequences and series", "Compound interest and depreciation", "Annuities and loans", "Systems of equations"] },
      { id: "functions", code: "02", title: "Functions", description: "Use graphs and functions to model real situations.", subtopics: ["Linear models", "Quadratic models", "Exponential models", "Sinusoidal models", "Model interpretation and limitations"] },
      { id: "geometry-trigonometry", code: "03", title: "Geometry & trigonometry", description: "Measurement, bearings and Voronoi diagrams.", subtopics: ["Geometry and measurement", "Trigonometry and bearings", "Voronoi diagrams", "Perpendicular bisectors", "Modelling with geometry"] },
      { id: "statistics-probability", code: "04", title: "Statistics & probability", description: "Analyse data, uncertainty and statistical evidence.", subtopics: ["Sampling and descriptive statistics", "Correlation and regression", "Probability", "Binomial and normal distributions", "Hypothesis testing"] },
      { id: "calculus", code: "05", title: "Calculus", description: "Rates of change, optimisation and accumulated quantities.", subtopics: ["Gradients and rates of change", "Polynomial differentiation", "Optimisation", "Definite integration", "Trapezoidal rule"] },
    ],
  },
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
    id: "physics-hl", label: "Physics", title: "Physics", subtitle: "Diploma Programme", symbol: "λ",
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
  biology: {
    id: "biology", label: "Biology", title: "Biology", subtitle: "Diploma Programme", symbol: "✿",
    topics: [
      { id: "unity-diversity", code: "A", title: "Unity and diversity", description: "Molecules, cells, organisms and the origins of biological diversity.", subtopics: ["Water", "Nucleic acids", "Origins of cells", "Cell structure", "Viruses", "Diversity of organisms", "Classification and cladistics", "Evolution and speciation", "Conservation of biodiversity"] },
      { id: "form-function", code: "B", title: "Form and function", description: "Structure and function from biological molecules to ecological niches.", subtopics: ["Carbohydrates and lipids", "Proteins", "Membranes and membrane transport", "Organelles and compartmentalization", "Cell specialization", "Gas exchange", "Transport", "Muscle and motility", "Adaptation to environment", "Ecological niches"] },
      { id: "interaction-interdependence", code: "C", title: "Interaction and interdependence", description: "Metabolism, signalling, body systems and ecological interactions.", subtopics: ["Enzymes and metabolism", "Cell respiration", "Photosynthesis", "Chemical signalling", "Neural signalling", "Integration of body systems", "Defence against disease", "Populations and communities", "Transfers of energy and matter"] },
      { id: "continuity-change", code: "D", title: "Continuity and change", description: "Inheritance, reproduction, homeostasis, selection and environmental change.", subtopics: ["DNA replication", "Protein synthesis", "Mutation and gene editing", "Cell and nuclear division", "Gene expression", "Water potential", "Reproduction", "Inheritance", "Homeostasis", "Natural selection", "Stability and change", "Climate change"] },
    ],
  },
};

export function ibSubject(value: unknown): IbSubject {
  return typeof value === "string" && Object.hasOwn(IB_COURSES, value) ? value as IbSubject : "math-aa-hl";
}
export const IB_MATH_SUBJECTS: IbMathSubject[] = ["math-aa-sl", "math-ai-sl", "math-aa-hl", "math-ai-hl"];
export function ibIsMathSubject(subject: IbSubject): subject is IbMathSubject {
  return subject === "math-aa-sl" || subject === "math-ai-sl" || subject === "math-aa-hl" || subject === "math-ai-hl";
}
/** Keep one Maths entry in the subject navigation while retaining the selected course. */
export function ibNavigationSubjects(subject: IbSubject): IbSubject[] {
  return [ibIsMathSubject(subject) ? subject : "math-aa-hl", "physics-hl", "chemistry", "biology", "economics", "business-management"];
}
export function ibSubjectLabel(subject: IbSubject) {
  return ibIsMathSubject(subject) ? "Maths" : subject === "business-management" ? "Business" : IB_COURSES[subject].label;
}
export function ibMathCourseHref(subject: IbMathSubject, topicId?: string) {
  if (!topicId) return ibHref(subject);
  const collection = subject === "math-aa-hl" ? topicId === "calculus" ? "calculus-1" : topicId : `${subject === "math-aa-sl" ? "aa-sl" : subject === "math-ai-hl" ? "ai-hl" : "ai-sl"}-${topicId}`;
  return `/ib/question-bank/${collection}`;
}
/** Identify the subject of an authenticated deep link without importing question content into the client. */
export function ibSubjectForPath(pathname: string): IbSubject {
  if (/^\/ib\/(?:question-bank\/aa-sl-|(?:questions|mark-scheme)\/ib-aasl-)/.test(pathname)) return "math-aa-sl";
  if (/^\/ib\/(?:question-bank\/ai-sl-|(?:questions|mark-scheme)\/ib-aisl-)/.test(pathname)) return "math-ai-sl";
  if (/^\/ib\/(?:question-bank\/ai-hl-|(?:questions|mark-scheme)\/ib-aihl-)/.test(pathname)) return "math-ai-hl";
  if (/^\/ib\/(?:question-bank\/economics-|(?:questions|mark-scheme)\/ib-econ-)/.test(pathname)) return "economics";
  if (/^\/ib\/(?:question-bank\/business-|(?:questions|mark-scheme)\/ib-bm-)/.test(pathname)) return "business-management";
  if (/^\/ib\/(?:question-bank\/biology-|(?:questions|mark-scheme)\/ib-bio-)/.test(pathname)) return "biology";
  if (/^\/ib\/(?:question-bank\/chemistry-|(?:questions|mark-scheme)\/ib-chem-)/.test(pathname)) return "chemistry";
  if (/^\/ib\/(?:question-bank\/physics-|(?:questions|mark-scheme)\/ib-phy-)/.test(pathname)) return "physics-hl";
  return "math-aa-hl";
}
export function ibCourseLevel(value: unknown): IbCourseLevel {
  return value === "sl" ? "sl" : "hl";
}
export function ibHasCourseChoice(subject: IbSubject) {
  return subject === "chemistry" || subject === "biology" || subject === "physics-hl" || subject === "economics" || subject === "business-management";
}
export function ibCoreLevel(subject: IbSubject) { return subject === "physics-hl" ? "core" : "sl"; }
export function ibIsHumanitiesSubject(subject: IbSubject): subject is "economics" | "business-management" { return subject === "economics" || subject === "business-management"; }
export function ibCourseLabel(subject: IbSubject, course: IbCourseLevel = "hl") {
  return ibHasCourseChoice(subject) ? `${IB_COURSES[subject].label} ${course.toUpperCase()}` : IB_COURSES[subject].label;
}
export function ibQualification(subject: IbSubject, course: IbCourseLevel = "hl") {
  return subject === "math-aa-sl" || subject === "math-ai-sl" || ibHasCourseChoice(subject) && course === "sl" ? "Standard Level" : "Higher Level";
}
/** Keep established Physics HL links stable while supporting explicit SL views. */
export function ibCourseHref(pathname: string, subject: IbSubject, course: IbCourseLevel = "hl") {
  if (!ibHasCourseChoice(subject)) return pathname;
  const [path, query = ""] = pathname.split("?");
  const params = new URLSearchParams(query);
  if (subject === "physics-hl" && course === "hl") params.delete("course");
  else params.set("course", course);
  return params.size ? `${path}?${params}` : path;
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
  return ibIsHumanitiesSubject(subject) ? humanitiesSyllabusSubtopics(subject, topicId, course) : subject === "biology" ? biologySyllabusSubtopics(topicId, course) : subject === "chemistry" ? chemistrySyllabusSubtopics(topicId, course) : subject === "physics-hl" ? physicsSyllabusSubtopics(topicId, course) : [];
}
export type IbSyllabusSubtopic = { code: string; title: string; additionalHlOnly: boolean };
const PHYSICS_AHL_ONLY = new Set(["A.4", "A.5", "B.4", "D.4", "E.2"]);
/** The numbered Physics subtopics follow the course first assessed in 2025. */
export function physicsSyllabusSubtopics(topicId?: string, course: IbCourseLevel = "hl"): IbSyllabusSubtopic[] {
  return IB_COURSES["physics-hl"].topics.filter(topic => !topicId || topic.id === topicId)
    .flatMap(topic => topic.subtopics.map((title, index) => {
      const code = `${topic.code}.${index + 1}`;
      return { code, title, additionalHlOnly: PHYSICS_AHL_ONLY.has(code) };
    })).filter(topic => course === "hl" || !topic.additionalHlOnly);
}

const BIOLOGY_AHL_ONLY = new Set(["A2.1", "A2.3", "A3.2", "B3.3", "C2.1", "D2.2"]);
const BIOLOGY_SUBTOPICS: Record<string, string[]> = {
  "unity-diversity": [
    "A1.1",
    "A1.2",
    "A2.1",
    "A2.2",
    "A2.3",
    "A3.1",
    "A3.2",
    "A4.1",
    "A4.2"
  ],
  "form-function": [
    "B1.1",
    "B1.2",
    "B2.1",
    "B2.2",
    "B2.3",
    "B3.1",
    "B3.2",
    "B3.3",
    "B4.1",
    "B4.2"
  ],
  "interaction-interdependence": [
    "C1.1",
    "C1.2",
    "C1.3",
    "C2.1",
    "C2.2",
    "C3.1",
    "C3.2",
    "C4.1",
    "C4.2"
  ],
  "continuity-change": [
    "D1.1",
    "D1.2",
    "D1.3",
    "D2.1",
    "D2.2",
    "D2.3",
    "D3.1",
    "D3.2",
    "D3.3",
    "D4.1",
    "D4.2",
    "D4.3"
  ]
};
/** Biology first assessment 2025: codes combine theme and level of organisation. */
export function biologySyllabusSubtopics(topicId?: string, course: IbCourseLevel = "hl"): IbSyllabusSubtopic[] {
  return IB_COURSES.biology.topics.filter(topic => !topicId || topic.id === topicId)
    .flatMap(topic => topic.subtopics.map((title, index) => {
      const code = BIOLOGY_SUBTOPICS[topic.id][index];
      return { code, title, additionalHlOnly: BIOLOGY_AHL_ONLY.has(code) };
    })).filter(topic => course === "hl" || !topic.additionalHlOnly);
}

export type IbSummary = Record<IbSubject, { questions: number; mocks: number; topics: Record<string, number>; collections: import("./question").IbCollectionSummary[] }>;
