import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useExtractionStore } from "@/lib/store";
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
  getApiTokens,
  createApiToken,
  revokeApiToken,
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  getUsageQuota,
  SubmissionPayload,
} from "@/lib/api";

// Query keys
export const queryKeys = {
  banks: ["banks"] as const,
  extractorConfigs: ["extractorConfigs"] as const,
  extractorConfig: (id: string) => ["extractorConfig", id] as const,
  extractorVersions: (id: string) => ["extractorVersions", id] as const,
  metrics: (configId?: string | null) => ["metrics", configId] as const,
  apiCallMetrics: (configId?: string | null) => ["apiCallMetrics", configId] as const,
  extractionLogs: (page: number, pageSize: number, configId?: string | null) =>
    ["extractionLogs", page, pageSize, configId] as const,
  availableModels: ["availableModels"] as const,
  apiTokens: ["apiTokens"] as const,
  users: ["users"] as const,
  usageQuota: ["usageQuota"] as const,
};

function useIsAuthenticated() {
  return !!useExtractionStore((s) => s.backendToken);
}

// Queries
export function useBanks() {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.banks,
    queryFn: getBanks,
    enabled: authed,
  });
}

export function useExtractorConfigs(status?: string) {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: [...queryKeys.extractorConfigs, status],
    queryFn: () => getExtractorConfigs(status),
    enabled: authed,
  });
}

export function useExtractorConfig(id: string, options?: { enabled?: boolean }) {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.extractorConfig(id),
    queryFn: () => getExtractorConfig(id),
    enabled: authed && (options?.enabled ?? true),
  });
}

export function useExtractorVersions(configId: string) {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.extractorVersions(configId),
    queryFn: () => getExtractorVersions(configId),
    enabled: authed,
  });
}

export function useMetrics(configId?: string | null) {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.metrics(configId),
    queryFn: () => getMetrics(configId),
    enabled: authed,
  });
}

export function useApiCallMetrics(configId?: string | null) {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.apiCallMetrics(configId),
    queryFn: () => getApiCallMetrics(configId),
    enabled: authed,
  });
}

export function useExtractionLogs(page: number, pageSize: number, configId?: string | null) {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.extractionLogs(page, pageSize, configId),
    queryFn: () => getExtractionLogs(page, pageSize, configId),
    enabled: authed,
  });
}

export function useAvailableModels() {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.availableModels,
    queryFn: getAvailableModels,
    enabled: authed,
  });
}

export function useUsageQuota() {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.usageQuota,
    queryFn: getUsageQuota,
    enabled: authed,
  });
}

// Mutations
export function useUploadFile() {
  return useMutation({
    mutationFn: (file: File) => uploadFile(file),
  });
}

export function useExtract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      s3Key,
      filename,
      extractorConfigId,
    }: {
      s3Key: string;
      filename: string;
      extractorConfigId?: string | null;
    }) => {
      return extractFromFile(s3Key, filename, extractorConfigId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.usageQuota });
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
    mutationFn: (id: string) => deleteExtractorConfig(id),
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
      queryClient.invalidateQueries({ queryKey: queryKeys.usageQuota });
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
      id: string;
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
      configId: string;
      versionId: string;
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
      extractorConfigId?: string | null;
    }) => {
      const { s3_key, filename } = await uploadFile(file);
      return testExtract(s3_key, filename, config, extractorConfigId);
    },
  });
}

export function useGenerateSchema() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (description: string) => generateSchema(description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.usageQuota });
    },
  });
}

export function useGeneratePrompt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      output_schema,
      document_type,
    }: {
      output_schema: Record<string, unknown>;
      document_type: string | null;
    }) => generatePrompt(output_schema, document_type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.usageQuota });
    },
  });
}

export function useUpdatePrompt() {
  const queryClient = useQueryClient();
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.usageQuota });
    },
  });
}

// API Token hooks
export function useApiTokens() {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.apiTokens,
    queryFn: getApiTokens,
    enabled: authed,
  });
}

export function useCreateApiToken() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ name, expires_at }: { name: string; expires_at?: string | null }) =>
      createApiToken(name, expires_at),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.apiTokens });
    },
  });
}

export function useRevokeApiToken() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => revokeApiToken(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.apiTokens });
    },
  });
}

// Admin hooks
export function useUsers() {
  const authed = useIsAuthenticated();
  return useQuery({
    queryKey: queryKeys.users,
    queryFn: getUsers,
    enabled: authed,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ github_username, role }: { github_username: string; role: string }) =>
      createUser(github_username, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { role?: string; is_active?: boolean } }) =>
      updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
    },
  });
}
