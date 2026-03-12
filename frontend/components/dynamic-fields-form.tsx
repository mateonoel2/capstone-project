"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface JsonSchema {
  properties?: Record<string, { type?: string; description?: string }>;
  required?: string[];
}

interface DynamicFieldsFormProps {
  schema: Record<string, unknown>;
  values: Record<string, string>;
  extracted?: Record<string, unknown>;
  onChange: (field: string, value: string) => void;
}

export function DynamicFieldsForm({
  schema,
  values,
  extracted,
  onChange,
}: DynamicFieldsFormProps) {
  const jsonSchema = schema as JsonSchema;
  const properties = jsonSchema?.properties || {};

  return (
    <div className="space-y-4">
      {Object.entries(properties).filter(([key]) => key !== "is_bank_statement").map(([key, prop]) => {
        const currentValue = values[key] || "";
        const extractedValue = extracted ? String(extracted[key] ?? "") : "";
        const isModified = extracted && currentValue !== extractedValue;

        return (
          <div key={key} className="space-y-2">
            <Label htmlFor={`field-${key}`} className="capitalize">
              {key.replace(/_/g, " ")}
            </Label>
            {prop.type === "boolean" ? (
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id={`field-${key}`}
                  checked={currentValue === "true"}
                  onChange={(e) =>
                    onChange(key, e.target.checked ? "true" : "false")
                  }
                  className="h-4 w-4 rounded border-gray-300"
                />
                <span className="text-sm text-gray-600">
                  {prop.description}
                </span>
              </div>
            ) : prop.type === "number" || prop.type === "integer" ? (
              <Input
                id={`field-${key}`}
                type="number"
                value={currentValue}
                onChange={(e) => onChange(key, e.target.value)}
                placeholder={prop.description}
                className={isModified ? "border-yellow-400" : ""}
              />
            ) : (
              <Input
                id={`field-${key}`}
                value={currentValue}
                onChange={(e) => onChange(key, e.target.value)}
                placeholder={prop.description}
                className={isModified ? "border-yellow-400" : ""}
              />
            )}
            {isModified && (
              <p className="text-xs text-yellow-600">
                IA extrajo: {extractedValue || "(vacío)"}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
