"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { EnumCombobox } from "@/components/enum-combobox";
import { toStr } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import { Plus, Trash2 } from "lucide-react";

interface SchemaProperty {
  type?: string;
  description?: string;
  enum?: string[];
  items?: {
    type?: string;
    properties?: Record<string, { type?: string; description?: string }>;
  };
}

interface JsonSchema {
  properties?: Record<string, SchemaProperty>;
  required?: string[];
}

interface DynamicFieldsFormProps {
  schema: Record<string, unknown>;
  values: Record<string, string>;
  extracted?: Record<string, unknown>;
  onChange: (field: string, value: string) => void;
}

function parseArray(value: string): Record<string, unknown>[] {
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch {
    return [];
  }
}

function EditableArrayTable({
  value,
  schema,
  onChange,
}: {
  value: string;
  schema?: SchemaProperty["items"];
  onChange: (json: string) => void;
}) {
  const t = useT();
  const items = parseArray(value);
  const columns = Object.keys(schema?.properties ?? items[0] ?? {});

  if (columns.length === 0 && items.length === 0) {
    return <p className="text-sm text-gray-500 italic">—</p>;
  }

  const update = (rowIdx: number, col: string, cellValue: string) => {
    const next = items.map((item, i) =>
      i === rowIdx ? { ...item, [col]: cellValue } : item
    );
    onChange(JSON.stringify(next));
  };

  const addRow = () => {
    const empty: Record<string, unknown> = {};
    for (const col of columns) empty[col] = "";
    onChange(JSON.stringify([...items, empty]));
  };

  const removeRow = (rowIdx: number) => {
    onChange(JSON.stringify(items.filter((_, i) => i !== rowIdx)));
  };

  return (
    <div className="space-y-2">
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-2 py-2 text-left font-medium text-gray-600 capitalize whitespace-nowrap text-xs"
                >
                  {col.replace(/_/g, " ")}
                </th>
              ))}
              <th className="w-10" />
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                {columns.map((col) => (
                  <td key={col} className="px-1 py-1">
                    <Input
                      value={toStr(item[col])}
                      onChange={(e) => update(i, col, e.target.value)}
                      className="h-8 text-sm"
                    />
                  </td>
                ))}
                <td className="px-1 py-1 text-center">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-gray-400 hover:text-red-500"
                    onClick={() => removeRow(i)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length + 1}
                  className="px-3 py-4 text-center text-sm text-gray-400"
                >
                  {t("dynamicFields.noItems")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="w-full"
        onClick={addRow}
      >
        <Plus className="h-4 w-4 mr-1" />
        {t("dynamicFields.addItem")}
      </Button>
    </div>
  );
}

export function DynamicFieldsForm({
  schema,
  values,
  extracted,
  onChange,
}: DynamicFieldsFormProps) {
  const jsonSchema = schema as JsonSchema;
  const properties = jsonSchema?.properties || {};
  const t = useT();

  return (
    <div className="space-y-4">
      {Object.entries(properties).filter(([key]) => key !== "is_valid_document").map(([key, prop]) => {
        const currentValue = values[key] || "";
        const extractedValue = extracted ? toStr(extracted[key]) : "";
        const isModified = extracted && currentValue !== extractedValue;

        return (
          <div key={key} className="space-y-2">
            <Label htmlFor={`field-${key}`} className="capitalize">
              {key.replace(/_/g, " ")}
            </Label>
            {prop.type === "array" ? (
              <EditableArrayTable
                value={currentValue}
                schema={prop.items}
                onChange={(json) => onChange(key, json)}
              />
            ) : prop.type === "boolean" ? (
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
            ) : Array.isArray(prop.enum) && prop.enum.length > 0 ? (
              <EnumCombobox
                options={prop.enum}
                value={currentValue}
                onChange={(v) => onChange(key, v)}
                placeholder={prop.description}
                className={isModified ? "border-yellow-400" : ""}
              />
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
            {isModified && prop.type !== "array" && (
              <p className="text-xs text-yellow-600">
                {t("dynamicFields.aiExtracted", { value: extractedValue || t("dynamicFields.empty") })}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
