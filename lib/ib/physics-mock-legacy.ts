import "server-only";
import a from "@/content/ib/physics-hl/space-time-motion.json";
import b from "@/content/ib/physics-hl/particulate-matter.json";
import c from "@/content/ib/physics-hl/wave-behaviour.json";
import d from "@/content/ib/physics-hl/fields.json";
import e from "@/content/ib/physics-hl/nuclear-quantum.json";
import { ibQuestionSchema } from "./question";
import { PHYSICS_MOCKS, type PhysicsQuestion, type MockPaper, type MockItem } from "./physics-mock-legacy-model";

const questions = new Map([...a,...b,...c,...d,...e].map(raw => {
  const question = ibQuestionSchema.parse(raw) as PhysicsQuestion;
  return [question.id, question];
}));
export function getPhysicsMock(id: string) { return PHYSICS_MOCKS.find(m => m.id === id && m.status === "published"); }
export function getMockItems(id: string, paper: MockPaper): MockItem[] {
  const mock = getPhysicsMock(id);
  if (!mock) return [];
  const sections = paper === "1" ? [["1A",mock.paper1A],["1B",mock.paper1B]] as const : [["2",mock.paper2]] as const;
  return sections.flatMap(([section, ids]) => ids.map((id,index) => {
    const q = questions.get(id);
    if (!q || q.status !== "published" || (mock.course === "sl" && q.level !== "core")) throw new Error("Invalid Physics mock catalogue.");
    return { question: q, section, number: index + 1 };
  }));
}
