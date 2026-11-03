/* Mathematical assets for the printable papers. No browser automation. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..');
const work=process.env.IB_AA_MOCK_WORK||path.resolve(root,'../aa-mocks-2026');
const mod=name=>require(path.join(work,'node-tools/node_modules',name));
const {mathjax}=mod('mathjax-full/js/mathjax.js');
const {TeX}=mod('mathjax-full/js/input/tex.js');
const {SVG}=mod('mathjax-full/js/output/svg.js');
const {liteAdaptor}=mod('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=mod('mathjax-full/js/handlers/html.js');
const {AllPackages}=mod('mathjax-full/js/input/tex/AllPackages.js');
const sharp=require(path.join(root,'node_modules/sharp'));
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const doc=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
const out=path.join(work,'pdf-assets');fs.mkdirSync(out,{recursive:true});
const hash=t=>crypto.createHash('sha256').update(t).digest('hex').slice(0,24);
const manifest={math:{},diagrams:{}};
(async()=>{
 const files=fs.readdirSync(path.join(root,'content/ib/aa-mocks-2026/papers')).filter(f=>f.endsWith('.json')).sort();
 const texts=[];
 for(const file of files){const paper=JSON.parse(fs.readFileSync(path.join(root,'content/ib/aa-mocks-2026/papers',file)));for(const q of paper.questions){
   texts.push(q.stem,...q.parts.map(p=>p.prompt),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text)));
   if(q.diagramSvg){const id=paper.id+'-q'+q.number;await sharp(Buffer.from(q.diagramSvg)).resize({width:1600}).png().toFile(path.join(out,id+'.png'));manifest.diagrams[id]=id+'.png';}
 }}
 const expressions=new Set();for(const text of texts)for(const m of text.matchAll(/\$\$([\s\S]*?)\$\$|\$([^$\n]+?)\$/g))expressions.add((m[1]??m[2]).trim());
 for(const tex of expressions){
   const outer=adaptor.outerHTML(doc.convert(tex,{display:false,em:16,ex:8,containerWidth:80*16}));
   if(outer.includes('data-mjx-error'))throw Error('Math rendering error: '+tex);
   let svg=outer.slice(outer.indexOf('<svg'),outer.lastIndexOf('</svg>')+6);
   const vb=svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
   const w=vb[2]/1000,h=vb[3]/1000;
   const depth=-(vb[1]+vb[3])/1000;
   const id=hash(tex);svg=svg.replace(/width="[\d.]+ex"/,`width="${Math.max(1,Math.ceil(w*46))}px"`).replace(/height="[\d.]+ex"/,`height="${Math.max(1,Math.ceil(h*46))}px"`);
   await sharp(Buffer.from(svg)).png().toFile(path.join(out,id+'.png'));
   fs.writeFileSync(path.join(out,id+'.svg'),svg);
   manifest.math[tex]={file:id+'.png',widthEm:w,heightEm:h,depthEm:depth};
 }
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 console.log(JSON.stringify({status:'passed',papers:files.length,mathExpressions:expressions.size,diagrams:Object.keys(manifest.diagrams).length}));
})().catch(e=>{console.error(e);process.exitCode=1;});
