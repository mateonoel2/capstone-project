import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FIELD_TYPE_OPTIONS, SchemaField } from "./types";
import { Type, Hash, ToggleLeft, List, Calendar } from "lucide-react";

const TYPE_ICONS = {
  string: Type,
  number: Hash,
  boolean: ToggleLeft,
  enum: List,
  date: Calendar,
};

interface FieldTypeSelectProps {
  value: SchemaField["type"];
  onChange: (value: SchemaField["type"]) => void;
}

export function FieldTypeSelect({ value, onChange }: FieldTypeSelectProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[140px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {FIELD_TYPE_OPTIONS.map((opt) => {
          const Icon = TYPE_ICONS[opt.value];
          return (
            <SelectItem key={opt.value} value={opt.value}>
              <span className="flex items-center gap-2">
                <Icon className="h-3.5 w-3.5" />
                {opt.label}
              </span>
            </SelectItem>
          );
        })}
      </SelectContent>
    </Select>
  );
}
