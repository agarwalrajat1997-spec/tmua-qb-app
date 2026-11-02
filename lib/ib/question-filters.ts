export type IbFilterQuery = Record<string, string | string[] | undefined>;
export const singleQueryValue = (value: IbFilterQuery[string]) => typeof value === "string" ? value : "";
export function queryValues(value: IbFilterQuery[string]): string[] {
  return [...new Set((Array.isArray(value) ? value : value ? [value] : []).slice(0, 100).map(item => item.slice(0, 160)))];
}
export function selectedValues(value: IbFilterQuery[string], allowed: readonly string[]) {
  return queryValues(value).filter(item => allowed.includes(item));
}
export function ibFilterHref(pathname: string, values: IbFilterQuery) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) for (const item of queryValues(value)) if (item) query.append(key, item);
  return pathname + (query.size ? "?" + query : "");
}
