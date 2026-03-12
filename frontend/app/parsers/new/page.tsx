"use client";

import { useRouter } from "next/navigation";
import { ParserConfigForm } from "@/components/parser-config-form";
import { createParserConfig } from "@/lib/api";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function NewParserPage() {
  const router = useRouter();

  const handleCreate = async (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => {
    await createParserConfig(data);
    router.push("/parsers");
  };

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
          <h1 className="text-2xl font-bold text-gray-900">Crear Parser</h1>
        </div>

        <ParserConfigForm
          onSave={handleCreate}
          onCancel={() => router.push("/parsers")}
        />
      </div>
    </main>
  );
}
