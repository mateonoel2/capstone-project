"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2, Sparkles } from "lucide-react";
import { SchemaBuilder } from "@/components/schema-builder/schema-builder";
import { useGenerateSchema } from "@/lib/hooks";

interface StepSchemaProps {
  schema: Record<string, unknown>;
  onChange: (schema: Record<string, unknown>) => void;
  isNew?: boolean;
}

export function StepSchema({ schema, onChange, isNew }: StepSchemaProps) {
  const [aiDescription, setAiDescription] = useState("");
  const generateMutation = useGenerateSchema();

  const handleGenerate = async () => {
    if (!aiDescription.trim()) return;
    generateMutation.mutate(aiDescription.trim(), {
      onSuccess: (result) => {
        onChange(result.output_schema);
      },
    });
  };

  return (
    <div className="space-y-6">
      {/* AI Generation Panel */}
      <div className="border rounded-lg p-4 bg-blue-50/50 space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-blue-600" />
          <Label className="text-blue-900 font-medium">Generar campos con IA</Label>
        </div>
        <Textarea
          value={aiDescription}
          onChange={(e) => setAiDescription(e.target.value)}
          placeholder="Describe los campos que necesitas extraer. Ej: 'Necesito extraer el RFC, razon social, total, subtotal y fecha de emision de facturas CFDI mexicanas'"
          className="min-h-[80px] bg-white"
        />
        {generateMutation.error && (
          <p className="text-xs text-red-600">
            {generateMutation.error instanceof Error ? generateMutation.error.message : "Error al generar schema"}
          </p>
        )}
        <Button
          type="button"
          size="sm"
          onClick={handleGenerate}
          disabled={generateMutation.isPending || !aiDescription.trim()}
        >
          {generateMutation.isPending ? (
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

      {/* Schema Builder */}
      <SchemaBuilder value={schema} onChange={onChange} isNew={isNew} />
    </div>
  );
}
