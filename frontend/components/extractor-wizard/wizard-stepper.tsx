"use client";

import { Check } from "lucide-react";

interface WizardStepperProps {
  steps: { label: string; description: string }[];
  currentStep: number;
  completedSteps: Set<number>;
  freeNavigation?: boolean;
  onStepClick: (step: number) => void;
}

export function WizardStepper({
  steps,
  currentStep,
  completedSteps,
  freeNavigation,
  onStepClick,
}: WizardStepperProps) {
  return (
    <nav className="mb-8">
      <ol className="flex items-center w-full">
        {steps.map((step, idx) => {
          const isActive = idx === currentStep;
          const isCompleted = completedSteps.has(idx);
          const isClickable = freeNavigation || isCompleted || idx === currentStep;

          return (
            <li
              key={idx}
              className={`flex items-center ${idx < steps.length - 1 ? "flex-1" : ""}`}
            >
              <button
                type="button"
                onClick={() => isClickable && onStepClick(idx)}
                disabled={!isClickable}
                className={`flex items-center gap-2 group ${
                  isClickable ? "cursor-pointer" : "cursor-not-allowed opacity-50"
                }`}
              >
                <span
                  className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium shrink-0 transition-colors ${
                    isActive
                      ? "bg-blue-600 text-white"
                      : isCompleted
                        ? "bg-green-600 text-white"
                        : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {isCompleted && !isActive ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    idx + 1
                  )}
                </span>
                <div className="hidden sm:block text-left">
                  <p
                    className={`text-sm font-medium ${
                      isActive ? "text-blue-600" : "text-gray-700"
                    }`}
                  >
                    {step.label}
                  </p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
              </button>
              {idx < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-3 ${
                    completedSteps.has(idx) ? "bg-green-600" : "bg-gray-200"
                  }`}
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
