"use client";

import { SchemaBuilder } from "@/components/schema-builder/schema-builder";

interface StepSchemaProps {
  schema: Record<string, unknown>;
  onChange: (schema: Record<string, unknown>) => void;
  isNew?: boolean;
}

export function StepSchema({ schema, onChange, isNew }: StepSchemaProps) {
  return <SchemaBuilder value={schema} onChange={onChange} isNew={isNew} />;
}
