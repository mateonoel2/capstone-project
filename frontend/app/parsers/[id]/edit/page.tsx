"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { ParserConfigForm } from "@/components/parser-config-form";
import { VersionHistory } from "@/components/version-history";
import {
  getParserConfig,
  updateParserConfig,
  deleteParserConfig,
  ParserConfig,
} from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2, Star, Trash2, History } from "lucide-react";
import Link from "next/link";

export default function EditParserPage() {
  const params = useParams();
  const router = useRouter();
  const configId = Number(params.id);

  const [config, setConfig] = useState<ParserConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [formKey, setFormKey] = useState(0);
  const [showVersions, setShowVersions] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      const data = await getParserConfig(configId);
      setConfig(data);
    } catch (err) {
      console.error("Failed to fetch config:", err);
    } finally {
      setIsLoading(false);
    }
  }, [configId]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const handleUpdate = async (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => {
    await updateParserConfig(configId, data);
    router.push("/parsers");
  };

  const handleDelete = async () => {
    if (!confirm("¿Eliminar este parser?")) return;
    try {
      await deleteParserConfig(configId);
      router.push("/parsers");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al eliminar");
    }
  };

  const handleRestore = async () => {
    await fetchConfig();
    setFormKey((k) => k + 1);
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-600">Cargando parser...</span>
        </div>
      </main>
    );
  }

  if (!config) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          <p className="text-gray-600">Parser no encontrado.</p>
          <Link href="/parsers" className="text-blue-600 hover:underline text-sm mt-2 inline-block">
            Volver a Parsers
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <Link
            href="/parsers"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-3"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Volver a Parsers
          </Link>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">
                Editar: {config.name}
              </h1>
              {config.is_default && (
                <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
                  <Star className="h-3 w-3" />
                  Default
                </span>
              )}
            </div>
            {!config.is_default && (
              <Button
                variant="outline"
                className="text-red-600 hover:text-red-700"
                onClick={handleDelete}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Eliminar
              </Button>
            )}
          </div>
        </div>

        <Card className="mb-6">
          <CardContent className="pt-6">
            <ParserConfigForm
              key={formKey}
              initialData={config}
              onSave={handleUpdate}
              onCancel={() => router.push("/parsers")}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader
            className="cursor-pointer"
            onClick={() => setShowVersions(!showVersions)}
          >
            <div className="flex items-center gap-2">
              <History className="h-5 w-5 text-gray-500" />
              <CardTitle className="text-lg">Historial de versiones</CardTitle>
            </div>
          </CardHeader>
          {showVersions && (
            <CardContent className="pt-0">
              <VersionHistory configId={configId} onRestore={handleRestore} />
            </CardContent>
          )}
        </Card>
      </div>
    </main>
  );
}
