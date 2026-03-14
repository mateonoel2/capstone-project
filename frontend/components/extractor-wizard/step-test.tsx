"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { FileUpload } from "@/components/file-upload";
import { FileViewer } from "@/components/file-viewer";
import { DynamicFieldsForm } from "@/components/dynamic-fields-form";
import { Loader2, Play, Clock } from "lucide-react";
import { uploadFile, testExtract } from "@/lib/api";

interface StepTestProps {
  prompt: string;
  model: string;
  schema: Record<string, unknown>;
}

export function StepTest({ prompt, model, schema }: StepTestProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});

  const handleTest = async () => {
    if (!file) return;
    setIsExtracting(true);
    setError(null);
    setResult(null);
    try {
      const { s3_key, filename } = await uploadFile(file);
      const res = await testExtract(s3_key, filename, { prompt, model, output_schema: schema });
      setResult(res.fields);
      setResponseTime(res.response_time_ms);
      // Initialize form values from result
      const values: Record<string, string> = {};
      for (const [key, val] of Object.entries(res.fields)) {
        values[key] = String(val ?? "");
      }
      setFormValues(values);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error en la extracción");
    } finally {
      setIsExtracting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left: File upload + preview */}
      <div className="space-y-4">
        {!file ? (
          <FileUpload onFileSelect={setFile} isLoading={isExtracting} />
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
                  setResult(null);
                  setError(null);
                  setResponseTime(null);
                }}
              >
                Cambiar archivo
              </Button>
            </div>
            <div className="h-[400px] overflow-hidden rounded-lg border">
              <FileViewer file={file} />
            </div>
            <Button
              type="button"
              onClick={handleTest}
              disabled={isExtracting}
              className="w-full"
            >
              {isExtracting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Extrayendo...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Ejecutar extracción
                </>
              )}
            </Button>
          </div>
        )}
      </div>

      {/* Right: Results */}
      <div className="space-y-4">
        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded">
            {error}
          </div>
        )}
        {result && (
          <>
            {responseTime !== null && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                {responseTime.toFixed(0)} ms
              </div>
            )}
            <div className="border rounded-lg p-4">
              <DynamicFieldsForm
                schema={schema}
                values={formValues}
                extracted={result}
                onChange={(field, value) =>
                  setFormValues((prev) => ({ ...prev, [field]: value }))
                }
              />
            </div>
          </>
        )}
        {!result && !error && (
          <div className="flex items-center justify-center h-64 border border-dashed rounded-lg text-sm text-muted-foreground">
            Sube un archivo y ejecuta la extracción para ver los resultados
          </div>
        )}
      </div>
    </div>
  );
}
