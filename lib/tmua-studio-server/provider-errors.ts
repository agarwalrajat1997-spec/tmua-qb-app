// Error codes, rather than HTTP 429 alone, distinguish billing from throttling.
// https://developers.openai.com/api/docs/guides/error-codes
export const API_QUOTA_ERROR_MESSAGE =
  "OpenAI could not authorize API usage for this project. The owner needs to check its API credits and organization/project limits, then retry. Your working is saved.";
export const API_CREDIT_ERROR_MESSAGE =
  "OpenAI reports that this API organization's prepaid credits are exhausted. The owner needs to check the billing organization linked to this API key, then retry. Your working is saved.";

type Failure = {code:string; message:string; status:number};
const billing:Record<string,string>={
  credit_balance_exhausted:API_CREDIT_ERROR_MESSAGE,
  insufficient_quota:API_QUOTA_ERROR_MESSAGE,
  organization_spend_limit_exceeded:"OpenAI reports that the organization's API spend limit has been reached. The owner needs to check that limit, then retry. Your working is saved.",
  project_spend_limit_exceeded:"OpenAI reports that this API project's spend limit has been reached. The owner needs to check that limit, then retry. Your working is saved.",
  organization_usage_limit_exceeded:"OpenAI reports that the organization's approved API usage limit has been reached. The owner needs to check its approved limit, then retry. Your working is saved.",
};
export function classifyProviderError(code:unknown,type:unknown,httpStatus?:number):Failure|null {
  if(typeof code==="string"&&Object.hasOwn(billing,code))return {code:code==="insufficient_quota"?"quota":code,message:billing[code],status:429};
  if(type==="insufficient_quota")return {code:"quota",message:API_QUOTA_ERROR_MESSAGE,status:429};
  if(code==="rate_limit_exceeded"||code==="slow_down"||type==="rate_limit_error")return {
    code:"rate_limit",message:"OpenAI's request rate limit was reached. Wait before retrying this saved review. No automatic retry was sent.",status:429,
  };
  if(code==="model_not_found"||code==="model_access_denied"||httpStatus===404)return {
    code:"model_unavailable",message:"The selected reasoning model is unavailable to this API project. The owner needs to check model access. No weaker model was substituted; your working is saved.",status:503,
  };
  if(httpStatus===401)return {code:"invalid_key",message:"OpenAI rejected the server API key. The owner needs to check its API connection, then retry. Your working is saved.",status:503};
  if(httpStatus===403)return {code:"permission_denied",message:"OpenAI denied this API project's permission to start the review. The owner needs to check its API access, then retry. Your working is saved.",status:503};
  if(code==="server_is_overloaded")return {code:"provider_overloaded",message:"The selected model is temporarily overloaded. Wait before retrying this saved review. No automatic retry was sent.",status:503};
  return null;
}

export function failureIsSafeToRetry(diagnostics:unknown) {
  if(!diagnostics||typeof diagnostics!=="object")return false;
  const d=diagnostics as {requestRejected?:unknown;providerStatus?:unknown};
  return d.requestRejected===true||["failed","cancelled","incomplete","completed"].includes(String(d.providerStatus));
}
