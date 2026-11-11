export type Role = "admin" | "analyst" | "reporter";

export type Organisation = {
  id: number;
  name: string;
  slug: string;
};

export type User = {
  id: number;
  full_name: string;
  email: string;
  role: Role;
  organisation_id: number;
  organisation: Organisation;
  is_active: boolean;
};

export type UserSummary = {
  id: number;
  full_name: string;
  email: string;
  role: Role;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
};

export type IncidentStatus =
  | "submitted"
  | "under_review"
  | "assigned"
  | "investigating"
  | "escalated"
  | "contained"
  | "remediated"
  | "recovered"
  | "closed";

export type Priority = "low" | "medium" | "high" | "critical";

export type IncidentListItem = {
  id: string;
  reference: string;
  title: string;
  category: string;
  status: IncidentStatus;
  priority: Priority;
  risk_score: number | null;
  ai_status: string;
  created_at: string;
  updated_at: string;
  reporter: UserSummary;
  assignee: UserSummary | null;
  evidence_count: number;
};

export type IncidentEvent = {
  id: number;
  event_type: string;
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
  actor: UserSummary | null;
};

export type EvidenceItem = {
  id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  sha256: string;
  created_at: string;
  uploader: UserSummary;
};

export type AnalysisClassification = "benign" | "suspicious" | "high_risk";

export type AnalysisReason = {
  component: "U" | "N" | "M" | "I";
  direction: "increases_risk" | "decreases_risk";
  weight: number;
  message: string;
};

export type AnalysisIndicator = {
  code: string;
  label: string;
  category: string;
  severity: "high" | "medium" | "low" | "info";
  detail: string;
};

export type AnalysisFactor = {
  key: "U" | "N" | "M" | "I";
  label: string;
  score: number;
  weight: number;
  contribution: number;
};

export type IncidentAnalysis = {
  id: string;
  status: string;
  model_version: string;
  ruleset_version: string;
  classification: AnalysisClassification;
  risk_score: number;
  confidence: number;
  url_score: number;
  nlp_score: number;
  ml_score: number;
  indicator_score: number;
  summary: string;
  reasons: AnalysisReason[];
  indicators: AnalysisIndicator[];
  factors: AnalysisFactor[];
  features: Record<string, unknown>;
  warnings: string[];
  latency_ms: number;
  created_at: string;
};

export type IncidentDetail = IncidentListItem & {
  description: string;
  channel: string;
  reported_url: string | null;
  state: string | null;
  classification: string | null;
  closed_at: string | null;
  events: IncidentEvent[];
  evidence: EvidenceItem[];
  analysis: IncidentAnalysis | null;
};

export type IncidentPage = {
  items: IncidentListItem[];
  total: number;
  page: number;
  page_size: number;
};

export type IncidentStats = {
  total: number;
  open: number;
  critical: number;
  unassigned: number;
  closed: number;
  last_7_days: number;
  average_risk: number | null;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_category: Record<string, number>;
};

export type IndicatorKind = "url" | "domain" | "ipv4" | "sha256" | "md5";

export type IndicatorSummary = {
  id: number;
  kind: IndicatorKind;
  value: string;
  display_value: string;
  incident_count: number;
  first_seen_at: string;
  last_seen_at: string;
  example_incident_id: string | null;
  example_incident_reference: string | null;
};

export type IndicatorPage = {
  items: IndicatorSummary[];
  total: number;
  page: number;
  page_size: number;
  by_kind: Record<string, number>;
};

export type IndicatorIncidentItem = {
  id: string;
  reference: string;
  title: string;
  category: string;
  status: IncidentStatus;
  priority: Priority;
  risk_score: number | null;
  classification: string | null;
  created_at: string;
  assignee_name: string | null;
  link_source: string;
  first_seen_at: string;
};

export type IndicatorDetail = IndicatorSummary & {
  incidents: IndicatorIncidentItem[];
};

export type SharedIndicatorRef = {
  id: number;
  kind: IndicatorKind;
  value: string;
  display_value: string;
};

export type RelatedIncidentItem = {
  id: string;
  reference: string;
  title: string;
  category: string;
  status: IncidentStatus;
  priority: Priority;
  risk_score: number | null;
  classification: string | null;
  created_at: string;
  assignee_name: string | null;
  shared_count: number;
  shared_indicators: SharedIndicatorRef[];
};

export type RelatedIncidentList = {
  incident_id: string;
  total: number;
  items: RelatedIncidentItem[];
};

export type DashboardCount = {
  key: string;
  label: string;
  count: number | null;
  suppressed: boolean;
};

export type TrendPoint = {
  date: string;
  total: number | null;
  high_risk: number | null;
  suppressed: boolean;
};

export type IndicatorHighlight = {
  id: number | null;
  kind: IndicatorKind;
  display_value: string;
  incident_count: number;
  organisation_count: number;
  suppressed: boolean;
};

export type DashboardSummary = {
  total: number | null;
  open: number | null;
  high_risk: number | null;
  linked_incidents: number | null;
  shared_indicators: number | null;
  mean_risk: number | null;
  mean_resolution_hours: number | null;
  organisations: number | null;
  suppressed_cells: number;
  k_threshold: number;
};

export type DashboardResponse = {
  scope: "organisation" | "national";
  generated_at: string;
  organisation: Organisation | null;
  summary: DashboardSummary;
  trend: TrendPoint[];
  severity: DashboardCount[];
  categories: DashboardCount[];
  channels: DashboardCount[];
  states: DashboardCount[];
  statuses: DashboardCount[];
  top_indicators: IndicatorHighlight[];
};

export type IncidentCreatePayload = {
  title: string;
  description: string;
  category: string;
  channel: string;
  reported_url?: string | null;
  state?: string | null;
  priority?: Priority;
};

export type AuditEntry = {
  id: number;
  organisation_id: number | null;
  actor_id: number | null;
  actor_email: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  detail: Record<string, unknown>;
  created_at: string;
  prev_hash: string;
  entry_hash: string;
};

export type AuditPage = {
  items: AuditEntry[];
  total: number;
  page: number;
  page_size: number;
};

export type AuditVerifyResult = {
  valid: boolean;
  entries_checked: number;
  first_invalid_id: number | null;
  message: string;
  latest_hash: string | null;
  checked_at: string;
};

const API_BASE = (
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1"
).replace(/\/$/, "");

const TOKEN_KEY = "votex.access_token";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Storage can be unavailable in private browsing; the session still works in memory.
  }
}

function extractDetail(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : "",
        )
        .filter(Boolean);
      if (messages.length) return messages.join(" ");
    }
  }
  return "Something went wrong. Please try again.";
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(
      "Cannot reach the Votex API. Check that the backend is running on port 8000.",
      0,
    );
  }

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    throw new ApiError(extractDetail(payload), response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

function queryString(params: Record<string, string | number | boolean | undefined>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== false) {
      search.set(key, String(value));
    }
  });
  const text = search.toString();
  return text ? `?${text}` : "";
}

export const api = {
  login: (email: string, password: string) =>
    request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>("/auth/me"),

  users: () => request<UserSummary[]>("/users"),

  stats: () => request<IncidentStats>("/incidents/stats"),

  incidents: (params: {
    status?: string;
    priority?: string;
    category?: string;
    search?: string;
    assigned_to_me?: boolean;
    page?: number;
    page_size?: number;
  } = {}) => request<IncidentPage>(`/incidents${queryString(params)}`),

  incident: (id: string) => request<IncidentDetail>(`/incidents/${id}`),

  createIncident: (payload: IncidentCreatePayload) =>
    request<IncidentDetail>("/incidents", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  assign: (id: string, assigneeId: number) =>
    request<IncidentDetail>(`/incidents/${id}/assignment`, {
      method: "PATCH",
      body: JSON.stringify({ assignee_id: assigneeId }),
    }),

  setStatus: (id: string, status: IncidentStatus, note?: string) =>
    request<IncidentDetail>(`/incidents/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, note: note || null }),
    }),

  setPriority: (id: string, priority: Priority) =>
    request<IncidentDetail>(`/incidents/${id}/priority`, {
      method: "PATCH",
      body: JSON.stringify({ priority }),
    }),

  addAction: (id: string, actionType: string, note: string) =>
    request<IncidentEvent>(`/incidents/${id}/actions`, {
      method: "POST",
      body: JSON.stringify({ action_type: actionType, note }),
    }),

  addComment: (id: string, message: string) =>
    request<IncidentEvent>(`/incidents/${id}/comments`, {
      method: "POST",
      body: JSON.stringify({ message }),
    }),

  analyzeIncident: (id: string) =>
    request<IncidentDetail>(`/incidents/${id}/analyze`, { method: "POST" }),

  relatedIncidents: (id: string) =>
    request<RelatedIncidentList>(`/incidents/${id}/related`),

  indicators: (params: {
    q?: string;
    kind?: IndicatorKind;
    page?: number;
    page_size?: number;
  } = {}) => request<IndicatorPage>(`/indicators${queryString(params)}`),

  indicator: (id: number) => request<IndicatorDetail>(`/indicators/${id}`),

  organisationDashboard: () => request<DashboardResponse>("/dashboards/organisation"),

  nationalDashboard: () => request<DashboardResponse>("/dashboards/national"),

  uploadEvidence: (id: string, file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<EvidenceItem>(`/incidents/${id}/evidence`, { method: "POST", body });
  },

  audit: (params: { action?: string; page?: number; page_size?: number } = {}) =>
    request<AuditPage>(`/audit${queryString(params)}`),

  verifyAudit: () => request<AuditVerifyResult>("/audit/verify"),
};

export async function downloadEvidence(
  incidentId: string,
  evidenceId: string,
): Promise<{ filename: string; sha256: string | null }> {
  const headers = new Headers();
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(
      `${API_BASE}/incidents/${incidentId}/evidence/${evidenceId}/download`,
      { headers },
    );
  } catch {
    throw new ApiError("Cannot reach the Votex API to download this file.", 0);
  }

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    throw new ApiError(extractDetail(payload), response.status);
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = /filename="?([^";]+)"?/i.exec(disposition);
  const filename = match?.[1] ?? "evidence";

  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);

  return { filename, sha256: response.headers.get("X-Content-SHA256") };
}

export async function downloadCsv(path: string, fallbackName: string): Promise<string> {
  const headers = new Headers();
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { headers });
  } catch {
    throw new ApiError("Cannot reach the Votex API to export this dataset.", 0);
  }

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    throw new ApiError(extractDetail(payload), response.status);
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = /filename="?([^";]+)"?/i.exec(disposition);
  const filename = match?.[1] ?? fallbackName;

  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
  return filename;
}
