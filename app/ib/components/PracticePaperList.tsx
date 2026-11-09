import Link from "next/link";
import { businessPapers, topicPapers, practiceFiles } from "@/lib/ib/practice-catalog";
import styles from "../maths-mocks/maths-mocks.module.css";

export default function PracticePaperList({subject, course}: {subject:string; course:string}) {
  const isBusiness = subject === "business-management";
  const papers = isBusiness ? businessPapers(course) : topicPapers(subject);
  if (!papers.length) return null;
  return <section className={styles.catalog} aria-label={isBusiness ? "Business Management mock tests" : "Timed topic tests"}>
    <div className={styles.intro}><h2>{isBusiness ? "Business Management · Sets A and B" : "Timed topic tests"}</h2>
      <p>{isBusiness ? "Read the Paper 1 pre-release statement before exam day. Open each unseen case when you start its paper. Write on paper or type your answers and use the mark scheme after submission." : "Practise a focused group of skills under timed conditions, then check your work against the mark scheme."}</p>
      {isBusiness && <p><a href="/ib-practice-2027/business-a-pre-release.pdf">Set A pre-release (PDF)</a>{" · "}<a href="/ib-practice-2027/business-b-pre-release.pdf">Set B pre-release (PDF)</a></p>}
    </div><div className={styles.cards}>{papers.map(p => <article key={p.id} className={styles.card}>
      <h3>{p.title}</h3><p>{p.minutes} minutes · {p.marks} marks · {p.calculator ? "Calculator permitted" : "No calculator"}</p>
      <Link className={styles.paperLink} href={`/ib/practice/${p.id}?course=${course}`}>Open timed paper ↗</Link>
      <a href={practiceFiles(p.id).questions}>Question booklet (PDF)</a>
    </article>)}</div></section>;
}
