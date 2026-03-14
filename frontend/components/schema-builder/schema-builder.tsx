"use client";

import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Braces } from "lucide-react";
import { SchemaField, SchemaTemplate, VALIDATION_FIELD } from "./types";
import { useSchemaFields, toJsonSchema, fromJsonSchema } from "./use-schema-fields";
import { FieldCard } from "./field-card";
import { ValidationFieldCard } from "./validation-field-card";
import { TemplatePicker } from "./template-picker";

interface SchemaBuilderProps {
  value: Record<string, unknown>;
  onChange: (schema: Record<string, unknown>) => void;
  isNew?: boolean;
}

function validateFields(
  fields: SchemaField[]
): Record<string, string> {
  const errors: Record<string, string> = {};
  const seen = new Set<string>();

  for (const f of fields) {
    const name = f.name.trim();
    if (!name) {
      errors[f.id] = "El nombre es requerido";
      continue;
    }
    if (!/^[a-z0-9_]+$/i.test(name)) {
      errors[f.id] = "Solo letras, números y guiones bajos";
      continue;
    }
    if (name === "is_valid_document") {
      errors[f.id] = "Nombre reservado";
      continue;
    }
    if (seen.has(name.toLowerCase())) {
      errors[f.id] = "Nombre duplicado";
      continue;
    }
    seen.add(name.toLowerCase());
  }

  return errors;
}

let idCounter = 0;
function genId() {
  return `tpl_${Date.now()}_${idCounter++}`;
}

export function SchemaBuilder({ value, onChange, isNew }: SchemaBuilderProps) {
  const parsed = useMemo(() => fromJsonSchema(value as Parameters<typeof fromJsonSchema>[0]), []); // eslint-disable-line react-hooks/exhaustive-deps
  const initialFields = useRef(parsed.fields);
  const initialSupported = useRef(parsed.supported);

  const { fields, addField, updateField, removeField, moveField, replaceAll } =
    useSchemaFields(initialFields.current);

  const [validationDesc, setValidationDesc] = useState(
    () =>
      (value as Record<string, Record<string, Record<string, string>>>)
        ?.properties?.is_valid_document?.description ||
      VALIDATION_FIELD.description
  );

  const [jsonMode, setJsonMode] = useState(!initialSupported.current);
  const [jsonText, setJsonText] = useState(() => JSON.stringify(value, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [showTemplates, setShowTemplates] = useState(
    isNew && initialFields.current.length === 0
  );

  // Sync visual → parent whenever fields or validation desc change
  const syncToParent = useCallback(() => {
    const errors = validateFields(fields);
    setFieldErrors(errors);

    const schema = toJsonSchema(fields);
    // Override is_valid_document description
    if (schema.properties.is_valid_document) {
      schema.properties.is_valid_document.description = validationDesc;
    }
    const text = JSON.stringify(schema, null, 2);
    setJsonText(text);
    onChange(schema);
  }, [fields, validationDesc, onChange]);

  // Trigger sync on field/desc changes (skip on mount to avoid double-call)
  const mounted = useRef(false);
  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;
      return;
    }
    if (!jsonMode) {
      syncToParent();
    }
  }, [fields, validationDesc, jsonMode, syncToParent]);

  const handleToggleJsonMode = () => {
    if (jsonMode) {
      // Switching from JSON → visual
      try {
        const parsed = JSON.parse(jsonText);
        const result = fromJsonSchema(parsed);
        if (!result.supported) {
          setJsonError(
            "El schema tiene estructuras no soportadas por el editor visual"
          );
          return;
        }
        replaceAll(result.fields);
        const desc =
          parsed?.properties?.is_valid_document?.description ||
          VALIDATION_FIELD.description;
        setValidationDesc(desc);
        setJsonError(null);
        setJsonMode(false);
      } catch {
        setJsonError("JSON inválido");
      }
    } else {
      // Switching from visual → JSON
      const schema = toJsonSchema(fields);
      if (schema.properties.is_valid_document) {
        schema.properties.is_valid_document.description = validationDesc;
      }
      setJsonText(JSON.stringify(schema, null, 2));
      setJsonMode(true);
    }
  };

  const handleJsonChange = (text: string) => {
    setJsonText(text);
    setJsonError(null);
    try {
      const parsed = JSON.parse(text);
      onChange(parsed);
    } catch {
      // Don't propagate invalid JSON
    }
  };

  const handleTemplateSelect = (template: SchemaTemplate) => {
    const newFields: SchemaField[] = template.fields.map((f) => ({
      ...f,
      id: genId(),
    }));
    replaceAll(newFields);
    setShowTemplates(false);
  };

  if (showTemplates) {
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Campos de extracción</Label>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setShowTemplates(false)}
          >
            Saltar
          </Button>
        </div>
        <TemplatePicker onSelect={handleTemplateSelect} />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label>Campos de extracción</Label>
        <div className="flex items-center gap-2">
          {!jsonMode && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addField}
            >
              <Plus className="h-3.5 w-3.5 mr-1" />
              Agregar campo
            </Button>
          )}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleToggleJsonMode}
          >
            <Braces className="h-3.5 w-3.5 mr-1" />
            {jsonMode ? "Visual" : "JSON"}
          </Button>
        </div>
      </div>

      {jsonMode ? (
        <div className="space-y-2">
          <Textarea
            value={jsonText}
            onChange={(e) => handleJsonChange(e.target.value)}
            className={`font-mono text-sm min-h-[300px] ${jsonError ? "border-red-400" : ""}`}
            placeholder="JSON Schema..."
          />
          {jsonError && <p className="text-xs text-red-600">{jsonError}</p>}
        </div>
      ) : (
        <div className="space-y-3">
          <ValidationFieldCard
            description={validationDesc}
            onDescriptionChange={setValidationDesc}
          />

          {fields.map((field, idx) => (
            <FieldCard
              key={field.id}
              field={field}
              index={idx}
              total={fields.length}
              error={fieldErrors[field.id]}
              onUpdate={(updates) => updateField(field.id, updates)}
              onRemove={() => removeField(field.id)}
              onMove={(dir) => moveField(field.id, dir)}
            />
          ))}

          {fields.length === 0 && (
            <div className="text-center py-6 text-sm text-muted-foreground border border-dashed rounded-lg">
              No hay campos. Haz clic en &quot;Agregar campo&quot; para empezar.
            </div>
          )}

          <Button
            type="button"
            variant="outline"
            size="sm"
            className="w-full"
            onClick={addField}
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Agregar campo
          </Button>
        </div>
      )}
    </div>
  );
}
