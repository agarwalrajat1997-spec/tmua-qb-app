(() => {
 "use strict";
 const paper=location.pathname.split("/").filter(Boolean).at(-2);
 let id,reader,started,queued=Promise.resolve(),last="",final,receipt;
 async function api(op,answers){
   const r=await fetch("/api/amc/practice",{method:"POST",headers:{"Content-Type":"application/json"},cache:"no-store",body:JSON.stringify({paper,id,op,answers})});
   const j=await r.json();if(!r.ok)throw Error(j.error||"Your attempt could not be saved.");return j;
 }
 async function start(fn){
   reader=fn;if(started)return started;id=crypto.randomUUID();
   started=api("start").catch(e=>{started=null;throw e});return started;
 }
 function choices(){return Array.from(reader(),x=>/^[A-E]$/.test(x)?x:null)}
 function save(){if(!started||final||!reader)return;const ar=choices(),sig=JSON.stringify(ar);if(sig===last)return;
  last=sig;queued=queued.catch(()=>{}).then(()=>api("save",ar)).catch(()=>{if(last===sig)last="";});}
 async function finish(){
  if(receipt)return receipt;if(final)return final;if(!started)throw Error("Start your saved attempt before submitting.");
  final=(async()=>{await started;await queued;const data=await api("submit",choices());if(!data.receipt)throw Error("No score receipt returned.");return receipt=data.receipt;})().catch(e=>{final=null;throw e});return final;
 }
 function mount(r){
  let el=document.querySelector("#official-amc-receipt");if(!el){el=document.createElement("aside");el.id="official-amc-receipt";el.setAttribute("role","status");el.style.cssText="max-width:850px;margin:12px auto;padding:14px 20px;background:#fff7e5;border:1px solid #ba9964;color:#3c2530;font:600 16px/1.55 system-ui;border-radius:10px";const host=document.querySelector("#result:not([hidden]),.report-wrap,.results-container")||document.querySelector("main")||document.body;host.prepend(el);}
  el.replaceChildren();const text=document.createElement("div");text.textContent="AMC score: "+r.points+" / "+r.maximum+" · "+r.correct+" correct · "+r.incorrect+" incorrect · "+r.blanks+" blank";el.append(text);const link=document.createElement("a");link.href=r.solutionPath;link.textContent="Download worked solutions (PDF)";el.append(link);
 }
 document.addEventListener("change",()=>setTimeout(save,0));document.addEventListener("click",()=>setTimeout(save,0));
 window.TS_AMC_ATTEMPT=Object.freeze({start,save,finish,mount});
})();
