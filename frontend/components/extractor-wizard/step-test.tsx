"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { FileUpload } from "@/components/file-upload";
import { FileViewer } from "@/components/file-viewer";
import { DynamicFieldsForm } from "@/components/dynamic-fields-form";
import { Loader2, Play, Clock } from "lucide-react";
import { useTestExtract } from "@/lib/hooks";
import { useT } from "@/lib/i18n";

interface StepTestProps {
  prompt: string;
  model: string;
  schema: Record<string, unknown>;
  extractorConfigId?: string | null;
}

export function StepTest({ prompt, model, schema, extractorConfigId }: StepTestProps) {
  const [file, setFile] = useState<File | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const testMutation = useTestExtract();
  const t = useT();

  const handleTest = async () => {
    if (!file) return;
    testMutation.mutate(
      { file, config: { prompt, model, output_schema: schema }, extractorConfigId },
      {
        onSuccess: (res) => {
          const values: Record<string, string> = {};
          for (const [key, val] of Object.entries(res.fields)) {
            values[key] = String(val ?? "");
          }
          setFormValues(values);
        },
      }
    );
  };

  const result = testMutation.data;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="space-y-4">
        {!file ? (
          <FileUpload onFileSelect={setFile} isLoading={testMutation.isPending} />
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-700 truncate">
                {file.name}
              </p>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => {
                  setFile(null);
                  testMutation.reset();
                }}
              >
                {t("stepTest.changeFile")}
              </Button>
            </div>
            <div className="h-[400px] overflow-hidden rounded-lg border">
              <FileViewer file={file} />
            </div>
            <Button
              type="button"
              onClick={handleTest}
              disabled={testMutation.isPending}
              className="w-full"
            >
              {testMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {t("stepTest.extracting")}
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  {t("stepTest.runExtraction")}
                </>
              )}
            </Button>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {testMutation.error && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded">
            {testMutation.error instanceof Error ? testMutation.error.message : t("stepTest.extractionError")}
          </div>
        )}
        {result && (
          <>
            {result.response_time_ms !== null && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                {result.response_time_ms.toFixed(0)} ms
              </div>
            )}
            <div className="border rounded-lg p-4">
              <DynamicFieldsForm
                schema={schema}
                values={formValues}
                extracted={result.fields}
                onChange={(field, value) =>
                  setFormValues((prev) => ({ ...prev, [field]: value }))
                }
              />
            </div>
          </>
        )}
        {!result && !testMutation.error && (
          <div className="flex items-center justify-center h-64 border border-dashed rounded-lg text-sm text-muted-foreground">
            {t("stepTest.placeholder")}
          </div>
        )}
      </div>
    </div>
  );
}
