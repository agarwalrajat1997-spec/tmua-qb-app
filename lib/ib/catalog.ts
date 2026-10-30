export type IbSubject = "math-aa-hl" | "physics-hl";
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
};

export function ibSubject(value: unknown): IbSubject {
  return value === "physics-hl" ? "physics-hl" : "math-aa-hl";
}
export function ibView(value: unknown): IbView {
  return value === "mocks" ? "mocks" : "questions";
}
export function ibHref(subject: IbSubject, view: IbView = "questions") {
  return `/ib?subject=${subject}&view=${view}`;
}
export type IbSummary = Record<IbSubject, { questions: number; mocks: number; topics: Record<string, number>; collections: import("./question").IbCollectionSummary[] }>;
