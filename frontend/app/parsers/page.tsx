"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  getParserConfigs,
  deleteParserConfig,
  ParserConfig,
} from "@/lib/api";
import { Loader2, Plus, Trash2, Star } from "lucide-react";
import Link from "next/link";

export default function ParsersPage() {
  const [configs, setConfigs] = useState<ParserConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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
          <Button asChild>
            <Link href="/parsers/new">
              <Plus className="h-4 w-4 mr-2" />
              Crear Parser
            </Link>
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
                    <Button size="sm" variant="outline" asChild>
                      <Link href={`/parsers/${config.id}/edit`}>Editar</Link>
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
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}
