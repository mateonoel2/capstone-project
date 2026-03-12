"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { WizardStepper } from "./wizard-stepper";
import { StepIdentity } from "./step-identity";
import { StepSchema } from "./step-schema";
import { StepPrompt } from "./step-prompt";
import { StepTest } from "./step-test";
import { ExtractorConfig } from "@/lib/api";

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

interface ExtractorWizardProps {
  initialData?: ExtractorConfig | null;
  onSave: (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => Promise<void>;
  onCancel: () => void;
}

const DEFAULT_SCHEMA: Record<string, unknown> = {
  type: "object",
  properties: {},
  required: [],
};

export function ExtractorWizard({ initialData, onSave, onCancel }: ExtractorWizardProps) {
  const isEditMode = !!initialData;

  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(
    isEditMode ? new Set([0, 1, 2, 3]) : new Set()
  );
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [state, setState] = useState<WizardState>({
    name: initialData?.name || "",
    description: initialData?.description || "",
    model: initialData?.model || "claude-haiku-4-5-20251001",
    output_schema: initialData?.output_schema || DEFAULT_SCHEMA,
    prompt: initialData?.prompt || "",
  });

  const updateField = useCallback((field: string, value: string) => {
    setState((prev) => ({ ...prev, [field]: value }));
  }, []);

  const updateSchema = useCallback((schema: Record<string, unknown>) => {
    setState((prev) => ({ ...prev, output_schema: schema }));
  }, []);

  const canAdvance = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!state.name.trim();
      case 1: {
        const props = (state.output_schema as { properties?: Record<string, unknown> })?.properties || {};
        return Object.keys(props).filter((k) => k !== "is_bank_statement").length > 0;
      }
      case 2:
        return !!state.prompt.trim();
      default:
        return true;
    }
  };

  const goNext = () => {
    if (!canAdvance(currentStep)) return;
    setCompletedSteps((prev) => new Set([...prev, currentStep]));
    setCurrentStep((prev) => Math.min(prev + 1, STEPS.length - 1));
  };

  const goPrev = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const handleStepClick = (step: number) => {
    if (isEditMode || completedSteps.has(step) || step === currentStep) {
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
      <WizardStepper
        steps={STEPS}
        currentStep={currentStep}
        completedSteps={completedSteps}
        freeNavigation={isEditMode}
        onStepClick={handleStepClick}
      />

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
            schema={state.output_schema}
            onChange={updateSchema}
            isNew={!isEditMode}
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
                  Guardando...
                </>
              ) : (
                "Guardar extractor"
              )}
            </Button>
          ) : (
            <>
              {currentStep === 2 && (
                <Button variant="outline" onClick={handleSave} disabled={isSaving}>
                  {isSaving ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Guardando...
                    </>
                  ) : (
                    "Saltar prueba y guardar"
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
    </div>
  );
}
