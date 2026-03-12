"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, User, Table2, MessageSquare, FlaskConical } from "lucide-react";
import { StepIdentity } from "./extractor-wizard/step-identity";
import { StepSchema } from "./extractor-wizard/step-schema";
import { StepPrompt } from "./extractor-wizard/step-prompt";
import { StepTest } from "./extractor-wizard/step-test";
import { ExtractorConfig } from "@/lib/api";

interface EditorState {
  name: string;
  description: string;
  model: string;
  output_schema: Record<string, unknown>;
  prompt: string;
}

interface ExtractorEditorProps {
  initialData: ExtractorConfig;
  onSave: (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => Promise<void>;
  onCancel: () => void;
}

export function ExtractorEditor({ initialData, onSave, onCancel }: ExtractorEditorProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [state, setState] = useState<EditorState>({
    name: initialData.name,
    description: initialData.description || "",
    model: initialData.model,
    output_schema: initialData.output_schema,
    prompt: initialData.prompt,
  });

  const updateField = useCallback((field: string, value: string) => {
    setState((prev) => ({ ...prev, [field]: value }));
  }, []);

  const updateSchema = useCallback((schema: Record<string, unknown>) => {
    setState((prev) => ({ ...prev, output_schema: schema }));
  }, []);

  const handleSave = async () => {
    setError(null);
    if (!state.name.trim()) {
      setError("El nombre es requerido");
      return;
    }
    if (!state.prompt.trim()) {
      setError("El prompt es requerido");
      return;
    }

    setIsSaving(true);
    try {
      await onSave({
        name: state.name.trim(),
        description: state.description.trim(),
        prompt: state.prompt.trim(),
        model: state.model,
        output_schema: state.output_schema,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div>
      <Tabs defaultValue="identity">
        <TabsList className="mb-6">
          <TabsTrigger value="identity" className="gap-2">
            <User className="h-4 w-4" />
            Identidad
          </TabsTrigger>
          <TabsTrigger value="schema" className="gap-2">
            <Table2 className="h-4 w-4" />
            Esquema
          </TabsTrigger>
          <TabsTrigger value="prompt" className="gap-2">
            <MessageSquare className="h-4 w-4" />
            Prompt
          </TabsTrigger>
          <TabsTrigger value="test" className="gap-2">
            <FlaskConical className="h-4 w-4" />
            Probar
          </TabsTrigger>
        </TabsList>

        <div className="min-h-[400px]">
          <TabsContent value="identity">
            <StepIdentity
              name={state.name}
              description={state.description}
              model={state.model}
              onChange={updateField}
            />
          </TabsContent>
          <TabsContent value="schema">
            <StepSchema
              schema={state.output_schema}
              onChange={updateSchema}
              isNew={false}
            />
          </TabsContent>
          <TabsContent value="prompt">
            <StepPrompt
              prompt={state.prompt}
              schema={state.output_schema}
              description={state.description}
              onChange={(p) => updateField("prompt", p)}
            />
          </TabsContent>
          <TabsContent value="test">
            <StepTest
              prompt={state.prompt}
              model={state.model}
              schema={state.output_schema}
            />
          </TabsContent>
        </div>
      </Tabs>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 p-3 rounded mt-4">
          {error}
        </div>
      )}

      <div className="flex items-center justify-end pt-6 mt-6 border-t gap-2">
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancelar
        </Button>
        <Button onClick={handleSave} disabled={isSaving}>
          {isSaving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Guardando...
            </>
          ) : (
            "Guardar extractor"
          )}
        </Button>
      </div>
    </div>
  );
}
