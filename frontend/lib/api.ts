const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
}

// Extraction
export async function extractFromFile(file: File, extractorConfigId?: number | null): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);
  if (extractorConfigId != null) {
    formData.append("extractor_config_id", String(extractorConfigId));
  }

  const response = await fetch(`${API_BASE_URL}/extraction/extract`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Extraction failed");
  }

  return response.json();
}

export async function submitExtraction(payload: SubmissionPayload): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/extraction/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Submission failed");
  }
}

export async function getBanks(): Promise<Bank[]> {
  const response = await fetch(`${API_BASE_URL}/extraction/banks`);
  if (!response.ok) throw new Error("Failed to fetch banks");
  const data = await response.json();
  return data.banks;
}

export async function getExtractionLogs(page: number = 1, pageSize: number = 50, extractorConfigId?: number | null): Promise<PaginatedLogsResponse> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (extractorConfigId != null) params.set("extractor_config_id", String(extractorConfigId));
  const response = await fetch(`${API_BASE_URL}/extraction/logs?${params}`);
  if (!response.ok) throw new Error("Failed to fetch extraction logs");
  return response.json();
}

export async function getApiCallMetrics(extractorConfigId?: number | null): Promise<ApiCallMetrics> {
  const params = extractorConfigId != null ? `?extractor_config_id=${extractorConfigId}` : "";
  const response = await fetch(`${API_BASE_URL}/extraction/api-metrics${params}`);
  if (!response.ok) throw new Error("Failed to fetch API call metrics");
  return response.json();
}

export async function getMetrics(extractorConfigId?: number | null): Promise<Metrics> {
  const params = extractorConfigId != null ? `?extractor_config_id=${extractorConfigId}` : "";
  const response = await fetch(`${API_BASE_URL}/extraction/metrics${params}`);
  if (!response.ok) throw new Error("Failed to fetch metrics");
  return response.json();
}

// Extractor Configs
export async function getExtractorConfigs(): Promise<ExtractorConfig[]> {
  const response = await fetch(`${API_BASE_URL}/extractors`);
  if (!response.ok) throw new Error("Failed to fetch extractor configs");
  const data = await response.json();
  return data.configs;
}

export async function getExtractorConfig(id: number): Promise<ExtractorConfig> {
  const response = await fetch(`${API_BASE_URL}/extractors/${id}`);
  if (!response.ok) throw new Error("Failed to fetch extractor config");
  return response.json();
}

export async function createExtractorConfig(config: {
  name: string;
  description: string;
  prompt: string;
  model: string;
  output_schema: Record<string, unknown>;
  is_default?: boolean;
}): Promise<ExtractorConfig> {
  const response = await fetch(`${API_BASE_URL}/extractors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create extractor config");
  }
  return response.json();
}

export async function updateExtractorConfig(id: number, config: {
  name?: string;
  description?: string;
  prompt?: string;
  model?: string;
  output_schema?: Record<string, unknown>;
  is_default?: boolean;
}): Promise<ExtractorConfig> {
  const response = await fetch(`${API_BASE_URL}/extractors/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update extractor config");
  }
  return response.json();
}

export async function deleteExtractorConfig(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/extractors/${id}`, { method: "DELETE" });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to delete extractor config");
  }
}

export async function getAvailableModels(): Promise<ModelInfo[]> {
  const response = await fetch(`${API_BASE_URL}/extractors/models`);
  if (!response.ok) throw new Error("Failed to fetch models");
  return response.json();
}

export async function getExtractorVersions(id: number): Promise<ExtractorConfigVersion[]> {
  const response = await fetch(`${API_BASE_URL}/extractors/${id}/versions`);
  if (!response.ok) throw new Error("Failed to fetch versions");
  return response.json();
}

export async function testExtract(
  file: File,
  config: { prompt: string; model: string; output_schema: Record<string, unknown> }
): Promise<{ fields: Record<string, unknown>; response_time_ms: number }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("config", JSON.stringify(config));

  const response = await fetch(`${API_BASE_URL}/extractors/test-extract`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Test extraction failed");
  }

  return response.json();
}

export async function toggleVersionActive(
  configId: number,
  versionId: number,
  isActive: boolean
): Promise<ExtractorConfigVersion> {
  const response = await fetch(
    `${API_BASE_URL}/extractors/${configId}/versions/${versionId}/active`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_active: isActive }),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to toggle version");
  }

  return response.json();
}
