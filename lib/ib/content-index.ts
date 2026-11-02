import "server-only";
import index from "@/content/ib/content-index.json";
import type { IbCourseLevel, IbSummary } from "./catalog";

const summaries = index.summaries as Record<IbCourseLevel, IbSummary>;
const questionCollections: Record<string, string> = index.questionCollections;
export function getIbSummary(course: IbCourseLevel = "hl"): IbSummary { return summaries[course]; }
export function collectionForQuestion(id: string) {
  return Object.hasOwn(questionCollections, id) ? questionCollections[id] : undefined;
}
