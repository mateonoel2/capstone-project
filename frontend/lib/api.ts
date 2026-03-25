import { useExtractionStore } from "./store";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getAuthHeaders(): Record<string, string> {
  const token = useExtractionStore.getState().backendToken;
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

async function authFetch(url: string, init?: RequestInit): Promise<Response> {
  const authHeaders = getAuthHeaders();
  const response = await fetch(url, {
    ...init,
    headers: {
      ...authHeaders,
      ...init?.headers,
    },
  });

  if (response.status === 401) {
    useExtractionStore.getState().clearBackendAuth();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }

  return response;
}

export class QuotaExceededError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "QuotaExceededError";
  }
}

async function parseErrorDetail(response: Response, fallback: string): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
    if (body.detail) return JSON.stringify(body.detail);
    return fallback;
  } catch {
    return `${fallback} (HTTP ${response.status})`;
  }
}

async function throwIfError(response: Response, fallback: string): Promise<void> {
  if (response.ok) return;
  const detail = await parseErrorDetail(response, fallback);
  if (response.status === 429) {
    throw new QuotaExceededError(detail);
  }
  throw new Error(detail);
}

export interface ExtractionResult {
  fields: Record<string, unknown>;
  extractor_config_id: number | null;
  extractor_config_name: string;
  extractor_config_version_id: number | null;
  extractor_config_version_number: number | null;
}

export interface SubmissionPayload {
  filename: string;
  extracted_fields: Record<string, string>;
  final_fields: Record<string, string>;
  extractor_config_id?: number | null;
  extractor_config_version_id?: number | null;
}

export interface Bank {
  name: string;
  code: string;
}

export interface ExtractionLog {
  id: number;
  timestamp: string;
  filename: string;
  extracted_fields: Record<string, string>;
  final_fields: Record<string, string>;
  corrected_fields: Record<string, boolean>;
}

export interface Metrics {
  total_extractions: number;
  total_corrections: number;
  accuracy_rate: number;
  this_week: number;
  field_accuracies: Record<string, number>;
}

export interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginatedLogsResponse {
  logs: ExtractionLog[];
  pagination: PaginationMeta;
}

export interface ErrorBreakdownItem {
  error_type: string;
  count: number;
}

export interface ApiCallMetrics {
  total_calls: number;
  total_failures: number;
  error_rate: number;
  avg_response_time_ms: number;
  calls_this_week: number;
  error_breakdown: ErrorBreakdownItem[];
}

export interface ExtractorConfig {
  id: number;
  name: string;
  description: string | null;
  prompt: string;
  model: string;
  output_schema: Record<string, unknown>;
  is_default: boolean;
  status: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ExtractorConfigVersion {
  id: number;
  version_number: number;
  prompt: string;
  model: string;
  output_schema: Record<string, unknown>;
  is_active: boolean;
  created_at: string | null;
}

export interface ModelInfo {
  id: string;
  name: string;
  tier: string;
  cost_hint: string;
  is_available: boolean;
}

// Auth
export interface BackendUser {
  id: number;
  github_username: string;
  email: string | null;
  avatar_url: string | null;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: BackendUser;
}

export async function loginToBackend(githubAccessToken: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ github_access_token: githubAccessToken }),
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response, "Login failed"));
  }

  return response.json();
}

export async function getMe(): Promise<BackendUser> {
  const response = await authFetch(`${API_BASE_URL}/auth/me`);
  if (!response.ok) throw new Error("Failed to fetch user info");
  return response.json();
}

// Usage Quota
export interface UsageQuotaResource {
  used: number;
  limit: number;
}

export interface UsageQuota {
  unlimited: boolean;
  extractions?: UsageQuotaResource;
  extractors?: UsageQuotaResource;
  ai_prompts?: UsageQuotaResource;
}

export async function getUsageQuota(): Promise<UsageQuota> {
  const response = await authFetch(`${API_BASE_URL}/auth/usage`);
  if (!response.ok) throw new Error("Failed to fetch usage quota");
  return response.json();
}

// Admin
export interface AdminUser {
  id: number;
  github_id: number | null;
  github_username: string;
  email: string | null;
  avatar_url: string | null;
  role: string;
  is_active: boolean;
}

export async function getUsers(): Promise<AdminUser[]> {
  const response = await authFetch(`${API_BASE_URL}/admin/users`);
  if (!response.ok) throw new Error(await parseErrorDetail(response, "Failed to fetch users"));
  return response.json();
}

export async function createUser(github_username: string, role: string = "user"): Promise<AdminUser> {
  const response = await authFetch(`${API_BASE_URL}/admin/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ github_username, role }),
  });
  if (!response.ok) throw new Error(await parseErrorDetail(response, "Failed to create user"));
  return response.json();
}

export async function updateUser(id: number, data: { role?: string; is_active?: boolean }): Promise<AdminUser> {
  const response = await authFetch(`${API_BASE_URL}/admin/users/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error(await parseErrorDetail(response, "Failed to update user"));
  return response.json();
}

export async function deleteUser(id: number): Promise<void> {
  const response = await authFetch(`${API_BASE_URL}/admin/users/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error(await parseErrorDetail(response, "Failed to delete user"));
}

// Upload
export interface UploadResult {
  s3_key: string;
  filename: string;
}

export async function uploadFile(file: File): Promise<UploadResult> {
  // Step 1: Request a presigned upload URL
  const urlResponse = await authFetch(`${API_BASE_URL}/extraction/upload-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename: file.name, content_type: file.type || "application/pdf" }),
  });

  if (!urlResponse.ok) {
    throw new Error(await parseErrorDetail(urlResponse, "Upload failed"));
  }

  const { s3_key, upload_url, filename } = await urlResponse.json();

  let needsBackendFallback = !upload_url;

  if (upload_url) {
    // Step 2a: Upload directly to S3 via presigned URL
    try {
      const putResponse = await fetch(upload_url, {
        method: "PUT",
        headers: { "Content-Type": file.type || "application/pdf" },
        body: file,
      });

      if (!putResponse.ok) {
        needsBackendFallback = true;
      }
    } catch {
      // CORS or network error — fall back to backend proxy
      needsBackendFallback = true;
    }
  }

  if (needsBackendFallback) {
    // Step 2b: Fallback — upload through backend
    const formData = new FormData();
    formData.append("file", file);

    const fallbackResponse = await authFetch(`${API_BASE_URL}/extraction/upload`, {
      method: "POST",
      body: formData,
    });

    if (!fallbackResponse.ok) {
      throw new Error(await parseErrorDetail(fallbackResponse, "Upload failed"));
    }
  }

  return { s3_key, filename };
}

// Extraction
export async function extractFromFile(s3Key: string, filename: string, extractorConfigId?: number | null): Promise<ExtractionResult> {
  const response = await authFetch(`${API_BASE_URL}/extraction/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      s3_key: s3Key,
      filename,
      extractor_config_id: extractorConfigId ?? null,
    }),
  });

  await throwIfError(response, "Extraction failed");
  return response.json();
}

export async function submitExtraction(payload: SubmissionPayload): Promise<void> {
  const response = await authFetch(`${API_BASE_URL}/extraction/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response, "Submission failed"));
  }
}

export async function getBanks(): Promise<Bank[]> {
  const response = await authFetch(`${API_BASE_URL}/extraction/banks`);
  if (!response.ok) throw new Error("Failed to fetch banks");
  const data = await response.json();
  return data.banks;
}

export async function getExtractionLogs(page: number = 1, pageSize: number = 50, extractorConfigId?: number | null): Promise<PaginatedLogsResponse> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (extractorConfigId != null) params.set("extractor_config_id", String(extractorConfigId));
  const response = await authFetch(`${API_BASE_URL}/extraction/logs?${params}`);
  if (!response.ok) throw new Error("Failed to fetch extraction logs");
  return response.json();
}

export async function getApiCallMetrics(extractorConfigId?: number | null): Promise<ApiCallMetrics> {
  const params = extractorConfigId != null ? `?extractor_config_id=${extractorConfigId}` : "";
  const response = await authFetch(`${API_BASE_URL}/extraction/api-metrics${params}`);
  if (!response.ok) throw new Error("Failed to fetch API call metrics");
  return response.json();
}

export async function getMetrics(extractorConfigId?: number | null): Promise<Metrics> {
  const params = extractorConfigId != null ? `?extractor_config_id=${extractorConfigId}` : "";
  const response = await authFetch(`${API_BASE_URL}/extraction/metrics${params}`);
  if (!response.ok) throw new Error("Failed to fetch metrics");
  return response.json();
}

// Extractor Configs
export async function getExtractorConfigs(status?: string): Promise<ExtractorConfig[]> {
  const params = status != null ? `?status=${status}` : "";
  const response = await authFetch(`${API_BASE_URL}/extractors${params}`);
  if (!response.ok) throw new Error("Failed to fetch extractor configs");
  const data = await response.json();
  return data.configs;
}

export async function getExtractorConfig(id: number): Promise<ExtractorConfig> {
  const response = await authFetch(`${API_BASE_URL}/extractors/${id}`);
  if (!response.ok) throw new Error("Failed to fetch extractor config");
  return response.json();
}

export async function createExtractorConfig(config: {
  name: string;
  description?: string;
  prompt?: string;
  model?: string;
  output_schema?: Record<string, unknown>;
  is_default?: boolean;
  status?: string;
}): Promise<ExtractorConfig> {
  const response = await authFetch(`${API_BASE_URL}/extractors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  await throwIfError(response, "Failed to create extractor config");
  return response.json();
}

export async function updateExtractorConfig(id: number, config: {
  name?: string;
  description?: string;
  prompt?: string;
  model?: string;
  output_schema?: Record<string, unknown>;
  is_default?: boolean;
  status?: string;
}): Promise<ExtractorConfig> {
  const response = await authFetch(`${API_BASE_URL}/extractors/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) {
    throw new Error(await parseErrorDetail(response, "Failed to update extractor config"));
  }
  return response.json();
}

export async function deleteExtractorConfig(id: number): Promise<void> {
  const response = await authFetch(`${API_BASE_URL}/extractors/${id}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(await parseErrorDetail(response, "Failed to delete extractor config"));
  }
}

export async function getAvailableModels(): Promise<ModelInfo[]> {
  const response = await authFetch(`${API_BASE_URL}/extractors/models`);
  if (!response.ok) throw new Error("Failed to fetch models");
  return response.json();
}

export async function getExtractorVersions(id: number): Promise<ExtractorConfigVersion[]> {
  const response = await authFetch(`${API_BASE_URL}/extractors/${id}/versions`);
  if (!response.ok) throw new Error("Failed to fetch versions");
  return response.json();
}

export async function testExtract(
  s3Key: string,
  filename: string,
  config: { prompt: string; model: string; output_schema: Record<string, unknown> },
  extractorConfigId?: number | null
): Promise<{ fields: Record<string, unknown>; response_time_ms: number; test_log_id: number | null }> {
  const response = await authFetch(`${API_BASE_URL}/extractors/test-extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      s3_key: s3Key,
      filename,
      config,
      extractor_config_id: extractorConfigId ?? null,
    }),
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response, "Test extraction failed"));
  }

  return response.json();
}

export async function generateSchema(description: string): Promise<{ output_schema: Record<string, unknown> }> {
  const response = await authFetch(`${API_BASE_URL}/extractors/generate-schema`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description }),
  });
  await throwIfError(response, "Failed to generate schema");
  return response.json();
}

export async function generatePrompt(
  output_schema: Record<string, unknown>,
  document_type: string | null
): Promise<{ prompt: string }> {
  const response = await authFetch(`${API_BASE_URL}/extractors/generate-prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ output_schema, document_type }),
  });
  await throwIfError(response, "Failed to generate prompt");
  return response.json();
}

export async function updatePrompt(
  current_prompt: string,
  instructions: string,
  output_schema: Record<string, unknown>
): Promise<{ prompt: string }> {
  const response = await authFetch(`${API_BASE_URL}/extractors/update-prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ current_prompt, instructions, output_schema }),
  });
  await throwIfError(response, "Failed to update prompt");
  return response.json();
}

// API Tokens
export interface ApiToken {
  id: number;
  name: string;
  created_at: string | null;
  expires_at: string | null;
  last_used_at: string | null;
  is_revoked: boolean;
}

export interface CreateTokenResponse {
  token: string;
  id: number;
  name: string;
  expires_at: string | null;
}

export async function getApiTokens(): Promise<ApiToken[]> {
  const response = await authFetch(`${API_BASE_URL}/tokens`);
  if (!response.ok) throw new Error(await parseErrorDetail(response, "Failed to fetch tokens"));
  return response.json();
}

export async function createApiToken(
  name: string,
  expires_at?: string | null
): Promise<CreateTokenResponse> {
  const response = await authFetch(`${API_BASE_URL}/tokens`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, expires_at: expires_at ?? null }),
  });
  await throwIfError(response, "Failed to create token");
  return response.json();
}

export async function revokeApiToken(id: number): Promise<void> {
  const response = await authFetch(`${API_BASE_URL}/tokens/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error(await parseErrorDetail(response, "Failed to revoke token"));
}

export async function toggleVersionActive(
  configId: number,
  versionId: number,
  isActive: boolean
): Promise<ExtractorConfigVersion> {
  const response = await authFetch(
    `${API_BASE_URL}/extractors/${configId}/versions/${versionId}/active`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_active: isActive }),
    }
  );

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response, "Failed to toggle version"));
  }

  return response.json();
}
