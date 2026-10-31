export class StudioError extends Error {
  constructor(public status: number, message: string, public code?: string) { super(message); }
}
export function studioJson(value: unknown, status=200) {
  return Response.json(value, {status, headers: {
    "Cache-Control": "private, no-store, max-age=0", "Vary":"Cookie", "X-Content-Type-Options":"nosniff",
    ...(status===503 ? {"Retry-After":"30"} : {}),
  }});
}
export function assertOrigin(request: Request, env: Record<string,string|undefined> = process.env) {
  const reject=()=>{throw new StudioError(403,"Open this request from your Study Studio.");};
  if(request.headers.get("X-TS-Studio")!=="1")reject();
  const requestUrl=new URL(request.url);
  // Next can reconstruct an internal URL using localhost even though the incoming
  // browser request used 127.0.0.1 or the public domain. Host is the requested
  // authority; browsers cannot override it. Never trust X-Forwarded-Host here.
  const authority=request.headers.get("Host")??requestUrl.host;
  if(!authority||/[\s,/@\\?#]/.test(authority))reject();
  const forwardedProto=request.headers.get("X-Forwarded-Proto");
  const protocol=env.VERCEL==="1"&&(forwardedProto==="https"||forwardedProto==="http")
    ? `${forwardedProto}:` : requestUrl.protocol;
  if(protocol!=="http:"&&protocol!=="https:")reject();
  let expectedOrigin:string;
  try{expectedOrigin=new URL(`${protocol}//${authority}`).origin;}catch{reject();return;}
  const origin=request.headers.get("Origin");
  if(origin&&origin!==expectedOrigin)reject();
  if(request.headers.get("Sec-Fetch-Site")==="cross-site")reject();
}
export async function readBody(request: Request) {
  const limit=4_400_000;
  if (Number(request.headers.get("Content-Length"))>limit) throw new StudioError(413,"This page is too large. Your device copy is safe.");
  const reader=request.body?.getReader(); if(!reader) throw new StudioError(400,"Missing request.");
  const chunks:Uint8Array[]=[];let length=0;
  while(true){const {done,value}=await reader.read();if(done)break;length+=value.byteLength;if(length>limit){await reader.cancel();throw new StudioError(413,"This page is too large. Your device copy is safe.");}chunks.push(value);}
  try{return JSON.parse(Buffer.concat(chunks).toString("utf8"));}catch{throw new StudioError(400,"The request could not be read.");}
}
export function assertViewer(expected: unknown, userId: string) {
  if (expected !== userId) throw new StudioError(409,"Your signed-in account changed. Refresh the Studio before continuing.","ACCOUNT_CHANGED");
}
export function isDevelopmentPreview(env: Record<string,string|undefined>) {
  return env.NODE_ENV !== "production" && env.DEV_BYPASS_TMUA_ACCESS === "1";
}
