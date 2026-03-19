"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ExtractorWizard } from "@/components/extractor-wizard/extractor-wizard";
import { useCreateExtractorConfig, useExtractorConfig } from "@/lib/hooks";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { useT } from "@/lib/i18n";

export default function NewExtractorPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-gray-50 p-6">
          <div className="max-w-5xl mx-auto flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        </main>
      }
    >
      <NewExtractorContent />
    </Suspense>
  );
}

function NewExtractorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const draftIdParam = searchParams.get("draft");
  const draftId = draftIdParam ? Number(draftIdParam) : null;
  const createMutation = useCreateExtractorConfig();
  const t = useT();

  const { data: draftConfig, isLoading: draftLoading } = useExtractorConfig(draftId ?? 0, {
    enabled: draftId !== null,
  });

  const handleCreate = async (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => {
    await createMutation.mutateAsync(data);
    router.push("/extractors");
  };

  if (draftId && draftLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-600">{t("extractors.loadingDraft")}</span>
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
          <h1 className="text-2xl font-bold text-gray-900">
            {draftConfig ? t("extractors.continueExtractor") : t("extractors.createExtractor")}
          </h1>
        </div>

        <Card>
          <CardContent className="pt-6">
            <ExtractorWizard
              onSave={handleCreate}
              onCancel={() => router.push("/extractors")}
              onDraftActivated={() => router.push("/extractors")}
              initialDraft={draftConfig ?? undefined}
            />
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
