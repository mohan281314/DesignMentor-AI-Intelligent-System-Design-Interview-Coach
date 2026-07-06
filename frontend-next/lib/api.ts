/**
 * Typed API client for the DesignMentor AI backend.
 * Reads NEXT_PUBLIC_API_URL from the environment.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login_at: string | null;
  profile: UserProfile | null;
}

export interface UserProfile {
  score_correctness: number;
  score_scalability: number;
  score_tradeoffs: number;
  score_communication: number;
  score_depth: number;
  total_interviews: number;
  total_designs: number;
  total_diagrams: number;
  experience_level: string;
  theme: string;
}

export interface DesignResult {
  topic: string;
  design: string;
  id?: number;
  saved?: boolean;
  generation_time_seconds?: number;
}

export interface DiagramResult {
  topic: string;
  diagram_type: string;
  mermaid_code: string;
  explanation: string;
  suggestions: string[];
}

export interface InterviewStart {
  interview_id?: number;
  session_id?: string;
  topic: string;
  first_question: string;
  turn_number: number;
  max_turns: number;
  status: string;
}

export interface InterviewAnswer {
  interview_id?: number;
  session_id?: string;
  turn_number: number;
  evaluation: string;
  scores?: Record<string, number | null>;
  next_question: string | null;
  is_complete: boolean;
  overall_score?: number | null;
}

export interface PerformanceSummary {
  overall_score: number;
  experience_level: string;
  total_interviews: number;
  total_designs: number;
  radar: Record<string, number>;
  trend: Array<{ date: string; score: number }>;
  topics: Array<{ topic: string; avg_score: number; attempts: number }>;
  weak_dimensions: string[];
}

export interface Recommendation {
  type: string;
  title: string;
  description: string;
  topic: string;
}

// ─── Internal fetch helper ────────────────────────────────────────────────────

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  // Attach auth token if present
  const token = typeof window !== "undefined"
    ? localStorage.getItem("access_token")
    : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail ?? JSON.stringify(err);
    } catch {/* ignore */}
    throw new Error(detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (email: string, password: string, full_name?: string) =>
    request<User>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    }),

  login: (email: string, password: string) =>
    request<Token>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>("/api/v1/auth/me"),

  logout: () => request<{ message: string }>("/api/v1/auth/logout", { method: "POST" }),

  changePassword: (current_password: string, new_password: string) =>
    request("/api/v1/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ current_password, new_password }),
    }),
};

// ─── Legacy endpoints (no auth required) ─────────────────────────────────────

export const legacyApi = {
  generateDesign: (topic: string) =>
    request<DesignResult>("/design", {
      method: "POST",
      body: JSON.stringify({ topic }),
    }),

  startInterview: (topic: string, session_id?: string) =>
    request<InterviewStart>("/interview/start", {
      method: "POST",
      body: JSON.stringify({ topic, session_id }),
    }),

  submitAnswer: (session_id: string, answer: string) =>
    request<InterviewAnswer>("/interview/answer", {
      method: "POST",
      body: JSON.stringify({ session_id, answer }),
    }),

  evaluate: (question: string, user_answer: string, reference?: string) =>
    request<{ evaluation: string }>("/evaluate", {
      method: "POST",
      body: JSON.stringify({ question, user_answer, reference }),
    }),

  generateDiagram: (
    topic: string,
    design_summary: string,
    diagram_type = "flowchart"
  ) =>
    request<DiagramResult>("/diagram", {
      method: "POST",
      body: JSON.stringify({ topic, design_summary, diagram_type }),
    }),

  generateFeedback: (topic: string, session_id?: string) =>
    request<{ topic: string; report: string }>("/feedback", {
      method: "POST",
      body: JSON.stringify({ topic, session_id }),
    }),

  chat: (message: string, session_id?: string) =>
    request<{ session_id: string; reply: string }>("/chat", {
      method: "POST",
      body: JSON.stringify({ message, session_id }),
    }),
};

// ─── Authenticated API endpoints ─────────────────────────────────────────────

export const designsApi = {
  generate: (topic: string, save = true) =>
    request<DesignResult>("/api/v1/designs/generate", {
      method: "POST",
      body: JSON.stringify(null),
    }).catch(() =>
      // fall back to legacy if not authenticated
      legacyApi.generateDesign(topic)
    ),

  list: (limit = 20, offset = 0) =>
    request<{ total: number; designs: any[] }>(
      `/api/v1/designs/?limit=${limit}&offset=${offset}`
    ),

  get: (id: number) => request<any>(`/api/v1/designs/${id}`),

  delete: (id: number) =>
    request(`/api/v1/designs/${id}`, { method: "DELETE" }),
};

export const analyticsApi = {
  performance: () => request<PerformanceSummary>("/api/v1/analytics/performance"),
  recommendations: () =>
    request<Recommendation[]>("/api/v1/analytics/recommendations"),
  activity: (limit = 10) =>
    request<any[]>(`/api/v1/analytics/activity?limit=${limit}`),
};

export const exportsApi = {
  designPdf: (designId: number) =>
    `${BASE_URL}/api/v1/exports/designs/${designId}/pdf`,
  interviewPdf: (interviewId: number) =>
    `${BASE_URL}/api/v1/exports/interviews/${interviewId}/pdf`,
};

export const sharingApi = {
  create: (resource_type: string, resource_id: number, expires_in_days?: number) =>
    request<{ public_id: string; share_url: string; expires_at: string | null }>("/api/v1/share/create", {
      method: "POST",
      body: JSON.stringify(null),
    }),
  get: (public_id: string) => request<any>(`/api/v1/share/${public_id}`),
};

// Health check
export const healthCheck = () =>
  request<{ status: string; version: string }>("/health");
