// Uses the existing Wrangler OAuth session. Never reads or logs its credentials.
import assert from 'node:assert/strict';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {ORIGIN,BUCKET,MANIFEST,readStage,sha} from './psychology-media.mjs';
const [artifactDirectory,wranglerEntry]=process.argv.slice(2);
assert.ok(artifactDirectory&&wranglerEntry,'Pass the staged artifact directory and installed Wrangler entry path');
assert.ok(existsSync(wranglerEntry),'Wrangler entry must exist');
const directory=resolve(artifactDirectory),stage=readStage(directory),exec=promisify(execFile);
const logs=resolve(directory,'wrangler-logs');mkdirSync(logs,{recursive:true});
const env={...process.env,WRANGLER_LOG_PATH:logs,WRANGLER_SEND_METRICS:'false'};
const progressPath=resolve(directory,'uploaded-results.json'),progress=existsSync(progressPath)?JSON.parse(readFileSync(progressPath,'utf8')):{schemaVersion:1,verified:{}};
const verified={};let uploaded=0,reused=0;
function failureCode(error){
  if(/not authenticated|not logged in|authentication error|requires authentication/i.test(error?.stderr??''))return 'AUTHENTICATION_REQUIRED';
  const value=error?.cause?.code??error?.code;
  return typeof value==='string'&&/^[A-Z_0-9]{1,40}$/.test(value)?value:'UNCONFIRMED';
}
async function publicBytes(item){
  const response=await fetch(`${ORIGIN}/${item.key}`,{signal:AbortSignal.timeout(25000)});
  assert.equal(response.status,200);assert.match(response.headers.get('content-type')??'',/^image\/svg\+xml\b/);
  const bytes=Buffer.from(await response.arrayBuffer());assert.equal(sha(bytes),item.sha256);assert.equal(bytes.length,item.bytes);
  return {key:item.key,bytes:bytes.length,contentType:'image/svg+xml'};
}
for(const item of stage.objects){
  const file=resolve(directory,'assets',item.sha256+'.svg'),bytes=readFileSync(file);
  assert.equal(sha(bytes),item.sha256);assert.equal(bytes.length,item.bytes);
  // Every resumed object is rechecked publicly; a stale progress file is insufficient.
  // Do not probe a new path before upload: the CDN can retain a negative cache
  // response. The SHA in the actual public path already identifies immutable bytes.
  try{assert.ok(progress.verified[item.sha256]);verified[item.sha256]=await publicBytes(item);reused++;}catch{
    let success=false;
    for(let attempt=1;attempt<=3;attempt++)try{
      await exec(process.execPath,['--dns-result-order=ipv4first',resolve(wranglerEntry),'r2','object','put',`${BUCKET}/${item.key}`,'--file',file,'--remote','--content-type','image/svg+xml','--cache-control','public,max-age=31536000,immutable'],{env,windowsHide:true,maxBuffer:1024*1024,timeout:60000});
      verified[item.sha256]=await publicBytes(item);uploaded++;success=true;break;
    }catch(error){console.log(JSON.stringify({image:item.sha256.slice(0,16),attempt,status:'Upload or public-byte verification did not complete',failure:failureCode(error)}));if(attempt<3)await new Promise(r=>setTimeout(r,1000*attempt));}
    assert.ok(success,`Image ${item.sha256.slice(0,16)} needs another transfer; canonical files are unchanged`);
  }
  progress.verified[item.sha256]=verified[item.sha256];writeFileSync(progressPath,JSON.stringify(progress,null,2)+'\n');
  if((uploaded+reused)%20===0)console.log(JSON.stringify({uploaded,reused,total:stage.objects.length}));
}
writeFileSync(MANIFEST,JSON.stringify({schemaVersion:1,origin:ORIGIN,assets:verified},null,2)+'\n');
console.log(JSON.stringify({status:'public-bytes-verified',uploaded,reused,assets:Object.keys(verified).length,manifest:MANIFEST}));
