import { createHash } from "node:crypto";
import type { SupabaseClient } from "@supabase/supabase-js";
import { z } from "zod/v3";
import { StudioError } from "./http";
const keySchema=z.string().min(1).max(400).regex(/^(board|notebook|review|view|session):[\w:./ @-]+$/);
export const notebookInput=z.object({key:keySchema,baseVersion:z.number().int().nonnegative(),value:z.unknown()}).strict();
function storageKey(key:unknown,userId:string){
  const parsed=keySchema.parse(key);
  if(!parsed.split(":").some((part,i,parts)=>part==="user"&&parts[i+1]===userId)) throw new StudioError(403,"This notebook belongs to another account.");
  return `studio:notebook:${createHash("sha256").update(parsed).digest("hex")}`;
}
export async function loadNotebook(db:SupabaseClient,userId:string,key:unknown){
  const {data,error}=await db.from("user_progress").select("data,updated_at").eq("user_id",userId).eq("product","tmua-question-bank").eq("key",storageKey(key,userId)).maybeSingle().retry(false);
  if(error)throw new StudioError(503,"Your cloud notebook is temporarily unavailable. Your device copy remains safe.");
  return data ? {version:data.data.version,updatedAt:Date.parse(data.updated_at),value:data.data.value} : {version:0};
}
export async function saveNotebook(db:SupabaseClient,user:{id:string;email:string},raw:unknown){
  const input=notebookInput.parse(raw);const key=storageKey(input.key,user.id);
  const value=JSON.stringify(input.value);
  if(!value||Buffer.byteLength(value)>4_200_000)throw new StudioError(413,"This notebook is too large for cloud sync. Your device copy is safe.");
  const version=input.baseVersion+1;
  const row={user_id:user.id,email:user.email.toLowerCase(),product:"tmua-question-bank",key,data:{version,value:input.value},updated_at:new Date().toISOString()};
  const result=input.baseVersion===0
    ? await db.from("user_progress").insert(row).select("updated_at").maybeSingle().retry(false)
    : await db.from("user_progress").update({data:row.data,updated_at:row.updated_at}).eq("user_id",user.id).eq("product",row.product).eq("key",key).eq("data->>version",String(input.baseVersion)).select("updated_at").maybeSingle().retry(false);
  if(result.error && result.error.code!=="23505")throw new StudioError(503,"Cloud saving is temporarily unavailable. Your device copy is safe.");
  if(result.error?.code==="23505"||!result.data)throw new StudioError(409,"Another device saved a newer copy. Your local copy is preserved.","NOTEBOOK_CONFLICT");
  return {version,updatedAt:Date.parse(result.data.updated_at)};
}
