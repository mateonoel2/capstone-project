"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useExtractorVersions, useUpdateExtractorConfig, useToggleVersionActive } from "@/lib/hooks";
import { Loader2, RotateCcw } from "lucide-react";
import { useT } from "@/lib/i18n";

interface VersionHistoryProps {
  configId: number;
  onRestore?: () => void;
}

export function VersionHistory({ configId, onRestore }: VersionHistoryProps) {
  const { data: versions = [], isLoading } = useExtractorVersions(configId);
  const updateMutation = useUpdateExtractorConfig();
  const toggleMutation = useToggleVersionActive();
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const t = useT();

  const handleRestore = async (version: typeof versions[number]) => {
    try {
      await updateMutation.mutateAsync({
        id: configId,
        config: {
          prompt: version.prompt,
          model: version.model,
          output_schema: version.output_schema,
        },
      });
      onRestore?.();
    } catch (err) {
      console.error("Failed to restore version:", err);
    }
  };

  const handleToggleActive = async (version: typeof versions[number]) => {
    try {
      await toggleMutation.mutateAsync({
        configId,
        versionId: version.id,
        isActive: !version.is_active,
      });
    } catch (err) {
      alert(err instanceof Error ? err.message : t("versionHistory.toggleError"));
    }
  };

  const activeVersions = versions.filter((v) => v.is_active);
  const totalVariants = activeVersions.length + 1;
  const pct = Math.round(100 / totalVariants);

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
        {t("versionHistory.noVersions")}
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {activeVersions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <p className="font-medium mb-1">{t("versionHistory.trafficDistribution")}</p>
          <p>
            {t("versionHistory.current")} ({pct}%)
            {activeVersions.map((v) => (
              <span key={v.id}>, {t("versionHistory.version", { number: String(v.version_number) })} ({pct}%)</span>
            ))}
          </p>
        </div>
      )}

      {versions.map((version) => (
        <Card
          key={version.id}
          className={`cursor-pointer ${version.is_active ? "border-green-300 bg-green-50/30" : ""}`}
          onClick={() =>
            setExpandedId(expandedId === version.id ? null : version.id)
          }
        >
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm">
                  {t("versionHistory.version", { number: String(version.version_number) })}
                  {version.is_active && (
                    <span className="ml-2 text-xs font-normal text-green-700 bg-green-100 px-1.5 py-0.5 rounded">
                      {t("versionHistory.active")}
                    </span>
                  )}
                </CardTitle>
                <CardDescription className="text-xs">
                  {version.created_at
                    ? new Date(version.created_at).toLocaleString()
                    : ""}
                  {" · "}
                  {t("versionHistory.model", { name: version.model })}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant={version.is_active ? "default" : "outline"}
                  className={
                    version.is_active
                      ? "bg-green-600 hover:bg-green-700 text-white"
                      : ""
                  }
                  onClick={(e) => {
                    e.stopPropagation();
                    handleToggleActive(version);
                  }}
                  disabled={toggleMutation.isPending}
                >
                  {toggleMutation.isPending ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : version.is_active ? (
                    t("versionHistory.deactivate")
                  ) : (
                    t("versionHistory.activateAB")
                  )}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRestore(version);
                  }}
                  disabled={updateMutation.isPending}
                >
                  {updateMutation.isPending ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <>
                      <RotateCcw className="h-3 w-3 mr-1" />
                      {t("versionHistory.restore")}
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardHeader>
          {expandedId === version.id && (
            <CardContent className="pt-0 px-4 pb-3">
              <div className="space-y-2">
                <div>
                  <p className="text-xs font-medium text-gray-500">{t("versionHistory.prompt")}</p>
                  <pre className="text-xs bg-gray-50 p-2 rounded max-h-32 overflow-auto whitespace-pre-wrap">
                    {version.prompt}
                  </pre>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500">{t("versionHistory.schema")}</p>
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
