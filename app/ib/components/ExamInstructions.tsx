import type { IbSubject } from "@/lib/ib/catalog";
import styles from "../questions.module.css";

export default function ExamInstructions({ subject }: { subject: IbSubject }) {
  return <p className={styles.examInstructions}>{subject === "physics-hl"
    ? <>A calculator may be used for every question. Unless stated otherwise, use <i>g</i> = 9.81 m s<sup>−2</sup>. Show your reasoning and calculations for structured responses, include appropriate units, and report numerical answers to a precision consistent with the data.</>
    : subject === "chemistry"
      ? <>A calculator may be used for every question. Show your reasoning and calculations for structured responses. Include appropriate units, use balanced chemical equations, and report numerical answers to a precision consistent with the data. Any constants needed are given in the question.</>
      : <>Unless stated otherwise, give exact answers or non-exact numerical answers to three significant figures. Show your working. Angles are in radians unless degrees are indicated.</>}</p>;
}
