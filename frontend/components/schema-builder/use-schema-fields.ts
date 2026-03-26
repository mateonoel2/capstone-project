import { useState, useCallback } from "react";
import { SchemaField, ArraySubField, VALIDATION_FIELD } from "./types";

let nextId = 1;
function genId() {
  return `field_${Date.now()}_${nextId++}`;
}

interface JsonSchema {
  type: string;
  properties: Record<
    string,
    { type: string; description?: string; [k: string]: unknown }
  >;
  required?: string[];
  [k: string]: unknown;
}

export function toJsonSchema(fields: SchemaField[]): JsonSchema {
  const allFields = [VALIDATION_FIELD, ...fields];
  const properties: JsonSchema["properties"] = {};
  const required: string[] = [];

  for (const f of allFields) {
    if (f.type === "enum") {
      properties[f.name] = { type: "string", enum: f.enumValues || [] };
    } else if (f.type === "date") {
      properties[f.name] = { type: "string", format: "date" };
    } else if (f.type === "array") {
      const itemProps: Record<string, { type: string; description?: string }> = {};
      const itemRequired: string[] = [];
      for (const sub of f.arrayFields || []) {
        itemProps[sub.name] = { type: sub.type };
        if (sub.description) itemProps[sub.name].description = sub.description;
        itemRequired.push(sub.name);
      }
      properties[f.name] = {
        type: "array",
        description: f.description,
        items: {
          type: "object",
          properties: itemProps,
          required: itemRequired,
        },
      };
    } else {
      properties[f.name] = { type: f.type };
    }
    if (f.description && f.type !== "array") {
      properties[f.name].description = f.description;
    }
    required.push(f.name);
  }

  return { type: "object", properties, required };
}

export function fromJsonSchema(
  schema: JsonSchema
): { fields: SchemaField[]; supported: boolean } {
  try {
    if (schema.type !== "object" || !schema.properties) {
      return { fields: [], supported: false };
    }

    const fields: SchemaField[] = [];
    for (const [key, prop] of Object.entries(schema.properties)) {
      if (key === "is_valid_document") continue;

      const hasEnum = Array.isArray(prop.enum);
      const fieldType = prop.type;
      const hasDateFormat = prop.format === "date";

      if (hasEnum && fieldType === "string") {
        fields.push({
          id: genId(),
          name: key,
          type: "enum",
          description: (prop.description as string) || "",
          enumValues: (prop.enum as string[]) || [],
        });
      } else if (hasDateFormat && fieldType === "string") {
        fields.push({
          id: genId(),
          name: key,
          type: "date",
          description: (prop.description as string) || "",
        });
      } else if (fieldType === "array") {
        const items = prop.items as
          | { type?: string; properties?: Record<string, { type?: string; description?: string }>; }
          | undefined;
        const subFields: ArraySubField[] = [];
        if (items?.type === "object" && items.properties) {
          for (const [subKey, subProp] of Object.entries(items.properties)) {
            const subType = subProp.type as "string" | "number" | "boolean" | undefined;
            subFields.push({
              name: subKey,
              type: subType === "number" || subType === "boolean" ? subType : "string",
              description: subProp.description || "",
            });
          }
        }
        fields.push({
          id: genId(),
          name: key,
          type: "array",
          description: (prop.description as string) || "",
          arrayFields: subFields,
        });
      } else if (
        fieldType === "string" ||
        fieldType === "number" ||
        fieldType === "boolean"
      ) {
        fields.push({
          id: genId(),
          name: key,
          type: fieldType,
          description: (prop.description as string) || "",
        });
      } else {
        return { fields: [], supported: false };
      }
    }

    return { fields, supported: true };
  } catch {
    return { fields: [], supported: false };
  }
}

export function useSchemaFields(initial: SchemaField[] = []) {
  const [fields, setFields] = useState<SchemaField[]>(initial);

  const addField = useCallback(() => {
    setFields((prev) => [
      ...prev,
      { id: genId(), name: "", type: "string", description: "" },
    ]);
  }, []);

  const updateField = useCallback(
    (id: string, updates: Partial<Omit<SchemaField, "id">>) => {
      setFields((prev) =>
        prev.map((f) => (f.id === id ? { ...f, ...updates } : f))
      );
    },
    []
  );

  const removeField = useCallback((id: string) => {
    setFields((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const moveField = useCallback((id: string, direction: "up" | "down") => {
    setFields((prev) => {
      const idx = prev.findIndex((f) => f.id === id);
      if (idx < 0) return prev;
      const swapIdx = direction === "up" ? idx - 1 : idx + 1;
      if (swapIdx < 0 || swapIdx >= prev.length) return prev;
      const next = [...prev];
      [next[idx], next[swapIdx]] = [next[swapIdx], next[idx]];
      return next;
    });
  }, []);

  const replaceAll = useCallback((newFields: SchemaField[]) => {
    setFields(newFields);
  }, []);

  return { fields, addField, updateField, removeField, moveField, replaceAll };
}
