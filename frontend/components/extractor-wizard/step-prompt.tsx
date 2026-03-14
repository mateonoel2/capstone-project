"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Sparkles } from "lucide-react";
import { useGeneratePrompt } from "@/lib/hooks";
import { SchemaSummary } from "./schema-summary";
import { PromptTips } from "./prompt-tips";

interface StepPromptProps {
  prompt: string;
  schema: Record<string, unknown>;
  description: string;
  onChange: (prompt: string) => void;
}

export function StepPrompt({ prompt, schema, description, onChange }: StepPromptProps) {
  const generateMutation = useGeneratePrompt();

  const handleGenerate = async () => {
    if (prompt.trim()) {
      if (!confirm("El prompt actual será reemplazado. ¿Continuar?")) return;
    }
    generateMutation.mutate(
      { output_schema: schema, document_type: description || null },
      {
        onSuccess: (result) => {
          onChange(result.prompt);
        },
      }
    );
  };

  const hasSchemaFields = Object.keys(
    (schema as { properties?: Record<string, unknown> })?.properties || {}
  ).filter((k) => k !== "is_bank_statement").length > 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main: Prompt editor */}
      <div className="lg:col-span-2 space-y-4">
        <div className="flex items-center justify-between">
          <Label htmlFor="wizard-prompt">Prompt de extracción *</Label>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={handleGenerate}
            disabled={generateMutation.isPending || !hasSchemaFields}
            title={!hasSchemaFields ? "Define campos en el schema primero" : ""}
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                Generando...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-1" />
                Generar desde esquema
              </>
            )}
          </Button>
        </div>
        <Textarea
          id="wizard-prompt"
          value={prompt}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Escribe las instrucciones para extraer datos del documento..."
          className="font-mono text-sm min-h-[350px]"
        />
        {generateMutation.error && (
          <p className="text-xs text-red-600">
            {generateMutation.error instanceof Error ? generateMutation.error.message : "Error al generar prompt"}
          </p>
        )}
        <PromptTips />
      </div>

      {/* Sidebar: Schema summary */}
      <div className="space-y-3">
        <Label>Campos del esquema</Label>
        <div className="border rounded-lg p-3 bg-gray-50">
          <SchemaSummary schema={schema} />
        </div>
        <p className="text-xs text-muted-foreground">
          Referencia de los campos definidos en el paso anterior
        </p>
      </div>
    </div>
  );
}
