const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ExtractionResult {
  fields: Record<string, unknown>;
  parser_config_id: number | null;
  parser_config_name: string;
}

export interface SubmissionPayload {
  filename: string;
  extracted_fields: Record<string, string>;
  final_fields: Record<string, string>;
  parser_config_id?: number | null;
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

export interface ParserConfig {
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

export interface ParserConfigVersion {
  id: number;
  version_number: number;
  prompt: string;
  model: string;
  output_schema: Record<string, unknown>;
  created_at: string | null;
}

export interface ModelInfo {
  id: string;
  name: string;
  tier: string;
  cost_hint: string;
}

export interface ABTestResultItem {
  parser_config_id: number;
  parser_config_name: string;
  model: string;
  fields: Record<string, unknown>;
  response_time_ms: number;
  success: boolean;
  error: string | null;
}

// Extraction
export async function extractFromFile(file: File, parserConfigId?: number | null): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);
  if (parserConfigId != null) {
    formData.append("parser_config_id", String(parserConfigId));
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

export async function getExtractionLogs(page: number = 1, pageSize: number = 50, parserConfigId?: number | null): Promise<PaginatedLogsResponse> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (parserConfigId != null) params.set("parser_config_id", String(parserConfigId));
  const response = await fetch(`${API_BASE_URL}/extraction/logs?${params}`);
  if (!response.ok) throw new Error("Failed to fetch extraction logs");
  return response.json();
}

export async function getApiCallMetrics(parserConfigId?: number | null): Promise<ApiCallMetrics> {
  const params = parserConfigId != null ? `?parser_config_id=${parserConfigId}` : "";
  const response = await fetch(`${API_BASE_URL}/extraction/api-metrics${params}`);
  if (!response.ok) throw new Error("Failed to fetch API call metrics");
  return response.json();
}

export async function getMetrics(parserConfigId?: number | null): Promise<Metrics> {
  const params = parserConfigId != null ? `?parser_config_id=${parserConfigId}` : "";
  const response = await fetch(`${API_BASE_URL}/extraction/metrics${params}`);
  if (!response.ok) throw new Error("Failed to fetch metrics");
  return response.json();
}

// Parser Configs
export async function getParserConfigs(): Promise<ParserConfig[]> {
  const response = await fetch(`${API_BASE_URL}/parsers`);
  if (!response.ok) throw new Error("Failed to fetch parser configs");
  const data = await response.json();
  return data.configs;
}

export async function getParserConfig(id: number): Promise<ParserConfig> {
  const response = await fetch(`${API_BASE_URL}/parsers/${id}`);
  if (!response.ok) throw new Error("Failed to fetch parser config");
  return response.json();
}

export async function createParserConfig(config: {
  name: string;
  description: string;
  prompt: string;
  model: string;
  output_schema: Record<string, unknown>;
  is_default?: boolean;
}): Promise<ParserConfig> {
  const response = await fetch(`${API_BASE_URL}/parsers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create parser config");
  }
  return response.json();
}

export async function updateParserConfig(id: number, config: {
  name?: string;
  description?: string;
  prompt?: string;
  model?: string;
  output_schema?: Record<string, unknown>;
  is_default?: boolean;
}): Promise<ParserConfig> {
  const response = await fetch(`${API_BASE_URL}/parsers/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update parser config");
  }
  return response.json();
}

export async function deleteParserConfig(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/parsers/${id}`, { method: "DELETE" });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to delete parser config");
  }
}

export async function getAvailableModels(): Promise<ModelInfo[]> {
  const response = await fetch(`${API_BASE_URL}/parsers/models`);
  if (!response.ok) throw new Error("Failed to fetch models");
  return response.json();
}

export async function getParserVersions(id: number): Promise<ParserConfigVersion[]> {
  const response = await fetch(`${API_BASE_URL}/parsers/${id}/versions`);
  if (!response.ok) throw new Error("Failed to fetch versions");
  return response.json();
}

export async function runABTest(file: File, configIds: number[]): Promise<ABTestResultItem[]> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("config_ids", configIds.join(","));

  const response = await fetch(`${API_BASE_URL}/extraction/ab-test`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "A/B test failed");
  }

  const data = await response.json();
  return data.results;
}
