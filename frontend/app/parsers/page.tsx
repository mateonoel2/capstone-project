"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ParserConfigForm } from "@/components/parser-config-form";
import { VersionHistory } from "@/components/version-history";
import {
  getParserConfigs,
  createParserConfig,
  updateParserConfig,
  deleteParserConfig,
  ParserConfig,
} from "@/lib/api";
import { Loader2, Plus, Trash2, Star, History } from "lucide-react";

export default function ParsersPage() {
  const [configs, setConfigs] = useState<ParserConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editingConfig, setEditingConfig] = useState<ParserConfig | null>(null);
  const [showVersions, setShowVersions] = useState<number | null>(null);

  const fetchConfigs = useCallback(async () => {
    try {
      const data = await getParserConfigs();
      setConfigs(data);
    } catch (err) {
      console.error("Failed to fetch configs:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfigs();
  }, [fetchConfigs]);

  const handleCreate = async (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => {
    await createParserConfig(data);
    setShowCreate(false);
    fetchConfigs();
  };

  const handleUpdate = async (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => {
    if (!editingConfig) return;
    await updateParserConfig(editingConfig.id, data);
    setEditingConfig(null);
    fetchConfigs();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("¿Eliminar este parser?")) return;
    try {
      await deleteParserConfig(id);
      fetchConfigs();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al eliminar");
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-600">Cargando parsers...</span>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Parsers</h1>
            <p className="text-gray-600 mt-1">
              Configura parsers con prompts, modelos y esquemas personalizados
            </p>
          </div>
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Crear Parser
          </Button>
        </div>

        <div className="grid gap-4">
          {configs.map((config) => (
            <Card key={config.id}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-lg">{config.name}</CardTitle>
                    {config.is_default && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
                        <Star className="h-3 w-3" />
                        Default
                      </span>
                    )}
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                      {config.model}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowVersions(showVersions === config.id ? null : config.id)}
                    >
                      <History className="h-4 w-4 mr-1" />
                      Versiones
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingConfig(config)}
                    >
                      Editar
                    </Button>
                    {!config.is_default && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleDelete(config.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
                {config.description && (
                  <CardDescription>{config.description}</CardDescription>
                )}
              </CardHeader>
              {showVersions === config.id && (
                <CardContent className="pt-0">
                  <div className="border-t pt-3">
                    <h4 className="text-sm font-medium mb-2">
                      Historial de versiones
                    </h4>
                    <VersionHistory
                      configId={config.id}
                      onRestore={fetchConfigs}
                    />
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>

        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Crear Parser</DialogTitle>
            </DialogHeader>
            <ParserConfigForm
              onSave={handleCreate}
              onCancel={() => setShowCreate(false)}
            />
          </DialogContent>
        </Dialog>

        <Dialog
          open={editingConfig !== null}
          onOpenChange={(open) => {
            if (!open) setEditingConfig(null);
          }}
        >
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Editar Parser</DialogTitle>
            </DialogHeader>
            {editingConfig && (
              <ParserConfigForm
                initialData={editingConfig}
                onSave={handleUpdate}
                onCancel={() => setEditingConfig(null)}
              />
            )}
          </DialogContent>
        </Dialog>
      </div>
    </main>
  );
}
