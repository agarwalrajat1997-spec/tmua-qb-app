import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { getPhysicsMock, getMockItems } from "@/lib/ib/physics-mocks";
import { questionPrompt } from "@/lib/ib/question";
import QuestionBody from "@/app/ib/components/QuestionBody";
import PhysicsMockRunner from "../../PhysicsMockRunner";
export const dynamic = "force-dynamic";
export const metadata:Metadata={title:"IB Physics Mock | Thriving Scholars",robots:{index:false,follow:false}};
export default async function MockPage({params,searchParams}:{params:Promise<{id:string;paper:string}>;searchParams:Promise<{attempt?:string}>}) {
  const [{id,paper},query]=await Promise.all([params,searchParams]);
  const mock=getPhysicsMock(id);
  if (!mock || (paper!=="1" && paper!=="2")) notFound();
  const destination=`/ib/mocks/${id}/${paper}${query.attempt?`?attempt=${encodeURIComponent(query.attempt)}`:""}`;
  const user=await requireIbUser(destination);
  const items=getMockItems(id,paper);
  return <PhysicsMockRunner key={`${id}-${paper}-${query.attempt??"new"}`} mock={mock} paper={paper} email={user.email} accountId={user.id} initialAttempt={query.attempt}
    items={items.map(({question:q,section,number})=>({id:q.id,section,number,marks:q.marks,parts:q.parts,type:q.questionType}))}
    bodies={items.map(({question:q,number})=><QuestionBody key={q.id} question={{...questionPrompt(q),number}}/>)} />;
}
