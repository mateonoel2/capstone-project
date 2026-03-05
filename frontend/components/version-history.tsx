"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  getParserVersions,
  updateParserConfig,
  ParserConfigVersion,
} from "@/lib/api";
import { Loader2, RotateCcw } from "lucide-react";

interface VersionHistoryProps {
  configId: number;
  onRestore?: () => void;
}

export function VersionHistory({ configId, onRestore }: VersionHistoryProps) {
  const [versions, setVersions] = useState<ParserConfigVersion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [restoringId, setRestoringId] = useState<number | null>(null);

  useEffect(() => {
    setIsLoading(true);
    getParserVersions(configId)
      .then(setVersions)
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, [configId]);

  const handleRestore = async (version: ParserConfigVersion) => {
    setRestoringId(version.id);
    try {
      await updateParserConfig(configId, {
        prompt: version.prompt,
        model: version.model,
        output_schema: version.output_schema,
      });
      onRestore?.();
    } catch (err) {
      console.error("Failed to restore version:", err);
    } finally {
      setRestoringId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (versions.length === 0) {
    return (
      <p className="text-sm text-gray-500 py-4">
        No hay versiones anteriores.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {versions.map((version) => (
        <Card
          key={version.id}
          className="cursor-pointer"
          onClick={() =>
            setExpandedId(expandedId === version.id ? null : version.id)
          }
        >
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm">
                  Versión {version.version_number}
                </CardTitle>
                <CardDescription className="text-xs">
                  {version.created_at
                    ? new Date(version.created_at).toLocaleString()
                    : ""}
                  {" · "}
                  Modelo: {version.model}
                </CardDescription>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRestore(version);
                }}
                disabled={restoringId === version.id}
              >
                {restoringId === version.id ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <>
                    <RotateCcw className="h-3 w-3 mr-1" />
                    Restaurar
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          {expandedId === version.id && (
            <CardContent className="pt-0 px-4 pb-3">
              <div className="space-y-2">
                <div>
                  <p className="text-xs font-medium text-gray-500">Prompt</p>
                  <pre className="text-xs bg-gray-50 p-2 rounded max-h-32 overflow-auto whitespace-pre-wrap">
                    {version.prompt}
                  </pre>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500">Schema</p>
                  <pre className="text-xs bg-gray-50 p-2 rounded max-h-32 overflow-auto">
                    {JSON.stringify(version.output_schema, null, 2)}
                  </pre>
                </div>
              </div>
            </CardContent>
          )}
        </Card>
      ))}
    </div>
  );
}
