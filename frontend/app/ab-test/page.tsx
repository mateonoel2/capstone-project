"use client";

import { useState, useEffect } from "react";
import { FileUpload } from "@/components/file-upload";
import { ABResults } from "@/components/ab-results";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  getParserConfigs,
  runABTest,
  ParserConfig,
  ABTestResultItem,
} from "@/lib/api";
import { Loader2, AlertCircle } from "lucide-react";

export default function ABTestPage() {
  const [configs, setConfigs] = useState<ParserConfig[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<ABTestResultItem[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTesting, setIsTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getParserConfigs()
      .then((data) => {
        setConfigs(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  const toggleConfig = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    setResults(null);
  };

  const handleRunTest = async () => {
    if (!file || selectedIds.length < 2) return;

    setIsTesting(true);
    setError(null);
    setResults(null);

    try {
      const testResults = await runABTest(file, selectedIds);
      setResults(testResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error en la prueba A/B");
    } finally {
      setIsTesting(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResults(null);
    setError(null);
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Prueba A/B</h1>
          <p className="text-gray-600 mt-1">
            Compara la extracción de múltiples parsers sobre el mismo documento
          </p>
        </div>

        {/* Step 1: Select configs */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">
              1. Seleccionar Parsers (mín. 2, máx. 4)
            </CardTitle>
            <CardDescription>
              Seleccionados: {selectedIds.length}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {configs.map((config) => {
                const isSelected = selectedIds.includes(config.id);
                const isDisabled =
                  !isSelected && selectedIds.length >= 4;

                return (
                  <button
                    key={config.id}
                    onClick={() => !isDisabled && toggleConfig(config.id)}
                    disabled={isDisabled}
                    className={`text-left p-3 rounded-lg border-2 transition-colors ${
                      isSelected
                        ? "border-blue-500 bg-blue-50"
                        : isDisabled
                          ? "border-gray-200 bg-gray-100 opacity-50 cursor-not-allowed"
                          : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">
                        {config.name}
                      </span>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                        {config.model}
                      </span>
                    </div>
                    {config.description && (
                      <p className="text-xs text-gray-500 mt-1">
                        {config.description}
                      </p>
                    )}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Step 2: Upload file */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">2. Subir Documento</CardTitle>
          </CardHeader>
          <CardContent>
            {file ? (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{file.name}</span>
                <Button variant="outline" size="sm" onClick={handleReset}>
                  Cambiar archivo
                </Button>
              </div>
            ) : (
              <FileUpload onFileSelect={handleFileSelect} isLoading={false} />
            )}
          </CardContent>
        </Card>

        {/* Run test button */}
        <div className="mb-6">
          <Button
            onClick={handleRunTest}
            disabled={
              selectedIds.length < 2 || !file || isTesting
            }
            className="w-full"
            size="lg"
          >
            {isTesting ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Ejecutando prueba A/B...
              </>
            ) : (
              `Ejecutar Prueba A/B (${selectedIds.length} parsers)`
            )}
          </Button>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-start gap-3 text-red-600 bg-red-50 p-4 rounded-lg mb-6">
            <AlertCircle className="h-5 w-5 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">3. Resultados</CardTitle>
              <CardDescription>
                Comparación de extracción entre parsers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ABResults results={results} />
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  );
}
