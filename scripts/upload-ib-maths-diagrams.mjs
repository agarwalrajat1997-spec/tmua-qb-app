// Uses the user's existing Wrangler OAuth connection. No credentials are read or logged here.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {createHash,randomUUID} from 'node:crypto';
const exec=promisify(execFile);
const [artifactDir,wranglerEntry]=process.argv.slice(2);
if(!artifactDir||!wranglerEntry)throw new Error('Pass staged asset directory and installed Wrangler entry path.');
const dir=resolve(artifactDir),staged=JSON.parse(readFileSync(resolve(dir,'staged-manifest.json'),'utf8'));
if(staged.bucket!=='thriving-scholars-media'||staged.origin!=='https://media.thrivingscholars.com')throw new Error('Unexpected Cloudflare target');
const resultPath=resolve(dir,'uploaded-results.json');
const done=existsSync(resultPath)?JSON.parse(readFileSync(resultPath,'utf8')):{schemaVersion:1,verified:{}};
let uploaded=0,skipped=0;
const failed=[];
async function verify(item) {
 if(process.platform==='win32') {
  // The native Windows HTTPS client remains reliable when Undici's IPv6 route times out.
  const output=resolve(dir,'assets',item.sha256+'.verified.svg');
  await exec('powershell.exe',['-NoLogo','-NoProfile','-NonInteractive','-File',resolve('scripts/verify-ib-maths-media.ps1'),'-Url',staged.origin+'/'+item.key,'-OutputPath',output],{maxBuffer:1024*1024,timeout:30000,windowsHide:true});
  const data=readFileSync(output);
  if(createHash('sha256').update(data).digest('hex')!==item.sha256)throw new Error('CDN body hash mismatch');
  return {key:item.key,bytes:data.length};
 }
 const response=await fetch(staged.origin+'/'+item.key+'?verification='+randomUUID(),{signal:AbortSignal.timeout(20000)});
 if(!response.ok)throw new Error('CDN response '+response.status);
 const data=Buffer.from(await response.arrayBuffer());
 if(createHash('sha256').update(data).digest('hex')!==item.sha256)throw new Error('CDN body hash mismatch');
 if(!response.headers.get('content-type')?.includes('image/svg+xml'))throw new Error('CDN returned incorrect image type');
 return {key:item.key,bytes:data.length};
}
for(const item of staged.objects){
 if(!/^[a-f0-9]{64}$/.test(item.sha256)||item.key!==`ib/maths/2026-10-30/${item.sha256}.svg`)throw new Error('Invalid content key');
 const path=resolve(dir,'assets',item.sha256+'.svg');
 const bytes=readFileSync(path);
 if(createHash('sha256').update(bytes).digest('hex')!==item.sha256)throw new Error('Local content hash mismatch');
 if(done.verified[item.sha256]){skipped++;continue;}
 let lastError;
 try {
  // An earlier upload may have finished even if its response or CDN check timed out.
  done.verified[item.sha256]=await verify(item);
  writeFileSync(resultPath,JSON.stringify(done,null,2)+'\n');skipped++;continue;
 }catch { /* Upload below when an existing public copy cannot be verified. */ }
 for(let attempt=0;attempt<3;attempt++){
  try{
   await exec(process.execPath,['--dns-result-order=ipv4first',wranglerEntry,'r2','object','put',staged.bucket+'/'+item.key,'--file',path,'--remote','--content-type','image/svg+xml','--cache-control','public,max-age=31536000,immutable'],{maxBuffer:1024*1024,timeout:90000,windowsHide:true});
   done.verified[item.sha256]=await verify(item);
   writeFileSync(resultPath,JSON.stringify(done,null,2)+'\n');uploaded++;lastError=undefined;break;
  }catch(error){
   lastError=error;
   console.log(JSON.stringify({retry:attempt+1,image:item.sha256.slice(0,16),reason:'Image upload or public verification did not finish'}));
   if(attempt<2)await new Promise(resolve=>setTimeout(resolve,3000*(2**attempt)));
  }
 }
 if(lastError){failed.push(item.sha256);continue;}
 if(uploaded%20===0)console.log(JSON.stringify({uploaded,skipped,total:staged.objects.length}));
}
if(failed.length)throw new Error(`${failed.length} images still need a successful upload and public verification. Resume this command; verified images are retained.`);
const assets=Object.fromEntries(staged.objects.map(item=>{if(!done.verified[item.sha256])throw new Error('Missing uploaded object');return [item.sha256,done.verified[item.sha256]];}));
writeFileSync(resolve('content/ib/maths-diagram-manifest.json'),JSON.stringify({schemaVersion:1,origin:staged.origin,assets},null,2)+'\n');
console.log(JSON.stringify({status:'verified',uploaded,skipped,total:staged.objects.length,manifest:'content/ib/maths-diagram-manifest.json'}));
