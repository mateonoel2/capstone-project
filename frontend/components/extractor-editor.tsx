"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, User, Table2, MessageSquare, FlaskConical, Sparkles } from "lucide-react";
import { StepIdentity } from "./extractor-wizard/step-identity";
import { StepSchema } from "./extractor-wizard/step-schema";
import { StepPrompt } from "./extractor-wizard/step-prompt";
import { StepTest } from "./extractor-wizard/step-test";
import { ExtractorConfig } from "@/lib/api";
import {
  AssistantSidebar,
  type AssistantMode,
} from "@/components/assistant/assistant-sidebar";
import { useT } from "@/lib/i18n";

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

function getAssistantMode(tab: string): AssistantMode {
  if (tab === "schema") return "schema";
  if (tab === "prompt") return "prompt";
  return null;
}

export function ExtractorEditor({ initialData, onSave, onCancel }: ExtractorEditorProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("identity");
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [schemaVersion, setSchemaVersion] = useState(0);
  const t = useT();

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
      setError(t("editor.nameRequired"));
      return;
    }
    if (!state.prompt.trim()) {
      setError(t("editor.promptRequired"));
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
      setError(err instanceof Error ? err.message : t("editor.saveError"));
    } finally {
      setIsSaving(false);
    }
  };

  const assistantMode = getAssistantMode(activeTab);

  return (
    <div>
      <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="flex items-center justify-between mb-6">
            <TabsList>
              <TabsTrigger value="identity" className="gap-2">
                <User className="h-4 w-4" />
                {t("editor.identityTab")}
              </TabsTrigger>
              <TabsTrigger value="schema" className="gap-2">
                <Table2 className="h-4 w-4" />
                {t("editor.schemaTab")}
              </TabsTrigger>
              <TabsTrigger value="prompt" className="gap-2">
                <MessageSquare className="h-4 w-4" />
                {t("editor.promptTab")}
              </TabsTrigger>
              <TabsTrigger value="test" className="gap-2">
                <FlaskConical className="h-4 w-4" />
                {t("editor.testTab")}
              </TabsTrigger>
            </TabsList>
            {assistantMode && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setAssistantOpen((prev) => !prev)}
                className={assistantOpen ? "bg-blue-50 border-blue-200 text-blue-700" : ""}
              >
                <Sparkles className="h-4 w-4 mr-1" />
                {t("editor.aiAssistant")}
              </Button>
            )}
          </div>

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
                key={schemaVersion}
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
            {t("editor.cancel")}
          </Button>
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t("editor.saving")}
              </>
            ) : (
              t("editor.saveExtractor")
            )}
          </Button>
        </div>

      <AssistantSidebar
        mode={assistantMode}
        open={assistantOpen}
        onClose={() => setAssistantOpen(false)}
        onSchemaGenerated={(schema) => {
          updateSchema(schema);
          setSchemaVersion((v) => v + 1);
        }}
        onPromptGenerated={(prompt) => updateField("prompt", prompt)}
        schema={state.output_schema}
        currentPrompt={state.prompt}
      />
    </div>
  );
}
