"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getAvailableModels, ModelInfo, ParserConfig } from "@/lib/api";
import { Loader2 } from "lucide-react";

interface ParserConfigFormProps {
  initialData?: ParserConfig | null;
  onSave: (data: {
    name: string;
    description: string;
    prompt: string;
    model: string;
    output_schema: Record<string, unknown>;
  }) => Promise<void>;
  onCancel: () => void;
}

const DEFAULT_SCHEMA_EXAMPLE = JSON.stringify(
  {
    type: "object",
    properties: {
      field1: { type: "string", description: "Descripción del campo 1" },
      field2: { type: "string", description: "Descripción del campo 2" },
    },
    required: ["field1", "field2"],
  },
  null,
  2
);

export function ParserConfigForm({
  initialData,
  onSave,
  onCancel,
}: ParserConfigFormProps) {
  const [name, setName] = useState(initialData?.name || "");
  const [description, setDescription] = useState(
    initialData?.description || ""
  );
  const [prompt, setPrompt] = useState(initialData?.prompt || "");
  const [model, setModel] = useState(
    initialData?.model || "claude-haiku-4-5-20251001"
  );
  const [schemaText, setSchemaText] = useState(
    initialData?.output_schema
      ? JSON.stringify(initialData.output_schema, null, 2)
      : DEFAULT_SCHEMA_EXAMPLE
  );
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [schemaError, setSchemaError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAvailableModels()
      .then(setModels)
      .catch(() => {});
  }, []);

  const handleSave = async () => {
    setSchemaError(null);
    setError(null);

    if (!name.trim()) {
      setError("El nombre es requerido");
      return;
    }
    if (!prompt.trim()) {
      setError("El prompt es requerido");
      return;
    }

    let parsedSchema: Record<string, unknown>;
    try {
      parsedSchema = JSON.parse(schemaText);
    } catch {
      setSchemaError("JSON Schema inválido");
      return;
    }

    setIsSaving(true);
    try {
      await onSave({
        name: name.trim(),
        description: description.trim(),
        prompt: prompt.trim(),
        model,
        output_schema: parsedSchema,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="config-name">Nombre</Label>
        <Input
          id="config-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nombre del parser"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="config-description">Descripción</Label>
        <Input
          id="config-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Descripción breve"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="config-model">Modelo</Label>
        <Select value={model} onValueChange={setModel}>
          <SelectTrigger id="config-model">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {models.map((m) => (
              <SelectItem key={m.id} value={m.id}>
                {m.name} ({m.tier}) - {m.cost_hint}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="config-prompt">Prompt</Label>
        <Textarea
          id="config-prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Prompt de extracción..."
          className="font-mono text-sm min-h-[200px]"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="config-schema">Output Schema (JSON Schema)</Label>
        <Textarea
          id="config-schema"
          value={schemaText}
          onChange={(e) => {
            setSchemaText(e.target.value);
            setSchemaError(null);
          }}
          placeholder="JSON Schema..."
          className={`font-mono text-sm min-h-[200px] ${
            schemaError ? "border-red-400" : ""
          }`}
        />
        {schemaError && (
          <p className="text-xs text-red-600">{schemaError}</p>
        )}
      </div>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 p-3 rounded">
          {error}
        </div>
      )}

      <div className="flex gap-2 pt-2">
        <Button onClick={handleSave} disabled={isSaving} className="flex-1">
          {isSaving ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Guardando...
            </>
          ) : (
            "Guardar"
          )}
        </Button>
        <Button variant="outline" onClick={onCancel} disabled={isSaving}>
          Cancelar
        </Button>
      </div>
    </div>
  );
}
