"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useExtractorConfigs, useDeleteExtractorConfig, useUsageQuota } from "@/lib/hooks";
import { Loader2, Plus, Trash2, Star, PenLine } from "lucide-react";
import Link from "next/link";
import { useT } from "@/lib/i18n";

export default function ExtractorsPage() {
  const { data: configs = [], isLoading } = useExtractorConfigs();
  const deleteMutation = useDeleteExtractorConfig();
  const { data: quota } = useUsageQuota();
  const t = useT();

  const extractorLimitReached = !!(
    quota &&
    !quota.unlimited &&
    quota.extractors &&
    quota.extractors.used >= quota.extractors.limit
  );

  const handleDelete = async (id: number) => {
    if (!confirm(t("extractors.confirmDelete"))) return;
    try {
      await deleteMutation.mutateAsync(id);
    } catch (err) {
      alert(err instanceof Error ? err.message : t("extractors.deleteError"));
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-600">{t("extractors.loading")}</span>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t("extractors.title")}</h1>
            <p className="text-gray-600 mt-1">
              {t("extractors.subtitle")}
            </p>
          </div>
          {extractorLimitReached ? (
            <Button disabled title={t("quota.limitReached")}>
              <Plus className="h-4 w-4 mr-2" />
              {t("extractors.create")}
            </Button>
          ) : (
            <Button asChild>
              <Link href="/extractors/new">
                <Plus className="h-4 w-4 mr-2" />
                {t("extractors.create")}
              </Link>
            </Button>
          )}
        </div>

        <div className="grid gap-4">
          {configs.map((config) => {
            const isDraft = config.status === "draft";
            const href = isDraft
              ? `/extractors/new?draft=${config.id}`
              : `/extractors/${config.id}/edit`;
            return (
              <Link key={config.id} href={href} className="block">
                <Card className="transition-colors hover:bg-gray-50 cursor-pointer">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg">{config.name}</CardTitle>
                        {isDraft && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
                            <PenLine className="h-3 w-3" />
                            {t("extractors.draft")}
                          </span>
                        )}
                        {config.is_default && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
                            <Star className="h-3 w-3" />
                            {t("extractors.default")}
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
                          className="text-red-600 hover:text-red-700"
                          onClick={(e) => {
                            e.preventDefault();
                            handleDelete(config.id);
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    {config.description && (
                      <CardDescription>{config.description}</CardDescription>
                    )}
                  </CardHeader>
                </Card>
              </Link>
            );
          })}
        </div>
      </div>
    </main>
  );
}
