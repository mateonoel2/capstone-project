import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ChevronUp, ChevronDown, Trash2, Plus, X } from "lucide-react";
import { FieldTypeSelect } from "./field-type-select";
import { SchemaField } from "./types";

interface FieldCardProps {
  field: SchemaField;
  index: number;
  total: number;
  error?: string;
  onUpdate: (updates: Partial<Omit<SchemaField, "id">>) => void;
  onRemove: () => void;
  onMove: (direction: "up" | "down") => void;
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "");
}

function EnumOptionsEditor({
  values,
  onChange,
}: {
  values: string[];
  onChange: (values: string[]) => void;
}) {
  const [newValue, setNewValue] = useState("");

  const addValue = () => {
    const trimmed = newValue.trim();
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed]);
      setNewValue("");
    }
  };

  const removeValue = (index: number) => {
    onChange(values.filter((_, i) => i !== index));
  };

  return (
    <div>
      <Label className="text-xs text-muted-foreground">Opciones permitidas</Label>
      <div className="mt-1 flex flex-wrap gap-1.5">
        {values.map((v, i) => (
          <span
            key={i}
            className="inline-flex items-center gap-1 bg-muted text-sm px-2 py-0.5 rounded"
          >
            {v}
            <button
              type="button"
              onClick={() => removeValue(i)}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2 mt-2">
        <Input
          value={newValue}
          onChange={(e) => setNewValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addValue();
            }
          }}
          className="text-sm"
          placeholder="Agregar opción..."
        />
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={addValue}
          disabled={!newValue.trim()}
        >
          <Plus className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
}

export function FieldCard({
  field,
  index,
  total,
  error,
  onUpdate,
  onRemove,
  onMove,
}: FieldCardProps) {
  const slug = slugify(field.name);

  return (
    <Card className={error ? "border-red-400" : ""}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-muted-foreground">
            {index + 1}.
          </span>
          <div className="flex items-center gap-1">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              disabled={index === 0}
              onClick={() => onMove("up")}
            >
              <ChevronUp className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              disabled={index === total - 1}
              onClick={() => onMove("down")}
            >
              <ChevronDown className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-red-500 hover:text-red-600"
              onClick={onRemove}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="grid gap-3">
          <div className="flex items-start gap-3">
            <div className="flex-1">
              <Label className="text-xs text-muted-foreground">Nombre</Label>
              <Input
                value={field.name}
                onChange={(e) => onUpdate({ name: e.target.value })}
                className="mt-1 text-sm"
                placeholder="nombre_del_campo"
              />
              {field.name && slug !== field.name && (
                <p className="text-xs text-muted-foreground mt-1">
                  se usará como: <code>{slug}</code>
                </p>
              )}
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Tipo</Label>
              <div className="mt-1">
                <FieldTypeSelect
                  value={field.type}
                  onChange={(type) =>
                    onUpdate(
                      type === "enum"
                        ? { type, enumValues: field.enumValues || [] }
                        : { type, enumValues: undefined }
                    )
                  }
                />
              </div>
            </div>
          </div>

          <div>
            <Label className="text-xs text-muted-foreground">
              Instrucción para la IA
            </Label>
            <Input
              value={field.description}
              onChange={(e) => onUpdate({ description: e.target.value })}
              className="mt-1 text-sm"
              placeholder="Describe qué debe extraer la IA..."
            />
          </div>

          {field.type === "enum" && (
            <EnumOptionsEditor
              values={field.enumValues || []}
              onChange={(enumValues) => onUpdate({ enumValues })}
            />
          )}
        </div>

        {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
      </CardContent>
    </Card>
  );
}
