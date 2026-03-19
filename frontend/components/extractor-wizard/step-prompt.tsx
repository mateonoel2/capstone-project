"use client";

import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { SchemaSummary } from "./schema-summary";
import { PromptTips } from "./prompt-tips";
import { useT } from "@/lib/i18n";

interface StepPromptProps {
  prompt: string;
  schema: Record<string, unknown>;
  description: string;
  onChange: (prompt: string) => void;
}

export function StepPrompt({ prompt, schema, onChange }: StepPromptProps) {
  const t = useT();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        <Label htmlFor="wizard-prompt">{t("stepPrompt.label")}</Label>
        <Textarea
          id="wizard-prompt"
          value={prompt}
          onChange={(e) => onChange(e.target.value)}
          placeholder={t("stepPrompt.placeholder")}
          className="font-mono text-sm min-h-[350px]"
        />
        <PromptTips />
      </div>

      <div className="space-y-3">
        <Label>{t("stepPrompt.schemaFields")}</Label>
        <div className="border rounded-lg p-3 bg-gray-50">
          <SchemaSummary schema={schema} />
        </div>
        <p className="text-xs text-muted-foreground">
          {t("stepPrompt.schemaReference")}
        </p>
      </div>
    </div>
  );
}
