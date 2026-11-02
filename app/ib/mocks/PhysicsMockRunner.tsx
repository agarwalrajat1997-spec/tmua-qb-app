"use client";
import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import Link from "next/link";
import Script from "next/script";
import IbBrand from "../IbBrand";
import MathContent from "../components/MathContent";
import DiagramImage from "../components/DiagramImage";
import { answerKey, paperSpec, reportPayload, type PhysicsMock, type MockPaper, type MockAnswers, type SelfMarks, type MockReview } from "@/lib/ib/physics-mock-model";
import styles from "./mocks.module.css";

type Item = {id:string;section:string;number:number;marks:number;parts:{label:string;prompt:string;marks:number}[];type:string};
type Draft = {version:1;attemptId:string;startedAt:number;deadline:number;answers:MockAnswers;flags:Record<string,boolean>;index:number;stage:"instructions"|"running"|"pending"|"review";elapsed:number;marks:SelfMarks;name:string};
type Props = {mock:PhysicsMock;paper:MockPaper;email:string;accountId:string;initialAttempt?:string;items:Item[];bodies:ReactNode[]};
function newDraft():Draft { return {version:1,attemptId:"",startedAt:0,deadline:0,answers:{},flags:{},index:0,stage:"instructions",elapsed:0,marks:{},name:""}; }
function clock(seconds:number) { return `${Math.floor(seconds/3600)?`${Math.floor(seconds/3600)}:`:""}${String(Math.floor(seconds/60)%60).padStart(2,"0")}:${String(seconds%60).padStart(2,"0")}`; }
type EmailJs = { init:(key:string)=>void; send:(service:string,template:string,payload:Record<string,string>)=>Promise<unknown> };

export default function PhysicsMockRunner({mock,paper,email,accountId,initialAttempt,items,bodies}:Props) {
  const spec=paperSpec(mock.course,paper);
  const storageKey=`ts:ib-physics:v1:${accountId}:${mock.id}:${paper}`;
  const [draft,setDraft]=useState<Draft>(newDraft);
  const [ready,setReady]=useState(false);
  const [remaining,setRemaining]=useState(spec.minutes*60);
  const [review,setReview]=useState<MockReview|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const [saveWarning,setSaveWarning]=useState("");
  const [mailState,setMailState]=useState<"idle"|"sending"|"sent"|"failed">("idle");
  const [mailError,setMailError]=useState("");
  const [confirmSubmit,setConfirmSubmit]=useState(false);
  const draftRef=useRef(draft); draftRef.current=draft;
  const mailBusy=useRef(false);
  const api=`/api/ib/mocks/${mock.id}`;
  const home=`/ib?subject=physics-hl&view=mocks&course=${mock.course}`;

  const loadAttempt=useCallback(async(id:string)=>{
    setBusy(true);setError("");
    try {
      const response=await fetch(`${api}?attempt=${encodeURIComponent(id)}`,{cache:"no-store"});
      const result=await response.json();
      if(!response.ok)throw new Error(result.error);
      if(result.paper!==paper)throw new Error("This saved attempt belongs to a different paper.");
      setReview(result.review);
      setDraft(d=>({...d,attemptId:id,stage:"review",answers:result.review.answers,marks:result.review.selfMarks??d.marks}));
      try {if(localStorage.getItem(`ts:ib-mail:${accountId}:${id}`)==="sent")setMailState("sent");}catch{}
    } catch(e){setError(e instanceof Error?e.message:"Could not load the saved attempt.");}finally{setBusy(false);}
  },[api,paper,accountId]);

  useEffect(()=>{
    let saved:Draft|null=null;
    if(!initialAttempt)try{
      const raw=localStorage.getItem(storageKey);
      if(raw){const d=JSON.parse(raw);if(d.version===1 && ["instructions","running","pending","review"].includes(d.stage) && Number.isFinite(d.deadline) && d.answers && d.flags && d.marks && Number.isInteger(d.index) && d.index>=0 && d.index<items.length)saved=d;}
    }catch{setSaveWarning("Device saving is unavailable. Keep this tab open until your attempt is submitted.");}
    if(saved)setDraft(saved);
    setReady(true);
    const attempt=initialAttempt || (saved?.stage==="review"?saved.attemptId:undefined);
    if(attempt)void loadAttempt(attempt);
  },[initialAttempt,storageKey,items.length,loadAttempt]);

  useEffect(()=>{
    if(!ready||initialAttempt)return;
    try{localStorage.setItem(storageKey,JSON.stringify(draft));}catch{setSaveWarning("This browser could not save your draft. Keep this tab open until submission.");}
  },[draft,ready,storageKey,initialAttempt]);

  useEffect(()=>{
    if(!ready||draft.stage!=="running")return;
    const tick=()=>{
      const d=draftRef.current;
      const seconds=Math.max(0,Math.ceil((d.deadline-Date.now())/1000));
      setRemaining(seconds);
      if(seconds===0)setDraft(current=>current.stage==="running"?{...current,stage:"pending",elapsed:spec.minutes*60}:current);
    };
    tick();const timer=setInterval(tick,500);
    const warn=(event:BeforeUnloadEvent)=>{event.preventDefault();event.returnValue="";};
    window.addEventListener("beforeunload",warn);
    return()=>{clearInterval(timer);window.removeEventListener("beforeunload",warn);};
  },[ready,draft.stage,spec.minutes]);

  const submit=useCallback(async()=>{
    const d=draftRef.current;
    if(d.stage!=="pending")return;
    setBusy(true);setError("");
    try{
      const response=await fetch(api,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"submit",attemptId:d.attemptId,paper,answers:d.answers,elapsed:d.elapsed})});
      const result=await response.json();if(!response.ok)throw new Error(result.error);
      setReview(result.review);setDraft(current=>({...current,stage:"review"}));
      window.history.replaceState(null,"",`?attempt=${d.attemptId}`);
    }catch(e){setError(e instanceof Error?e.message:"Submission failed. Your answers are kept on this device; retry when connected.");}finally{setBusy(false);}
  },[api,paper]);
  useEffect(()=>{if(ready&&draft.stage==="pending")void submit();},[ready,draft.stage,submit]);

  function start(){const now=Date.now();setDraft(d=>({...d,attemptId:crypto.randomUUID(),startedAt:now,deadline:now+spec.minutes*60000,stage:"running"}));window.scrollTo({top:0});}
  function finish(){setConfirmSubmit(false);setDraft(d=>({...d,stage:"pending",elapsed:Math.min(spec.minutes*60,Math.max(0,Math.round((Date.now()-d.startedAt)/1000)))}));}
  function write(key:string,value:string){setDraft(d=>d.stage==="running"&&Date.now()<d.deadline?{...d,answers:{...d.answers,[key]:value}}:d);}
  function jump(index:number){setDraft(d=>({...d,index}));setConfirmSubmit(false);window.scrollTo({top:0,behavior:"smooth"});}
  function startAgain(){
    try{localStorage.removeItem(storageKey);}catch{}
    window.location.assign(`/ib/mocks/${mock.id}/${paper}`);
  }

  async function sendEmail(result:MockReview){
    if(mailBusy.current||result.score.total===null)return;
    mailBusy.current=true;setMailState("sending");setMailError("");
    try{
      const mail=(window as Window & {emailjs?:EmailJs}).emailjs;
      if(!mail)throw new Error("The email service has not loaded. Check your connection and retry.");
      mail.init("9jjn3yBHl6S88hITy");
      await mail.send("service_5l4w8x2","template_j1jrs4o",reportPayload(mock,paper,result,email,draft.name,window.location.origin));
      setMailState("sent");try{localStorage.setItem(`ts:ib-mail:${accountId}:${result.id}`,"sent");}catch{}
    }catch(e){setMailState("failed");setMailError(e instanceof Error?e.message:"The email service did not confirm sending. Your saved report is still available; retry below.");}
    finally{mailBusy.current=false;}
  }
  async function saveMarks(){
    if(!review)return;
    setBusy(true);setError("");
    try{
      const response=await fetch(api,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"mark",attemptId:review.id,paper,selfMarks:draft.marks})});
      const result=await response.json();if(!response.ok)throw new Error(result.error);
      setReview(result.review);await sendEmail(result.review);
    }catch(e){setError(e instanceof Error?e.message:"Marks could not be saved. Please retry.");}finally{setBusy(false);}
  }
  const item=items[draft.index];
  const answered=(q:Item)=>q.type==="multiple-choice"?!!draft.answers[q.id]:q.parts.every(p=>!!draft.answers[answerKey(q.id,p.label)]?.trim());
  const unanswered=items.filter(q=>!answered(q)).length;
  const unmarked=items.flatMap(q=>q.parts.map(p=>answerKey(q.id,p.label))).filter(key=>draft.marks[key]===undefined).length;

  return <div className={styles.app}>
    <Script src="https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js" strategy="afterInteractive"/>
    <header className={styles.header}><Link href={home} aria-label="IB mock tests"><IbBrand/></Link><span className={styles.account}>{email}</span><Link href={home}>All mocks ↗</Link></header>
    <main className={styles.main}>
      <div className={styles.heading}><span className={styles.tag}>IB PHYSICS · {mock.course.toUpperCase()} · ORIGINAL PRACTICE</span><h1>{mock.title}<span>{spec.label}</span></h1><p>{spec.minutes} minutes · {spec.marks} marks · Calculator permitted</p></div>
      {saveWarning?<p className={styles.notice} role="status">{saveWarning}</p>:null}
      {error?<div className={styles.error} role="alert">{error}{(initialAttempt||draft.stage==="review")&&!review?<button onClick={()=>loadAttempt(initialAttempt||draft.attemptId)} disabled={busy}>Retry loading</button>:null}</div>:null}
      {!ready?<p>Loading your saved work…</p>:null}
      {ready&&draft.stage==="instructions"&&!initialAttempt?<section className={styles.instructions}>
        <h2>Before you begin</h2><ul><li>Answer every question. There is no penalty for an incorrect multiple-choice answer.</li><li>{paper==="1"?"Paper 1A and 1B use a single timer. You can move freely between them; there is no break.":"Show your reasoning, units and working for every written response."}</li><li>Have a calculator, a clean copy of the current Physics data booklet, paper and a pen ready. Use g = 9.81 m s⁻² unless stated otherwise.</li><li>You may work on paper. Enter your answer or a brief working summary beside each part, then retain your paper for self-assessment.</li><li>Your timer continues if you leave or refresh. Draft answers are saved on this device. Submitted answers and marks are saved to your account.</li><li>After submission, mark written parts using the worked solutions. Your report will identify self-assessed marks and will be emailed to {email}.</li></ul>
        <label className={styles.field}>Your name (for your report)<input value={draft.name} maxLength={100} onChange={e=>setDraft(d=>({...d,name:e.target.value}))} autoComplete="name"/></label>
        <p className={styles.note}>These questions are compiled from your original Physics question bank. Previous topic practice may affect your result. This is not an official IB paper or grade prediction.</p>
        <button className={styles.primary} onClick={start}>Start timed paper →</button>
      </section>:null}
      {ready&&draft.stage==="running"?<>
        <div className={styles.toolbar}><strong>{item.section==="2"?"Paper 2":`Paper ${item.section}`} · Question {item.number}</strong><span role="timer" aria-label="Time remaining" className={remaining<300?styles.urgent:styles.timer}>{clock(remaining)}</span><button className={styles.secondary} onClick={()=>setDraft(d=>({...d,flags:{...d.flags,[item.id]:!d.flags[item.id]}}))} aria-pressed={!!draft.flags[item.id]}>{draft.flags[item.id]?"⚑ Flagged":"Flag question"}</button><button className={styles.primary} onClick={()=>setConfirmSubmit(true)}>Submit paper</button></div>
        {confirmSubmit?<section className={styles.confirm} role="alertdialog" aria-labelledby="submit-title"><h2 id="submit-title">Submit this paper?</h2><p>{unanswered} question{unanswered===1?"":"s"} without a complete entered response. Keep any working on paper for marking. Submitted responses cannot be changed.</p><button className={styles.primary} onClick={finish}>Submit and review</button><button className={styles.secondary} onClick={()=>setConfirmSubmit(false)}>Keep working</button></section>:null}
        <div className={styles.examGrid}>
          <aside className={styles.navigator} aria-label="Question navigator">{[...new Set(items.map(q=>q.section))].map(section=><div key={section}><h2>Paper {section}</h2><div className={styles.numbers}>{items.map((q,index)=>q.section===section?<button key={q.id} onClick={()=>jump(index)} aria-label={`Paper ${section} question ${q.number}${answered(q)?", answered":""}${draft.flags[q.id]?", flagged":""}`} aria-current={index===draft.index?"step":undefined} className={`${answered(q)?styles.answered:""} ${index===draft.index?styles.current:""}`}>{q.number}{draft.flags[q.id]?" ⚑":""}</button>:null)}</div></div>)}<p>Filled = response entered<br/>⚑ = review later</p></aside>
          <section className={styles.question} aria-label={`Paper ${item.section} question ${item.number}`}>
            {bodies[draft.index]}
            {item.type==="multiple-choice"?<fieldset className={styles.choices}><legend>Your answer</legend>{["A","B","C","D"].map(option=><label key={option}><input type="radio" name={item.id} value={option} checked={draft.answers[item.id]===option} onChange={()=>write(item.id,option)}/>{option}</label>)}<button className={styles.secondary} onClick={()=>write(item.id,"")}>Clear choice</button></fieldset>:<div className={styles.responses}>{item.parts.map(part=><label key={part.label} className={styles.field}>Part ({part.label}) · {part.marks} marks<textarea value={draft.answers[answerKey(item.id,part.label)]??""} onChange={e=>write(answerKey(item.id,part.label),e.target.value)} maxLength={12000} rows={4} placeholder="Enter your response or summarise working completed on paper."/></label>)}</div>}
            <div className={styles.questionFooter}><button className={styles.secondary} disabled={draft.index===0} onClick={()=>jump(draft.index-1)}>← Previous</button><span>{draft.index+1} of {items.length}</span>{draft.index<items.length-1?<button className={styles.primary} onClick={()=>jump(draft.index+1)}>Next →</button>:<button className={styles.primary} onClick={()=>setConfirmSubmit(true)}>Review and submit</button>}</div>
          </section>
        </div>
      </>:null}
      {draft.stage==="pending"?<section className={styles.instructions}><h2>{busy?"Saving your answers…":"Answers locked for submission"}</h2><p>Your answers are retained on this device. Solutions appear after the server confirms that the attempt is saved.</p>{!busy?<button className={styles.primary} onClick={submit}>Retry submission</button>:null}</section>:null}
      {review?<>
        <section className={styles.result}><span className={styles.tag}>{review.selfMarks?"REPORT SAVED":"ATTEMPT SAVED · SELF-ASSESSMENT"}</span><h2>{review.score.total===null?"Mark your written responses":`${review.score.total} / ${review.score.maximum}`}</h2><p>{paper==="1"?`Multiple choice: ${review.score.mcq} / ${mock.paper1A.length}. `:""}{review.selfMarks?`Written: ${review.score.written} (self-assessed). `:"Use the worked solutions below to enter a mark for every written part. "}Time used: {clock(review.elapsed)}.</p><p>Written marks are self-assessed. No official IB grade is calculated; internal assessment is not included.</p>
          {review.selfMarks?<div className={styles.reportActions}><button className={styles.primary} onClick={()=>sendEmail(review)} disabled={mailState==="sending"||mailState==="sent"}>{mailState==="sent"?"Report accepted by email service ✓":mailState==="sending"?"Sending report…":mailState==="failed"?"Retry email report":"Email my report"}</button><button className={styles.secondary} onClick={()=>window.print()}>Print report & solutions</button><p role="status">{mailState==="sent"?`Sent for delivery to ${email}.`:mailError}</p></div>:null}
        </section>
        {review.selfMarks?<section className={styles.breakdown}><h2>Topic breakdown</h2><table><thead><tr><th>Topic</th><th>Marks</th></tr></thead><tbody>{review.score.topics.map(t=><tr key={t.code}><td>{t.code} · {t.title}</td><td>{t.score} / {t.max}</td></tr>)}</tbody></table></section>:null}
        <section className={styles.solutions}><h2>Worked solutions & written self-assessment</h2><p>Award separate method (M), accuracy (A) and reasoning (R) marks up to each part’s maximum. Accept valid equivalent methods. Apply follow-through only where the marking note states it.</p>{review.solutions.map((solution,index)=><details key={solution.id} className={styles.solution} open={items[index].type!=="multiple-choice"}><summary>{solution.label} · {items[index].marks} marks{solution.correctOption?` · Your answer: ${review.answers[solution.id]||"—"} · Correct: ${solution.correctOption}`:""}</summary><div className={styles.solutionBody}>{bodies[index]}{solution.markScheme.map(group=><section key={group.part||"all"}>
          {group.part?<h3>Part ({group.part})</h3>:null}{group.part?<p className={styles.writtenAnswer}><strong>Your response:</strong> {review.answers[answerKey(solution.id,group.part)]||"No typed response. Check your working on paper."}</p>:null}
          <ol className={styles.markSteps}>{group.steps.map((step,n)=><li key={n}><strong>{step.code}</strong><MathContent>{step.text}</MathContent></li>)}</ol>
          {group.part?<label className={styles.markInput}>Your mark for {solution.label} ({group.part})<select disabled={!!review.selfMarks} value={draft.marks[answerKey(solution.id,group.part)]??""} onChange={e=>setDraft(d=>({...d,marks:{...d.marks,[answerKey(solution.id,group.part)]:Number(e.target.value)}}))}><option value="" disabled>Choose a mark</option>{Array.from({length:(solution.parts.find(p=>p.label===group.part)?.marks??0)+1},(_,n)=><option key={n} value={n}>{n}</option>)}</select></label>:null}
        </section>)}{solution.diagram?<figure><DiagramImage src={solution.diagram} caption={`Worked diagram for ${solution.label}`}/>{solution.diagramCaption?<figcaption>{solution.diagramCaption}</figcaption>:null}</figure>:null}</div></details>)}</section>
        {!review.selfMarks?<div className={styles.markFooter}><p>{unmarked} written part{unmarked===1?"":"s"} left to mark. Your report will be emailed to {email}.</p><button className={styles.primary} disabled={busy||unmarked>0} onClick={saveMarks}>{busy?"Saving…":"Save marks and email report"}</button></div>:null}
        <Link className={styles.back} href={home}>← Back to Physics mock series</Link>
        {review.selfMarks?<button className={styles.secondary} onClick={startAgain}>Start a new attempt</button>:null}
      </>:null}
    </main>
  </div>;
}
