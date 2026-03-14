"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, Sparkles } from "lucide-react";
import { WizardStepper } from "./wizard-stepper";
import { StepIdentity } from "./step-identity";
import { StepSchema } from "./step-schema";
import { StepPrompt } from "./step-prompt";
import { StepTest } from "./step-test";
import {
  AssistantSidebar,
  type AssistantMode,
} from "@/components/assistant/assistant-sidebar";
import {
  useCreateExtractorConfig,
  useUpdateExtractorConfig,
} from "@/lib/hooks";

const STEPS = [
  { label: "Identidad", description: "Nombre y modelo" },
  { label: "Esquema", description: "Campos a extraer" },
  { label: "Prompt", description: "Instrucciones" },
  { label: "Probar", description: "Prueba en vivo" },
];

interface WizardState {
  name: string;
  description: string;
  model: string;
  output_schema: Record<string, unknown>;
  prompt: string;
}

interface DraftData {
  id: number;
  name: string;
  description: string | null;
  model: string;
  prompt: string;
  output_schema: Record<string, unknown>;
}

interface ExtractorWizardProps {
  onSave: (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => Promise<void>;
  onCancel: () => void;
  onDraftActivated?: () => void;
  initialDraft?: DraftData;
}

const DEFAULT_SCHEMA: Record<string, unknown> = {
  type: "object",
  properties: {},
  required: [],
};

function getAssistantMode(step: number): AssistantMode {
  if (step === 1) return "schema";
  if (step === 2) return "prompt";
  return null;
}

export function ExtractorWizard({ onSave, onCancel, onDraftActivated, initialDraft }: ExtractorWizardProps) {
  const hasSchema = initialDraft
    ? Object.keys((initialDraft.output_schema as { properties?: Record<string, unknown> })?.properties || {}).filter((k) => k !== "is_valid_document").length > 0
    : false;
  const hasPrompt = !!initialDraft?.prompt?.trim();

  const initialCompleted = new Set<number>();
  if (initialDraft?.name?.trim()) initialCompleted.add(0);
  if (hasSchema) initialCompleted.add(1);
  if (hasPrompt) initialCompleted.add(2);

  // Resume at the first incomplete step
  const initialStep = initialDraft
    ? (!initialDraft.name?.trim() ? 0 : !hasSchema ? 1 : !hasPrompt ? 2 : 3)
    : 0;

  const [currentStep, setCurrentStep] = useState(initialStep);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(initialCompleted);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [schemaVersion, setSchemaVersion] = useState(0);
  const [draftId, setDraftId] = useState<number | null>(initialDraft?.id ?? null);
  const draftCreating = useRef(false);

  const createConfig = useCreateExtractorConfig();
  const updateConfig = useUpdateExtractorConfig();

  const [state, setState] = useState<WizardState>({
    name: initialDraft?.name ?? "",
    description: initialDraft?.description ?? "",
    model: initialDraft?.model ?? "claude-haiku-4-5-20251001",
    output_schema: initialDraft?.output_schema ?? DEFAULT_SCHEMA,
    prompt: initialDraft?.prompt ?? "",
  });

  const updateField = useCallback((field: string, value: string) => {
    setState((prev) => ({ ...prev, [field]: value }));
  }, []);

  const updateSchema = useCallback((schema: Record<string, unknown>) => {
    setState((prev) => ({ ...prev, output_schema: schema }));
  }, []);

  const saveDraft = useCallback(
    async (currentState: WizardState, existingDraftId: number | null) => {
      if (existingDraftId) {
        try {
          await updateConfig.mutateAsync({
            id: existingDraftId,
            config: {
              name: currentState.name.trim(),
              description: currentState.description.trim(),
              prompt: currentState.prompt,
              model: currentState.model,
              output_schema: currentState.output_schema,
              status: "draft",
            },
          });
        } catch {
          // Draft update is best-effort
        }
      } else if (!draftCreating.current) {
        draftCreating.current = true;
        try {
          const created = await createConfig.mutateAsync({
            name: currentState.name.trim(),
            description: currentState.description.trim(),
            model: currentState.model,
            status: "draft",
          });
          setDraftId(created.id);
          return created.id;
        } catch {
          // Draft creation is best-effort
        } finally {
          draftCreating.current = false;
        }
      }
      return existingDraftId;
    },
    [createConfig, updateConfig]
  );

  const canAdvance = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!state.name.trim();
      case 1: {
        const props = (state.output_schema as { properties?: Record<string, unknown> })?.properties || {};
        return Object.keys(props).filter((k) => k !== "is_valid_document").length > 0;
      }
      case 2:
        return !!state.prompt.trim();
      default:
        return true;
    }
  };

  const goNext = async () => {
    if (!canAdvance(currentStep)) return;
    setCompletedSteps((prev) => new Set([...prev, currentStep]));
    // Create or update draft on step transition
    const newDraftId = await saveDraft(state, draftId);
    if (newDraftId && !draftId) setDraftId(newDraftId);
    setCurrentStep((prev) => Math.min(prev + 1, STEPS.length - 1));
  };

  const goPrev = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const handleStepClick = (step: number) => {
    if (completedSteps.has(step) || step === currentStep) {
      setCurrentStep(step);
    }
  };

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
      if (draftId) {
        // Activate the draft — update to active then notify parent
        await updateConfig.mutateAsync({
          id: draftId,
          config: {
            name: state.name.trim(),
            description: state.description.trim(),
            prompt: state.prompt.trim(),
            model: state.model,
            output_schema: state.output_schema,
            status: "active",
          },
        });
        onDraftActivated?.();
      } else {
        // No draft — fallback to original create flow
        await onSave({
          name: state.name.trim(),
          description: state.description.trim(),
          prompt: state.prompt.trim(),
          model: state.model,
          output_schema: state.output_schema,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setIsSaving(false);
    }
  };

  const assistantMode = getAssistantMode(currentStep);

  return (
    <div>
      <WizardStepper
          steps={STEPS}
          currentStep={currentStep}
          completedSteps={completedSteps}
          onStepClick={handleStepClick}
        />

        <div className="flex items-center justify-between mb-4">
          <div />
          {assistantMode && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setAssistantOpen((prev) => !prev)}
              className={assistantOpen ? "bg-blue-50 border-blue-200 text-blue-700" : ""}
            >
              <Sparkles className="h-4 w-4 mr-1" />
              Asistente IA
            </Button>
          )}
        </div>

        <div className="min-h-[400px]">
          {currentStep === 0 && (
            <StepIdentity
              name={state.name}
              description={state.description}
              model={state.model}
              onChange={updateField}
            />
          )}
          {currentStep === 1 && (
            <StepSchema
              key={schemaVersion}
              schema={state.output_schema}
              onChange={updateSchema}
              isNew={true}
            />
          )}
          {currentStep === 2 && (
            <StepPrompt
              prompt={state.prompt}
              schema={state.output_schema}
              description={state.description}
              onChange={(p) => updateField("prompt", p)}
            />
          )}
          {currentStep === 3 && (
            <StepTest
              prompt={state.prompt}
              model={state.model}
              schema={state.output_schema}
              extractorConfigId={draftId}
            />
          )}
        </div>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded mt-4">
            {error}
          </div>
        )}

        <div className="flex items-center justify-between pt-6 mt-6 border-t">
          <div>
            {currentStep > 0 && (
              <Button type="button" variant="outline" onClick={goPrev}>
                Anterior
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="ghost" onClick={onCancel}>
              Cancelar
            </Button>
            {currentStep === STEPS.length - 1 ? (
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creando...
                  </>
                ) : (
                  "Crear extractor"
                )}
              </Button>
            ) : (
              <>
                {currentStep === 2 && (
                  <Button variant="outline" onClick={handleSave} disabled={isSaving}>
                    {isSaving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Creando...
                      </>
                    ) : (
                      "Saltar prueba y crear"
                    )}
                  </Button>
                )}
                <Button onClick={goNext} disabled={!canAdvance(currentStep)}>
                  Siguiente
                </Button>
              </>
            )}
          </div>
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
