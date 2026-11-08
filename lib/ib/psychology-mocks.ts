import "server-only";
import {z} from "zod";
import {safeDiagram} from "./question";
import {getPsychologyPaperMeta, paperSpec, type MockPaper, type PsychologyMockPaper, type PsychologyPaperMeta, type PsychologyMockPrompt, type PsychologyQuestion, type PsychologySolution} from "./psychology-mock-model";

const plain = z.string().min(1).max(22000);
const number = z.number().int().positive();
const papers = z.enum(["1","2","3"]);
const svg=z.string().refine(safeDiagram);
const part=z.object({label:z.literal("response"),marks:number.max(15),prompt:plain});
const question=z.object({id:plain,section:papers,division:z.enum(["A","B","C","R"]),number,title:plain,optional:z.boolean(),marks:number,stem:z.string().max(22000),parts:z.array(part).length(1),subtopic:plain,syllabusCode:plain,stimulusSvg:svg.optional(),stimulusCaption:plain.optional(),markScheme:z.array(z.object({part:z.literal("response"),steps:z.array(z.object({code:plain,text:plain})).min(2)})).length(1)});
const resource=z.object({number,title:plain,text:plain,svg:svg.optional(),caption:plain.optional()});
const schema=z.object({id:plain,mockId:plain,course:z.enum(["hl","sl"]),set:z.enum(["A","B"]),paper:papers,title:plain,minutes:number,marks:number,questions:z.array(question),resources:z.array(resource)});
const maxima={"1":[4,4,6,6,15,15],"2":[4,4,6,6,15],"3":[3,6,6,15]};
const sections={"1":"AABBCC","2":"AAAAB","3":"RRRR"};
export function validatePsychologyMockPaper(input:unknown,meta:PsychologyPaperMeta):PsychologyMockPaper {
 const p=schema.parse(input),spec=paperSpec(p.paper);
 for(const k of ["id","mockId","course","set","paper","title","minutes","marks"] as const)if(p[k]!==meta[k])throw new Error("Inconsistent paper metadata: "+k);
 if(p.minutes!==spec.minutes || p.marks!==spec.marks || (p.paper==="3" && p.course!=="hl") || p.questions.length!==maxima[p.paper].length || p.questions.length!==meta.questionCount)throw new Error("Invalid Psychology paper specification.");
 p.questions.forEach((q,i)=>{
  const id=["psy",p.course,p.set.toLowerCase(),p.paper,String(i+1).padStart(2,"0")].join("-");
  if(q.id!==id || q.section!==p.paper || q.number!==i+1 || q.division!==sections[p.paper][i] || q.optional!==(q.division==="C") || q.marks!==maxima[p.paper][i] || q.parts[0].marks!==q.marks || !q.markScheme[0].steps.some(x=>x.code==="Markband"))throw new Error("Invalid Psychology question: "+id);
 });
 if(p.resources.length!==(p.paper==="3"?4:0) || p.resources.some((s,i)=>s.number!==i+2) || (p.paper==="3" && !p.questions[0].stimulusSvg))throw new Error("Invalid research sources.");
 return p;
}
const loaders = {
    "psychology-sl-set-a-paper-1": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-sl-set-a-paper-1.json"),
    "psychology-sl-set-a-paper-2": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-sl-set-a-paper-2.json"),
    "psychology-sl-set-b-paper-1": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-sl-set-b-paper-1.json"),
    "psychology-sl-set-b-paper-2": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-sl-set-b-paper-2.json"),
    "psychology-hl-set-a-paper-1": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-hl-set-a-paper-1.json"),
    "psychology-hl-set-a-paper-2": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-hl-set-a-paper-2.json"),
    "psychology-hl-set-a-paper-3": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-hl-set-a-paper-3.json"),
    "psychology-hl-set-b-paper-1": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-hl-set-b-paper-1.json"),
    "psychology-hl-set-b-paper-2": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-hl-set-b-paper-2.json"),
    "psychology-hl-set-b-paper-3": ()=>import("@/content/ib/psychology-mocks-2027/papers/psychology-hl-set-b-paper-3.json"),
};
export async function getPsychologyMockPaper(id:string, paper:MockPaper) {
    const meta=getPsychologyPaperMeta(id,paper);
    if(!meta)return undefined;
    const loader=loaders[meta.id as keyof typeof loaders];
    return loader ? validatePsychologyMockPaper((await loader()).default,meta) : undefined;
}
function imageUrl(svg:string){return "data:image/svg+xml;base64,"+Buffer.from(svg).toString("base64")}
function prompt(q:PsychologyQuestion){
 const {id,section,division,number,title,optional,marks,stem,parts}=q;
 return {id,section,division,number,title,optional,marks,stem,parts,...(q.stimulusSvg?{stimulusUrl:imageUrl(q.stimulusSvg),stimulusCaption:q.stimulusCaption}:{})};
}
export function psychologyMockPrompt(p:PsychologyMockPaper,meta:PsychologyPaperMeta):PsychologyMockPrompt {
 return {...meta,questions:p.questions.map(prompt),resources:p.resources.map(({svg,...s})=>({...s,...(svg?{figureUrl:imageUrl(svg)}:{})}))};
}
export function psychologyMockSolutions(p:PsychologyMockPaper):PsychologySolution[]{return p.questions.map(q=>({...prompt(q),markScheme:q.markScheme}));}
