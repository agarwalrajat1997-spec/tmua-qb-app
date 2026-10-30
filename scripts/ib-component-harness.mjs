// Isolated server-component renderer for tests and local visual review only.
// This is never imported by the application and creates no authentication bypass.
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
const require=createRequire(import.meta.url);
export function ibHarness({ questions=[], user={email:'review@example.invalid'}, onAuth=()=>{}, onDestination=()=>{}, query='', useContentModule=false }={}) {
  const cache=new Map();
  const userReader=async destination=>{onAuth(destination);if(!user)throw new Error('AUTH_REQUIRED');return user;};
  const mocks={
    'server-only':{},
    'next/link':{__esModule:true,default:({children,href,...props})=>{const anchorProps={...props};delete anchorProps.prefetch;return React.createElement('a',{...anchorProps,href},children);}},
    'next/navigation':{useSearchParams:()=>new URLSearchParams(query),notFound(){throw new Error('NOT_FOUND');},redirect(url){onDestination(url);throw new Error('REDIRECT');}},
    '@/lib/ib/auth':{requireIbUser:userReader},
    '@/utils/supabase/server':{supabaseServer:async()=>({auth:{getUser:async()=>({data:{user},error:null})}})},
    '@/utils/supabase/browser':{supabaseBrowser:()=>{const blocked=()=>{throw new Error('NO_LIVE_AUTH_IN_REVIEW');};return {auth:{getUser:blocked,signInWithOtp:blocked,signOut:blocked}};}},
    '@/lib/ib/content':{getIbQuestion:(id,course)=>questions.find(q=>q.id===id&&q.status==='published'&&load('lib/ib/question.ts').questionAvailableForCourse(q,course)),getIbQuestions:(collection,course)=>questions.filter(q=>q.status==='published'&&(!collection||q.collectionId===collection)&&load('lib/ib/question.ts').questionAvailableForCourse(q,course))},
  };
  if(useContentModule)delete mocks['@/lib/ib/content'];
  function load(filename) {
    const absolute=resolve(filename);
    if(cache.has(absolute))return cache.get(absolute);
    const compiled=ts.transpileModule(readFileSync(absolute,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText;
    const exports={};cache.set(absolute,exports);
    const context=vm.createContext({exports,Buffer,URL,URLSearchParams,console,process,setTimeout,clearTimeout,
      require(name){
        if(name in mocks)return mocks[name];
        if(name.endsWith('.css'))return {__esModule:true,default:new Proxy({},{get:(_t,p)=>String(p)})};
        if(name.startsWith('@/') && name.endsWith('.json')) {
          const bank=name.match(/^@\/content\/ib\/([^/]+)\/([^/]+)\.json$/);
          if(useContentModule&&bank)return questions.filter(q=>q.subject===bank[1]&&(q.collectionId===bank[2]||q.topicId===bank[2]));
          return require(resolve(name.slice(2)));
        }
        if(name.startsWith('@/'))return load(resolve(name.slice(2))+ (name.endsWith('.ts')||name.endsWith('.tsx')?'':'.ts'));
        if(name.startsWith('.')) {
          const path=resolve(dirname(absolute),name);
          if(/\.tsx?$/.test(path))return load(path);
          if(/\.[cm]?jsx?$/.test(path))return require(path);
          for(const ext of ['.tsx','.ts']){try{return load(path+ext);}catch(error){if(error.code!=='ENOENT')throw error;}}
        }
        return require(name);
      }});
    vm.runInContext(compiled,context,{filename:absolute});
    return exports;
  }
  return {load,model:load('lib/ib/question.ts')};
}
