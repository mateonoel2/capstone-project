"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Sparkles, X } from "lucide-react";
import { useGenerateSchema, useGeneratePrompt, useUpdatePrompt, useUsageQuota } from "@/lib/hooks";
import { useT } from "@/lib/i18n";

export type AssistantMode = "schema" | "prompt" | null;

interface AssistantSidebarProps {
  mode: AssistantMode;
  open: boolean;
  onClose: () => void;
  onSchemaGenerated: (schema: Record<string, unknown>) => void;
  onPromptGenerated: (prompt: string) => void;
  schema: Record<string, unknown>;
  currentPrompt: string;
}

export function AssistantSidebar({
  mode,
  open,
  onClose,
  onSchemaGenerated,
  onPromptGenerated,
  schema,
  currentPrompt,
}: AssistantSidebarProps) {
  const [schemaDescription, setSchemaDescription] = useState("");
  const [promptInstructions, setPromptInstructions] = useState("");
  const generateSchema = useGenerateSchema();
  const generatePrompt = useGeneratePrompt();
  const updatePromptMutation = useUpdatePrompt();
  const { data: quota } = useUsageQuota();
  const t = useT();

  const aiLimitReached = !!(
    quota &&
    !quota.unlimited &&
    quota.ai_prompts &&
    quota.ai_prompts.used >= quota.ai_prompts.limit
  );

  const handleGenerateSchema = () => {
    if (!schemaDescription.trim()) return;
    generateSchema.mutate(schemaDescription.trim(), {
      onSuccess: (result) => {
        onSchemaGenerated(result.output_schema);
        setSchemaDescription("");
      },
    });
  };

  const handlePromptAction = () => {
    const instructions = promptInstructions.trim();
    if (!instructions) return;

    if (currentPrompt.trim()) {
      updatePromptMutation.mutate(
        {
          current_prompt: currentPrompt,
          instructions,
          output_schema: schema,
        },
        {
          onSuccess: (result) => {
            onPromptGenerated(result.prompt);
            setPromptInstructions("");
          },
        }
      );
    } else {
      generatePrompt.mutate(
        { output_schema: schema, document_type: instructions },
        {
          onSuccess: (result) => {
            onPromptGenerated(result.prompt);
            setPromptInstructions("");
          },
        }
      );
    }
  };

  const hasSchemaFields =
    Object.keys(
      (schema as { properties?: Record<string, unknown> })?.properties || {}
    ).filter((k) => k !== "is_valid_document").length > 0;

  const isPromptPending = generatePrompt.isPending || updatePromptMutation.isPending;
  const promptError = generatePrompt.error || updatePromptMutation.error;
  const hasPrompt = !!currentPrompt.trim();
  const isVisible = open && mode;

  return (
    <>
      {isVisible && (
        <div
          className="fixed inset-0 z-40 bg-black/20 transition-opacity"
          onClick={onClose}
        />
      )}

      <div
        className={`fixed top-0 right-0 z-50 h-full w-[360px] max-w-[90vw] bg-white border-l shadow-xl transition-transform duration-300 ease-in-out ${
          isVisible ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            <span className="font-semibold text-blue-900">{t("assistant.title")}</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="overflow-y-auto p-5 h-[calc(100%-57px)]">
          {mode === "schema" && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">
                  {t("assistant.generateFieldsTitle")}
                </p>
                <p className="text-xs text-muted-foreground mb-3">
                  {t("assistant.generateFieldsDesc")}
                </p>
              </div>
              <Textarea
                value={schemaDescription}
                onChange={(e) => setSchemaDescription(e.target.value)}
                placeholder={t("assistant.generateFieldsPlaceholder")}
                className="min-h-[120px] bg-white text-sm"
              />
              {generateSchema.error && (
                <p className="text-xs text-red-600">
                  {generateSchema.error instanceof Error
                    ? generateSchema.error.message
                    : t("assistant.schemaError")}
                </p>
              )}
              <Button
                size="sm"
                className="w-full"
                onClick={handleGenerateSchema}
                disabled={generateSchema.isPending || !schemaDescription.trim() || aiLimitReached}
              >
                {generateSchema.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                    {t("assistant.generating")}
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-1" />
                    {t("assistant.generateFields")}
                  </>
                )}
              </Button>
            </div>
          )}

          {mode === "prompt" && (
            <div className="space-y-4">
              {!hasSchemaFields && (
                <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                  {t("assistant.defineSchemaFirst")}
                </p>
              )}

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">
                  {t("assistant.generateFromFields")}
                </p>
                <p className="text-xs text-muted-foreground">
                  {t("assistant.generateFromFieldsDesc")}
                </p>
                <Button
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    generatePrompt.mutate(
                      { output_schema: schema, document_type: null },
                      {
                        onSuccess: (result) => onPromptGenerated(result.prompt),
                      }
                    );
                  }}
                  disabled={isPromptPending || !hasSchemaFields || aiLimitReached}
                >
                  {generatePrompt.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      {t("assistant.generating")}
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-1" />
                      {t("assistant.generatePrompt")}
                    </>
                  )}
                </Button>
              </div>

              <div className="relative py-1">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-muted-foreground">{t("assistant.or")}</span>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">
                  {hasPrompt ? t("assistant.updateWithInstructions") : t("assistant.generateWithContext")}
                </p>
                <p className="text-xs text-muted-foreground">
                  {hasPrompt
                    ? t("assistant.updatePromptDesc")
                    : t("assistant.generatePromptDesc")}
                </p>
                <Textarea
                  value={promptInstructions}
                  onChange={(e) => setPromptInstructions(e.target.value)}
                  placeholder={
                    hasPrompt
                      ? t("assistant.updatePlaceholder")
                      : t("assistant.generatePlaceholder")
                  }
                  className="min-h-[100px] bg-white text-sm"
                  disabled={!hasSchemaFields}
                />
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full"
                  onClick={handlePromptAction}
                  disabled={isPromptPending || !promptInstructions.trim() || !hasSchemaFields || aiLimitReached}
                >
                  {updatePromptMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      {t("assistant.updating")}
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-1" />
                      {hasPrompt ? t("assistant.updatePrompt") : t("assistant.generatePrompt")}
                    </>
                  )}
                </Button>
              </div>

              {promptError && (
                <p className="text-xs text-red-600">
                  {promptError instanceof Error
                    ? promptError.message
                    : t("assistant.promptError")}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
