import type { IbQuestion } from "@/lib/ib/question";
import MathContent from "./MathContent";
import styles from "../questions.module.css";
type Rubric = NonNullable<IbQuestion["markScheme"][number]["rubric"]>;
function BandTable({ title, maximum, bands }: { title:string; maximum:number; bands:NonNullable<Rubric["bands"]> }) {
  return <table className={styles.rubricTable}><caption>{title} · {maximum} marks</caption><thead><tr><th scope="col">Marks</th><th scope="col">Response guidance</th></tr></thead><tbody>{bands.map(band => <tr key={band.min}><th scope="row">{band.min === band.max ? band.min : `${band.min}–${band.max}`}</th><td><MathContent>{band.descriptor}</MathContent></td></tr>)}</tbody></table>;
}
export default function MarkRubric({ rubric }: {rubric:Rubric}) {
  return <div className={styles.rubric}><p>Use the descriptors to select the best-fitting level, then choose the mark within that level. The indicative answer illustrates possible reasoning; other well-supported responses can earn credit.</p>{rubric.bands ? <BandTable title="Best-fit mark bands" maximum={rubric.maxMarks} bands={rubric.bands} /> : rubric.criteria?.map(criterion => <BandTable key={criterion.id} title={`${criterion.id}: ${criterion.title}`} maximum={criterion.maxMarks} bands={criterion.bands} />)}</div>;
}
