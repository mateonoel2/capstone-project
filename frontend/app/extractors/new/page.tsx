"use client";

import { useRouter } from "next/navigation";
import { ExtractorConfigForm } from "@/components/extractor-config-form";
import { createExtractorConfig } from "@/lib/api";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function NewExtractorPage() {
  const router = useRouter();

  const handleCreate = async (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => {
    await createExtractorConfig(data);
    router.push("/extractors");
  };

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <Link
            href="/extractors"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-3"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Volver a Extractores
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Crear Extractor</h1>
        </div>

        <ExtractorConfigForm
          onSave={handleCreate}
          onCancel={() => router.push("/extractors")}
        />
      </div>
    </main>
  );
}
