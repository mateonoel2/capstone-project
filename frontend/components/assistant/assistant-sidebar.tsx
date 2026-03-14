"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Sparkles, X } from "lucide-react";
import { useGenerateSchema, useGeneratePrompt, useUpdatePrompt } from "@/lib/hooks";

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
      // Update existing prompt
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
      // Generate from scratch using instructions as document_type context
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
      {/* Backdrop */}
      {isVisible && (
        <div
          className="fixed inset-0 z-40 bg-black/20 transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed top-0 right-0 z-50 h-full w-[360px] max-w-[90vw] bg-white border-l shadow-xl transition-transform duration-300 ease-in-out ${
          isVisible ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            <span className="font-semibold text-blue-900">Asistente IA</span>
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

        {/* Content */}
        <div className="overflow-y-auto p-5 h-[calc(100%-57px)]">
          {mode === "schema" && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">
                  Generar campos con IA
                </p>
                <p className="text-xs text-muted-foreground mb-3">
                  Describe el tipo de documento y los campos que necesitas extraer.
                </p>
              </div>
              <Textarea
                value={schemaDescription}
                onChange={(e) => setSchemaDescription(e.target.value)}
                placeholder="Ej: Necesito extraer el RFC, razon social, total, subtotal y fecha de emision de facturas CFDI mexicanas"
                className="min-h-[120px] bg-white text-sm"
              />
              {generateSchema.error && (
                <p className="text-xs text-red-600">
                  {generateSchema.error instanceof Error
                    ? generateSchema.error.message
                    : "Error al generar schema"}
                </p>
              )}
              <Button
                size="sm"
                className="w-full"
                onClick={handleGenerateSchema}
                disabled={generateSchema.isPending || !schemaDescription.trim()}
              >
                {generateSchema.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                    Generando...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-1" />
                    Generar campos
                  </>
                )}
              </Button>
            </div>
          )}

          {mode === "prompt" && (
            <div className="space-y-4">
              {!hasSchemaFields && (
                <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                  Define campos en el esquema primero.
                </p>
              )}

              {/* One-click generate from schema fields */}
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">
                  Generar desde campos
                </p>
                <p className="text-xs text-muted-foreground">
                  Genera un prompt automaticamente basado en los campos del esquema.
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
                  disabled={isPromptPending || !hasSchemaFields}
                >
                  {generatePrompt.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      Generando...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-1" />
                      Generar prompt
                    </>
                  )}
                </Button>
              </div>

              {/* Divider */}
              <div className="relative py-1">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-muted-foreground">o</span>
                </div>
              </div>

              {/* Update with instructions */}
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">
                  {hasPrompt ? "Actualizar con instrucciones" : "Generar con contexto"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {hasPrompt
                    ? "Describe los cambios que quieres hacer al prompt actual."
                    : "Describe el tipo de documento para un prompt mas preciso."}
                </p>
                <Textarea
                  value={promptInstructions}
                  onChange={(e) => setPromptInstructions(e.target.value)}
                  placeholder={
                    hasPrompt
                      ? "Ej: Agrega instrucciones para manejar documentos escaneados con baja calidad"
                      : "Ej: Es un estado de cuenta bancario mexicano en formato PDF"
                  }
                  className="min-h-[100px] bg-white text-sm"
                  disabled={!hasSchemaFields}
                />
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full"
                  onClick={handlePromptAction}
                  disabled={isPromptPending || !promptInstructions.trim() || !hasSchemaFields}
                >
                  {updatePromptMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      Actualizando...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-1" />
                      {hasPrompt ? "Actualizar prompt" : "Generar prompt"}
                    </>
                  )}
                </Button>
              </div>

              {promptError && (
                <p className="text-xs text-red-600">
                  {promptError instanceof Error
                    ? promptError.message
                    : "Error al generar prompt"}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
