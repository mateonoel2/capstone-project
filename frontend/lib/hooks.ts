import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getBanks,
  getExtractorConfigs,
  getExtractorConfig,
  getExtractorVersions,
  getMetrics,
  getApiCallMetrics,
  getExtractionLogs,
  deleteExtractorConfig,
  createExtractorConfig,
  updateExtractorConfig,
  toggleVersionActive,
  uploadFile,
  extractFromFile,
  submitExtraction,
  testExtract,
  generateSchema,
  generatePrompt,
  updatePrompt,
  getAvailableModels,
  SubmissionPayload,
} from "@/lib/api";

// Query keys
export const queryKeys = {
  banks: ["banks"] as const,
  extractorConfigs: ["extractorConfigs"] as const,
  extractorConfig: (id: number) => ["extractorConfig", id] as const,
  extractorVersions: (id: number) => ["extractorVersions", id] as const,
  metrics: (configId?: number | null) => ["metrics", configId] as const,
  apiCallMetrics: (configId?: number | null) => ["apiCallMetrics", configId] as const,
  extractionLogs: (page: number, pageSize: number, configId?: number | null) =>
    ["extractionLogs", page, pageSize, configId] as const,
  availableModels: ["availableModels"] as const,
};

// Queries
export function useBanks() {
  return useQuery({
    queryKey: queryKeys.banks,
    queryFn: getBanks,
  });
}

export function useExtractorConfigs(status?: string) {
  return useQuery({
    queryKey: [...queryKeys.extractorConfigs, status],
    queryFn: () => getExtractorConfigs(status),
  });
}

export function useExtractorConfig(id: number, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.extractorConfig(id),
    queryFn: () => getExtractorConfig(id),
    enabled: options?.enabled,
  });
}

export function useExtractorVersions(configId: number) {
  return useQuery({
    queryKey: queryKeys.extractorVersions(configId),
    queryFn: () => getExtractorVersions(configId),
  });
}

export function useMetrics(configId?: number | null) {
  return useQuery({
    queryKey: queryKeys.metrics(configId),
    queryFn: () => getMetrics(configId),
  });
}

export function useApiCallMetrics(configId?: number | null) {
  return useQuery({
    queryKey: queryKeys.apiCallMetrics(configId),
    queryFn: () => getApiCallMetrics(configId),
  });
}

export function useExtractionLogs(page: number, pageSize: number, configId?: number | null) {
  return useQuery({
    queryKey: queryKeys.extractionLogs(page, pageSize, configId),
    queryFn: () => getExtractionLogs(page, pageSize, configId),
  });
}

export function useAvailableModels() {
  return useQuery({
    queryKey: queryKeys.availableModels,
    queryFn: getAvailableModels,
  });
}

// Mutations
export function useUploadAndExtract() {
  return useMutation({
    mutationFn: async ({
      file,
      extractorConfigId,
    }: {
      file: File;
      extractorConfigId?: number | null;
    }) => {
      const { s3_key, filename } = await uploadFile(file);
      return extractFromFile(s3_key, filename, extractorConfigId);
    },
  });
}

export function useSubmitExtraction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SubmissionPayload) => submitExtraction(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["extractionLogs"] });
      queryClient.invalidateQueries({ queryKey: ["metrics"] });
      queryClient.invalidateQueries({ queryKey: ["apiCallMetrics"] });
    },
  });
}

export function useDeleteExtractorConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteExtractorConfig(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.extractorConfigs });
    },
  });
}

export function useCreateExtractorConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (config: {
      name: string;
      description?: string;
      prompt?: string;
      model?: string;
      output_schema?: Record<string, unknown>;
      is_default?: boolean;
      status?: string;
    }) => createExtractorConfig(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.extractorConfigs });
    },
  });
}

export function useUpdateExtractorConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      config,
    }: {
      id: number;
      config: {
        name?: string;
        description?: string;
        prompt?: string;
        model?: string;
        output_schema?: Record<string, unknown>;
        is_default?: boolean;
        status?: string;
      };
    }) => updateExtractorConfig(id, config),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.extractorConfigs });
      queryClient.invalidateQueries({ queryKey: queryKeys.extractorConfig(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.extractorVersions(id) });
    },
  });
}

export function useToggleVersionActive() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      configId,
      versionId,
      isActive,
    }: {
      configId: number;
      versionId: number;
      isActive: boolean;
    }) => toggleVersionActive(configId, versionId, isActive),
    onSuccess: (_, { configId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.extractorVersions(configId) });
    },
  });
}

export function useTestExtract() {
  return useMutation({
    mutationFn: async ({
      file,
      config,
      extractorConfigId,
    }: {
      file: File;
      config: { prompt: string; model: string; output_schema: Record<string, unknown> };
      extractorConfigId?: number | null;
    }) => {
      const { s3_key, filename } = await uploadFile(file);
      return testExtract(s3_key, filename, config, extractorConfigId);
    },
  });
}

export function useGenerateSchema() {
  return useMutation({
    mutationFn: (description: string) => generateSchema(description),
  });
}

export function useGeneratePrompt() {
  return useMutation({
    mutationFn: ({
      output_schema,
      document_type,
    }: {
      output_schema: Record<string, unknown>;
      document_type: string | null;
    }) => generatePrompt(output_schema, document_type),
  });
}

export function useUpdatePrompt() {
  return useMutation({
    mutationFn: ({
      current_prompt,
      instructions,
      output_schema,
    }: {
      current_prompt: string;
      instructions: string;
      output_schema: Record<string, unknown>;
    }) => updatePrompt(current_prompt, instructions, output_schema),
  });
}
