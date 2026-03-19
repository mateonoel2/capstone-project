"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ExtractorEditor } from "@/components/extractor-editor";
import { VersionHistory } from "@/components/version-history";
import { useExtractorConfig, useUpdateExtractorConfig, useDeleteExtractorConfig } from "@/lib/hooks";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2, Star, Trash2, History, Settings } from "lucide-react";
import Link from "next/link";
import { useT } from "@/lib/i18n";

export default function EditExtractorPage() {
  const params = useParams();
  const router = useRouter();
  const configId = Number(params.id);
  const t = useT();

  const { data: config, isLoading, error: loadError, refetch } = useExtractorConfig(configId);
  const updateMutation = useUpdateExtractorConfig();
  const deleteMutation = useDeleteExtractorConfig();
  const [formKey, setFormKey] = useState(0);

  const handleUpdate = async (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => {
    await updateMutation.mutateAsync({ id: configId, config: data });
    router.push("/extractors");
  };

  const handleDelete = async () => {
    if (!confirm(t("extractors.confirmDelete"))) return;
    try {
      await deleteMutation.mutateAsync(configId);
      router.push("/extractors");
    } catch (err) {
      alert(err instanceof Error ? err.message : t("extractors.deleteError"));
    }
  };

  const handleRestore = async () => {
    await refetch();
    setFormKey((k) => k + 1);
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-600">{t("extractors.loadingExtractor")}</span>
        </div>
      </main>
    );
  }

  if (!config) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          <p className="text-gray-600">{loadError instanceof Error ? loadError.message : t("extractors.notFound")}</p>
          <Link href="/extractors" className="text-blue-600 hover:underline text-sm mt-2 inline-block">
            {t("extractors.backToExtractors")}
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
            href="/extractors"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-3"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            {t("extractors.backToExtractors")}
          </Link>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">
                {t("extractors.edit", { name: config.name })}
              </h1>
              {config.is_default && (
                <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
                  <Star className="h-3 w-3" />
                  {t("extractors.default")}
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
                {t("extractors.delete")}
              </Button>
            )}
          </div>
        </div>

        <Tabs defaultValue="config">
          <TabsList className="mb-4">
            <TabsTrigger value="config" className="gap-2">
              <Settings className="h-4 w-4" />
              {t("extractors.configTab")}
            </TabsTrigger>
            <TabsTrigger value="versions" className="gap-2">
              <History className="h-4 w-4" />
              {t("extractors.versionsTab")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="config">
            <Card>
              <CardContent className="pt-6">
                <ExtractorEditor
                  key={formKey}
                  initialData={config}
                  onSave={handleUpdate}
                  onCancel={() => router.push("/extractors")}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="versions">
            <Card>
              <CardContent className="pt-6">
                <VersionHistory configId={configId} onRestore={handleRestore} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}
