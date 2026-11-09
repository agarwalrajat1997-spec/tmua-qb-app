"use server";
import { requireIbUser } from "@/lib/ib/auth";
import { loadPracticePaper } from "@/lib/ib/practice-papers";
import { activeParts } from "@/lib/ib/practice-catalog";
import { supabaseServer } from "@/utils/supabase/server";

async function context(id:string, attemptId:string) {
  if(!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(attemptId)) throw new Error("Invalid attempt.");
  const user=await requireIbUser("/ib/practice/"+encodeURIComponent(id));
  const paper=await loadPracticePaper(id);
  if(!paper) throw new Error("Unknown paper.");
  const db=await supabaseServer();
  return {user,paper,db};
}
export async function submitPractice(id:string, attemptId:string, choice:number|null, answers:Record<string,string>, elapsed:number) {
  const {user,paper,db}=await context(id,attemptId);
  const options=paper.questions.flatMap((q,i)=>q.optional?[i]:[]);
  if(options.length ? choice===null || !options.includes(choice) : choice!==null) throw new Error("Choose one Section B option.");
  if(!Number.isInteger(elapsed)||elapsed<0||elapsed>paper.meta.minutes*60) throw new Error("Invalid elapsed time.");
  const clean:Record<string,string>={};
  for(const p of activeParts(paper,choice)){
    const value=answers?.[p.key]??"";
    if(typeof value!=="string" || value.length>12000) throw new Error("A response is too long.");
    clean[p.key]=value;
  }
  const {error}=await db.from("ib_practice_paper_attempts").insert({id:attemptId,user_id:user.id,paper_id:id,choice,answers:clean,elapsed_seconds:elapsed});
  if(error && error.code!=="23505") throw new Error("Could not save the attempt. Please retry.");
  if(error){
    const existing=await db.from("ib_practice_paper_attempts").select("id").eq("id",attemptId).eq("user_id",user.id).eq("paper_id",id).maybeSingle();
    if(existing.error || !existing.data) throw new Error("Could not confirm the saved attempt.");
  }
}
export async function markPractice(id:string,attemptId:string,marks:Record<string,number>){
  const {user,paper,db}=await context(id,attemptId);
  const base=()=>db.from("ib_practice_paper_attempts");
  const row=await base().select("choice,self_marks").eq("id",attemptId).eq("user_id",user.id).eq("paper_id",id).single();
  if(row.error || !row.data) throw new Error("Attempt unavailable.");
  if(row.data.self_marks) return;
  const clean:Record<string,number>={};
  for(const p of activeParts(paper,row.data.choice)){
    const n=marks?.[p.key];
    if(!Number.isInteger(n)||n<0||n>p.max) throw new Error("Enter a whole-number mark for each part.");
    clean[p.key]=n;
  }
  const updated=await base().update({self_marks:clean}).eq("id",attemptId).eq("user_id",user.id).eq("paper_id",id).is("self_marks",null);
  if(updated.error) throw new Error("Could not save marks. Please retry.");
}
