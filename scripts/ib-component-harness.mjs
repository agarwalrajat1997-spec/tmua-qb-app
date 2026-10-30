// Isolated server-component renderer for tests and local visual review only.
// This is never imported by the application and creates no authentication bypass.
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
const require=createRequire(import.meta.url);
export function ibHarness({ questions=[], user={email:'review@example.invalid'}, onAuth=()=>{}, onDestination=()=>{}, query='' }={}) {
  const cache=new Map();
  const userReader=async destination=>{onAuth(destination);if(!user)throw new Error('AUTH_REQUIRED');return user;};
  const mocks={
    'server-only':{},
    'next/link':{__esModule:true,default:({children,href,prefetch:_,...props})=>React.createElement('a',{...props,href},children)},
    'next/navigation':{useSearchParams:()=>new URLSearchParams(query),notFound(){throw new Error('NOT_FOUND');},redirect(url){onDestination(url);throw new Error('REDIRECT');}},
    '@/lib/ib/auth':{requireIbUser:userReader},
    '@/utils/supabase/browser':{supabaseBrowser:()=>{throw new Error('NO_LIVE_AUTH_IN_REVIEW');}},
    '@/lib/ib/content':{getIbQuestion:id=>questions.find(q=>q.id===id&&q.status==='published'),getIbQuestions:collection=>questions.filter(q=>q.status==='published'&&(!collection||q.collectionId===collection))},
  };
  function load(filename) {
    const absolute=resolve(filename);
    if(cache.has(absolute))return cache.get(absolute);
    const compiled=ts.transpileModule(readFileSync(absolute,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText;
    const exports={};cache.set(absolute,exports);
    const context=vm.createContext({exports,Buffer,URL,URLSearchParams,console,process,setTimeout,clearTimeout,
      require(name){
        if(name in mocks)return mocks[name];
        if(name.endsWith('.css'))return {__esModule:true,default:new Proxy({},{get:(_t,p)=>String(p)})};
        if(name.startsWith('@/'))return load(resolve(name.slice(2))+ (name.endsWith('.ts')||name.endsWith('.tsx')?'':'.ts'));
        if(name.startsWith('.')) {
          const path=resolve(dirname(absolute),name);
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
