"use client";
import { useEffect,useRef,useState } from "react";
import MathContent from "@/app/ib/components/MathContent";
import { activeParts,practiceFiles,type PracticeAttempt,type PracticePrompt,type PracticeQuestion } from "@/lib/ib/practice-catalog";
import { submitPractice,markPractice } from "./actions";
import styles from "./practice.module.css";
type Draft={id:string;start:number;choice:number|null;answers:Record<string,string>};

export default function PracticeRunner({paper,account,path,attempt,schemes}:{paper:PracticePrompt;account:string;path:string;attempt:PracticeAttempt|null;schemes?:PracticeQuestion["markScheme"][]}){
  const {meta,questions,resources}=paper, files=practiceFiles(meta.id);
  const [draft,setDraft]=useState<Draft|null>(null),[ready,setReady]=useState(false),[now,setNow]=useState(0);
  const [busy,setBusy]=useState(false),[message,setMessage]=useState(""),[marks,setMarks]=useState<Record<string,number>>(attempt?.self_marks??{});
  const auto=useRef(false), key=`ib-practice:v1:${account}:${meta.id}`;
  useEffect(()=>{
    if(!attempt)try{
      const raw=localStorage.getItem(key);
      if(raw){const d=JSON.parse(raw);if(typeof d.id==="string" && Number.isFinite(d.start) && d.start>0 && d.start<=Date.now()+60000 && d.answers && typeof d.answers==="object" && !Array.isArray(d.answers)) setDraft(d);}
    }catch{setMessage("The saved draft could not be restored.");}
    setNow(Date.now());setReady(true);
  },[key,attempt]);
  useEffect(()=>{
    if(!ready||!draft||attempt)return;
    try{localStorage.setItem(key,JSON.stringify(draft));}catch{setMessage("Browser storage is unavailable. Keep this tab open until submission.");}
  },[key,draft,attempt,ready]);
  useEffect(()=>{
    if(!draft||attempt)return;
    const t=window.setInterval(()=>setNow(Date.now()),1000);return()=>clearInterval(t);
  },[draft?.id,attempt]); // Retain one wall-clock timer while answers change.
  const seconds=draft?Math.max(0,Math.min(meta.minutes*60,Math.ceil((draft.start+meta.minutes*60000-now)/1000))):meta.minutes*60;
  async function finish(){
    if(!draft||busy)return;
    setBusy(true);setMessage("");
    try{
      await submitPractice(meta.id,draft.id,draft.choice,draft.answers,Math.max(0,Math.min(meta.minutes*60,Math.floor((Date.now()-draft.start)/1000))));
      try{localStorage.removeItem(key);}catch{}
      window.location.assign(path+"&attempt="+draft.id);
    }catch{setBusy(false);setMessage("Could not submit. Your answers are still here. Retry submission.");}
  }
  useEffect(()=>{
    if(ready && draft && seconds===0 && !attempt && !auto.current){auto.current=true;void finish();}
  },[ready,draft,seconds,attempt]); // Expiry submits once. A failed submission can be retried.
  const options=questions.map((q,i)=>q.optional?i:-1).filter(i=>i>=0);
  const choice=attempt?attempt.choice:draft?.choice??null;
  const responses=attempt?.answers??draft?.answers??{};
  const selected=activeParts(paper,choice);
  async function saveMarks(){
    if(!attempt)return;
    setBusy(true);
    try{await markPractice(meta.id,attempt.id,marks);window.location.reload();}
    catch{setBusy(false);setMessage("Enter a valid mark for each part and retry.");}
  }
  return <><p>{meta.minutes} minutes · {meta.marks} marks · {meta.calculator?"Calculator permitted":"No calculator"}</p>
    <p><a href={files.questions}>Print question booklet (PDF)</a>{attempt&&<> · <a href={files.solutions}>Worked mark scheme (PDF)</a></>}</p>
    {message&&<p role="alert">{message}</p>}
    {!attempt&&!draft?<section><p>{options.length?"Answer all of Section A and one option from Section B.":"Answer all questions."} Show working on paper or type below. Submit to open the mark scheme.</p><button disabled={!ready} onClick={()=>{const start=Date.now();setNow(start);setDraft({id:crypto.randomUUID(),start,choice:options[0]??null,answers:{}});}}>Start timed paper</button></section>:<>
    {attempt?<p><strong>{attempt.self_marks?`Self-assessed score · ${Object.values(attempt.self_marks).reduce((a,b)=>a+b,0)} / ${meta.marks}`:"Submitted · Ready to mark"}</strong> · {Math.floor(attempt.elapsed_seconds/60)} min {attempt.elapsed_seconds%60} s used</p>:<div className={styles.clock} role="timer">Time remaining <b>{Math.floor(seconds/60)}:{String(seconds%60).padStart(2,"0")}</b></div>}
    {resources.map(r=><section key={r.title}><h2>{r.title}</h2><MathContent>{r.text}</MathContent></section>)}
    {options.length>0&&<fieldset><legend>Section B · Choose one option</legend>{options.map(i=><label key={i}><input type="radio" name="option" checked={choice===i} disabled={!!attempt||busy||seconds===0} onChange={()=>setDraft(d=>d?{...d,choice:i}:d)}/>{questions[i].title}</label>)}</fieldset>}
    {questions.map((q,i)=>q.optional&&choice!==i?null:<section key={i}><h2>{q.title}</h2>{q.stem&&<MathContent>{q.stem}</MathContent>}
      {q.diagramSvg&&<img className={styles.figure} src={"data:image/svg+xml;charset=utf-8,"+encodeURIComponent(q.diagramSvg)} alt={"Diagram for "+q.title}/>}
      {q.parts.map((p,j)=>{const k=`${i+1}:${p.label}`;return <div key={k} className={styles.part}><strong>({p.label}) · {p.marks} marks</strong><MathContent>{p.prompt}</MathContent>
        {attempt?<><p><b>Your response</b></p><p className={styles.response}>{responses[k]||"No typed response. Use your written working."}</p>
        <details open><summary>Worked mark scheme</summary>{schemes?.[i]?.[j]?.steps.map((s,n)=><div key={n}><b>{s.code}</b><MathContent>{s.text}</MathContent></div>)}</details>
        <label>Your mark (0–{p.marks}) <input type="number" min={0} max={p.marks} step={1} disabled={!!attempt.self_marks||busy} value={marks[k]??""} onChange={e=>{const text=e.target.value;setMarks(m=>{const copy={...m};if(text==="")delete copy[k];else copy[k]=Number(text);return copy;});}}/></label></>:<label>Your working<textarea rows={3} maxLength={12000} disabled={busy||seconds===0} value={responses[k]??""} onChange={e=>{const value=e.target.value;setDraft(d=>d?{...d,answers:{...d.answers,[k]:value}}:d);}}/></label>}</div>;})}</section>)}
    {attempt?(!attempt.self_marks&&<button disabled={busy||selected.some(p=>!Number.isInteger(marks[p.key])||marks[p.key]<0||marks[p.key]>p.max)} onClick={saveMarks}>Save self-assessed marks</button>):<button disabled={busy} onClick={finish}>{busy?"Submitting…":"Submit and open mark scheme"}</button>}
    </>}</>;
}
