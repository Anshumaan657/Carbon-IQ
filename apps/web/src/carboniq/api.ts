import type { CarbonIQService, User, Project, ProjectFilters, PageResult, BuyerPreference, RecommendationRun, Portfolio, PortfolioItem, AssistantAnswer, SimulatedOrder, ImportBatch } from "./domain";
export class ApiError extends Error {
  constructor(public code: string, message: string, public status = 0, public details: unknown = null, public requestId?: string) { super(message); this.name="ApiError"; }
}
/** Never use demo as a fallback. No credentials are persisted in browser storage. */
export function createApiService(baseUrl: string, onUnauthorized?: () => void): CarbonIQService {
  let token: string | null = null;
  const base = baseUrl.replace(/\/+$/, "");
  async function request<T>(path: string, options: RequestInit = {}, blob = false): Promise<T> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    const abort = () => controller.abort();
    options.signal?.addEventListener("abort", abort, {once:true});
    if (options.signal?.aborted) controller.abort();
    try {
      const response = await fetch(`${base}${path}`, { ...options, signal: controller.signal, headers: {Accept:blob?"application/pdf":"application/json", ...(options.body && !(options.body instanceof FormData) ? {"Content-Type":"application/json"}:{}), ...(token?{Authorization:`Bearer ${token}`} : {}), ...options.headers } });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const error = payload.error || (typeof payload.detail === "object" && !Array.isArray(payload.detail) ? payload.detail : payload);
        if (response.status===401) { token=null; onUnauthorized?.(); }
        const message = typeof error.message === "string" ? error.message : typeof payload.detail === "string" ? payload.detail : response.status===422 ? "Some fields were rejected by the API. Review your inputs." : `Request failed (${response.status}).`;
        throw new ApiError(error.code || "API_ERROR", message, response.status, error.details || payload.detail, error.request_id || response.headers.get("x-request-id") || undefined);
      }
      if (blob) return await response.blob() as T;
      return response.status===204 ? undefined as T : await response.json() as T;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (options.signal?.aborted) throw error;
      throw new ApiError("CONNECTION_UNAVAILABLE", controller.signal.aborted ? "The API took too long to respond. Please try again." : "The CarbonIQ API could not be reached. Check the API address and allowed frontend origins.");
    } finally { clearTimeout(timeout); options.signal?.removeEventListener("abort",abort); }
  }
  const post = <T,>(path:string,body:unknown) => request<T>(path,{method:"POST",body:JSON.stringify(body)});
  async function signIn(email:string,password:string) { const auth=await post<{access_token:string}>("/auth/login",{email,password}); token=auth.access_token; return request<User>("/auth/me"); }
  return {
    projects(filters:ProjectFilters,signal?:AbortSignal) { const query=new URLSearchParams(); Object.entries(filters).forEach(([key,value])=>{if(value!=="") query.set(key,String(value));});return request<PageResult<Project>>(`/projects?${query}`,{signal}); },
    async project(id) { const project=await request<Project>(`/projects/${encodeURIComponent(id)}`); const [score,risk_signals]=await Promise.all([request<Project["score"]>(`/projects/${id}/score`),request<Project["risk_signals"]>(`/projects/${id}/risk-signals`)]); return {...project,score,risk_signals}; },
    compare:ids=>post<Project[]>("/projects/compare",{project_ids:ids}),
    login:signIn,
    async register(name,email,password) { await post("/auth/register",{name,email,password});return signIn(email,password); },
    logout() {token=null;},
    preferences:()=>request<BuyerPreference[]>("/preferences"),
    savePreference:preference=>preference.id ? request<BuyerPreference>(`/preferences/${preference.id}`,{method:"PATCH",body:JSON.stringify(preference)}) : post<BuyerPreference>("/preferences",preference),
    recommendations:preference=>post<RecommendationRun>("/recommendations",{preference_id:preference.id}),
    optimize:(preference,locked:PortfolioItem[]=[])=>post<Portfolio>("/portfolios/optimize",{preference_id:preference.id,budget:preference.budget,currency:preference.currency,required_credits:preference.required_credits,min_projects:preference.min_projects,max_projects:preference.max_projects,concentration_limit:preference.concentration_limit,locked_allocations:locked.map(item=>({credit_id:item.credit_id,quantity:item.quantity}))}),
    portfolios:()=>request<Portfolio[]>("/portfolios"),
    savePortfolio:portfolio=>request<Portfolio>(`/portfolios/${portfolio.id}`,{method:"PATCH",body:JSON.stringify({name:portfolio.name})}),
    ask:(id,question)=>post<AssistantAnswer>(`/projects/${encodeURIComponent(id)}/assistant/ask`,{question}),
    simulate:portfolio=>post<SimulatedOrder>("/orders/simulate",{portfolio_id:portfolio.id}),
    report:order=>request<Blob>(`/orders/${order.id}/report`,{},true),
    importProjects:file=>{const form=new FormData();form.append("file",file);return request<ImportBatch>("/imports/projects",{method:"POST",body:form});},
    importStatus:id=>request<ImportBatch>(`/imports/${encodeURIComponent(id)}`)
  };
}
