import "server-only";
import {z} from "zod";
import {safeDiagram} from "./question";
import {getEconomicsPaperMeta, paperSpec, type MockPaper, type EconomicsMockPaper, type EconomicsPaperMeta, type EconomicsMockPrompt, type EconomicsQuestion, type EconomicsSolution} from "./economics-mock-model";

const plain = z.string().min(1).max(22000);
const number = z.number().int().positive();
const papers = z.enum(["1","2","3"]);
const part = z.object({label:plain, marks:number.max(15), prompt:plain});
const question = z.object({
    id:plain, section:papers, number, title:plain, optional:z.boolean(), marks:number,
    stem:plain, parts:z.array(part).min(2), subtopic:plain, syllabusCode:z.string().regex(/^[1-4]\.\d{1,2}$/),
    stimulusSvg:z.string().refine(safeDiagram).optional(),stimulusCaption:plain.optional(),solutionSvg:z.string().refine(safeDiagram), background:z.object({label:plain,url:z.string().url().startsWith("https://")}).optional(),
    markScheme:z.array(z.object({part:plain, steps:z.array(z.object({code:plain,text:plain})).min(1)}))
});
const schema = z.object({id:plain,mockId:plain,course:z.enum(["hl","sl"]),set:z.enum(["A","B"]),paper:papers,title:plain,
    minutes:number,marks:number,calculator:z.boolean(),questions:z.array(question).min(2).max(3)});
const requiredParts = {
    "1":{"a":10,"b":15},
    "2":{"a(i)":2,"a(ii)":2,"b(i)":3,"b(ii)":2,"c":4,"d":4,"e":4,"f":4,"g":15},
    "3":{"a(i)":2,"a(ii)":2,"a(iii)":3,"a(iv)":3,"a(v)":2,"a(vi)":4,"a(vii)":4,"b":10},
};
export function validateEconomicsMockPaper(input:unknown, meta:EconomicsPaperMeta):EconomicsMockPaper {
    const p=schema.parse(input), spec=paperSpec(p.paper);
    for(const k of ["id","mockId","course","set","paper","title","minutes","marks","calculator"] as const)
        if(p[k]!==meta[k])throw new Error("Inconsistent Economics paper metadata: "+k);
    if(p.minutes!==spec.minutes || p.marks!==spec.marks || p.calculator!==spec.calculator || (p.paper==="3" && p.course!=="hl") ||
        p.questions.length!==(p.paper==="1"?3:2) || p.questions.length!==meta.questionCount)throw new Error("Invalid Economics paper specification.");
    p.questions.forEach((q,i)=>{
        const id=["econ",p.course,p.set.toLowerCase(),p.paper,String(i+1).padStart(2,"0")].join("-");
        const allocation=Object.entries(requiredParts[p.paper]);
        if(q.id!==id || q.section!==p.paper || q.number!==i+1 || q.optional!==(p.paper!=="3") ||
            q.parts.length!==allocation.length || q.markScheme.length!==allocation.length ||
            q.marks!==q.parts.reduce((n,a)=>n+a.marks,0))throw new Error("Invalid Economics question: "+id);
        allocation.forEach(([label,maximum],j)=>{
            const a=q.parts[j],g=q.markScheme[j];
            if(a.label!==label || a.marks!==maximum || g.part!==label ||
                (maximum>=10 && !g.steps.some(s=>s.code==="Markband")))throw new Error("Invalid mark allocation: "+id+" "+label);
        });
    });
    return p;
}
const loaders = {
    "economics-sl-set-a-paper-1": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-sl-set-a-paper-1.json"),
    "economics-sl-set-a-paper-2": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-sl-set-a-paper-2.json"),
    "economics-sl-set-b-paper-1": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-sl-set-b-paper-1.json"),
    "economics-sl-set-b-paper-2": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-sl-set-b-paper-2.json"),
    "economics-hl-set-a-paper-1": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-hl-set-a-paper-1.json"),
    "economics-hl-set-a-paper-2": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-hl-set-a-paper-2.json"),
    "economics-hl-set-a-paper-3": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-hl-set-a-paper-3.json"),
    "economics-hl-set-b-paper-1": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-hl-set-b-paper-1.json"),
    "economics-hl-set-b-paper-2": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-hl-set-b-paper-2.json"),
    "economics-hl-set-b-paper-3": ()=>import("@/content/ib/economics-mocks-2022/papers/economics-hl-set-b-paper-3.json"),
};
export async function getEconomicsMockPaper(id:string, paper:MockPaper) {
    const meta=getEconomicsPaperMeta(id,paper);
    if(!meta)return undefined;
    const loader=loaders[meta.id as keyof typeof loaders];
    return loader ? validateEconomicsMockPaper((await loader()).default,meta) : undefined;
}
function prompt(q:EconomicsQuestion) {
    const {id,section,number,title,optional,marks,stem,parts}=q;
    return {id,section,number,title,optional,marks,stem,parts,...(q.stimulusSvg ? {stimulusUrl:"data:image/svg+xml;base64,"+Buffer.from(q.stimulusSvg).toString("base64"),stimulusCaption:q.stimulusCaption} : {})};
}
export function economicsMockPrompt(p:EconomicsMockPaper,meta:EconomicsPaperMeta):EconomicsMockPrompt {
    return {...meta,questions:p.questions.map(prompt)};
}
export function economicsMockSolutions(p:EconomicsMockPaper):EconomicsSolution[] {
    return p.questions.map(q=>({...prompt(q),markScheme:q.markScheme,background:q.background,solutionUrl:"data:image/svg+xml;base64,"+Buffer.from(q.solutionSvg).toString("base64")}));
}
