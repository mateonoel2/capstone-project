"use client";

import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { SchemaSummary } from "./schema-summary";
import { PromptTips } from "./prompt-tips";

interface StepPromptProps {
  prompt: string;
  schema: Record<string, unknown>;
  description: string;
  onChange: (prompt: string) => void;
}

export function StepPrompt({ prompt, schema, onChange }: StepPromptProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main: Prompt editor */}
      <div className="lg:col-span-2 space-y-4">
        <Label htmlFor="wizard-prompt">Prompt de extraccion *</Label>
        <Textarea
          id="wizard-prompt"
          value={prompt}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Escribe las instrucciones para extraer datos del documento..."
          className="font-mono text-sm min-h-[350px]"
        />
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
