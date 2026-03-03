const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ExtractionResult {
  owner: string;
  bank_name: string;
  account_number: string;
}

export interface SubmissionPayload {
  filename: string;
  extracted_owner: string;
  extracted_bank_name: string;
  extracted_account_number: string;
  final_owner: string;
  final_bank_name: string;
  final_account_number: string;
}

export interface Bank {
  name: string;
  code: string;
}

export interface ExtractionLog {
  id: number;
  timestamp: string;
  filename: string;
  extracted_owner: string;
  extracted_bank_name: string;
  extracted_account_number: string;
  final_owner: string;
  final_bank_name: string;
  final_account_number: string;
  owner_corrected: boolean;
  bank_name_corrected: boolean;
  account_number_corrected: boolean;
}

export interface Metrics {
  total_extractions: number;
  total_corrections: number;
  accuracy_rate: number;
  this_week: number;
  owner_accuracy: number;
  bank_name_accuracy: number;
  account_number_accuracy: number;
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

export async function extractFromPDF(file: File, parser: string = "claude_ocr"): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("parser", parser);

  const response = await fetch(`${API_BASE_URL}/extraction/pdf`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Extraction failed");
  }

  return response.json();
}

export async function submitExtraction(
  payload: SubmissionPayload
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/extraction/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Submission failed");
  }
}

export async function getBanks(): Promise<Bank[]> {
  const response = await fetch(`${API_BASE_URL}/extraction/banks`);

  if (!response.ok) {
    throw new Error("Failed to fetch banks");
  }

  const data = await response.json();
  return data.banks;
}

export async function getExtractionLogs(page: number = 1, pageSize: number = 50): Promise<PaginatedLogsResponse> {
  const response = await fetch(`${API_BASE_URL}/extraction/logs?page=${page}&page_size=${pageSize}`);

  if (!response.ok) {
    throw new Error("Failed to fetch extraction logs");
  }

  return response.json();
}

export async function getMetrics(): Promise<Metrics> {
  const response = await fetch(`${API_BASE_URL}/extraction/metrics`);

  if (!response.ok) {
    throw new Error("Failed to fetch metrics");
  }

  return response.json();
}

