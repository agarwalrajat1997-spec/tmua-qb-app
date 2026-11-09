import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { ibHref, type IbSubject } from "@/lib/ib/catalog";
import { loadPracticePaper, practicePrompt } from "@/lib/ib/practice-papers";
import { supabaseServer } from "@/utils/supabase/server";
import type { PracticeAttempt } from "@/lib/ib/practice-catalog";
import PracticeRunner from "./PracticeRunner";
import styles from "./practice.module.css";

export default async function PracticePage({params,searchParams}:{params:Promise<{id:string}>;searchParams:Promise<{course?:string;attempt?:string}>}) {
  const {id}=await params, query=await searchParams;
  const course=query.course==="sl" || (!query.course && /^(aa|business)-sl-/.test(id)) ? "sl":"hl";
  const path=`/ib/practice/${encodeURIComponent(id)}?course=${course}`;
  const user=await requireIbUser(path);
  const paper=await loadPracticePaper(id);
  if(!paper || (paper.meta.course && paper.meta.course!=="both" && paper.meta.course!==course)) notFound();
  const db=await supabaseServer();
  const history=await db.from("ib_practice_paper_attempts").select("id,submitted_at").eq("user_id",user.id).eq("paper_id",id).order("submitted_at",{ascending:false}).limit(15);
  let attempt:PracticeAttempt|null=null;
  if(query.attempt){
    if(!/^[0-9a-f-]{36}$/i.test(query.attempt)) notFound();
    const saved=await db.from("ib_practice_paper_attempts").select("id,submitted_at,answers,choice,self_marks,elapsed_seconds").eq("user_id",user.id).eq("paper_id",id).eq("id",query.attempt).maybeSingle();
    if(saved.error) throw new Error("Could not load this attempt.");
    if(!saved.data) notFound();
    attempt=saved.data as PracticeAttempt;
  }
  return <main className={styles.page}><Link href={ibHref(paper.meta.subject as IbSubject,"mocks",course)}>← Practice tests</Link>
    <h1>{paper.meta.title}</h1><PracticeRunner key={attempt?.id ?? id} paper={practicePrompt(paper)} account={user.id} path={path} attempt={attempt} schemes={attempt?paper.questions.map(q=>q.markScheme):undefined}/>
    <section><h2>Saved attempts</h2>{history.error?<p>Attempt history could not be loaded. Refresh to retry.</p>:history.data?.length?<ul>{history.data.map(row=><li key={row.id}><Link href={path+"&attempt="+row.id}>{new Date(row.submitted_at).toUTCString()} · Review</Link></li>)}</ul>:<p>No submitted attempts yet.</p>}</section></main>;
}
