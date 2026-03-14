"use client";

interface SchemaSummaryProps {
  schema: Record<string, unknown>;
}

export function SchemaSummary({ schema }: SchemaSummaryProps) {
  const properties = (schema as { properties?: Record<string, { type?: string; description?: string }> })?.properties || {};
  const entries = Object.entries(properties).filter(([key]) => key !== "is_valid_document");

  if (entries.length === 0) {
    return (
      <p className="text-sm text-muted-foreground italic">
        No hay campos definidos en el schema
      </p>
    );
  }

  return (
    <div className="space-y-1">
      {entries.map(([name, prop]) => (
        <div key={name} className="flex items-center gap-2 text-sm">
          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">
            {name}
          </code>
          <span className="text-muted-foreground text-xs">
            {prop.type || "string"}
          </span>
        </div>
      ))}
    </div>
  );
}
