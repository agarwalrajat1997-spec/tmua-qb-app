import type { IbSubject } from "@/lib/ib/catalog";
import styles from "../questions.module.css";

export default function ExamInstructions({ subject }: { subject: IbSubject }) {
  return <p className={styles.examInstructions}>{subject === "physics-hl"
    ? <>A calculator may be used for every question. Unless stated otherwise, use <i>g</i> = 9.81 m s<sup>−2</sup>. Show your reasoning and calculations for structured responses, include appropriate units, and report numerical answers to a precision consistent with the data.</>
    : subject === "biology"
      ? <>A calculator may be used for every question. Use precise biological terms, show calculations with appropriate units, and support data-based conclusions with values from the evidence. Constructed data are identified in the question. Diagrams are schematic unless stated otherwise.</>
    : subject === "chemistry"
      ? <>A calculator may be used for every question. Show your reasoning and calculations for structured responses. Include appropriate units, use balanced chemical equations, and report numerical answers to a precision consistent with the data. Any constants needed are given in the question.</>
    : subject === "math-ai-sl"
      ? <>A calculator may be used for every question. Show your method and interpret calculator results in context. Unless stated otherwise, give non-exact numerical answers to three significant figures, include appropriate units, and use degrees for angles.</>
      : <>Unless stated otherwise, give exact answers or non-exact numerical answers to three significant figures. Show your working and follow the calculator label on each question. Angles are in radians unless degrees are indicated.</>}</p>;
}
