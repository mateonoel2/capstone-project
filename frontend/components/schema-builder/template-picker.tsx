import { Card, CardContent } from "@/components/ui/card";
import { TEMPLATES, SchemaTemplate } from "./types";

interface TemplatePickerProps {
  onSelect: (template: SchemaTemplate) => void;
}

export function TemplatePicker({ onSelect }: TemplatePickerProps) {
  return (
    <div className="space-y-2">
      <p className="text-sm text-muted-foreground">
        Selecciona una plantilla para empezar:
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {TEMPLATES.map((tpl) => (
          <Card
            key={tpl.label}
            className="cursor-pointer hover:border-primary transition-colors"
            onClick={() => onSelect(tpl)}
          >
            <CardContent className="p-4">
              <p className="font-medium text-sm">{tpl.label}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {tpl.description}
              </p>
              {tpl.fields.length > 0 && (
                <p className="text-xs text-muted-foreground mt-2">
                  {tpl.fields.length} campo{tpl.fields.length !== 1 && "s"}:{" "}
                  {tpl.fields.map((f) => f.name).join(", ")}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
