import { Card, CardContent } from "@/components/ui/card";
import { TEMPLATES, SchemaTemplate } from "./types";
import { useT } from "@/lib/i18n";

interface TemplatePickerProps {
  onSelect: (template: SchemaTemplate) => void;
}

const TEMPLATE_KEYS = [
  { labelKey: "templates.bankStatement", descKey: "templates.bankStatementDesc" },
  { labelKey: "templates.invoice", descKey: "templates.invoiceDesc" },
  { labelKey: "templates.blank", descKey: "templates.blankDesc" },
];

export function TemplatePicker({ onSelect }: TemplatePickerProps) {
  const t = useT();

  return (
    <div className="space-y-2">
      <p className="text-sm text-muted-foreground">
        {t("templatePicker.selectTemplate")}
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {TEMPLATES.map((tpl, idx) => (
          <Card
            key={idx}
            className="cursor-pointer hover:border-primary transition-colors"
            onClick={() => onSelect(tpl)}
          >
            <CardContent className="p-4">
              <p className="font-medium text-sm">{t(TEMPLATE_KEYS[idx].labelKey)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {t(TEMPLATE_KEYS[idx].descKey)}
              </p>
              {tpl.fields.length > 0 && (
                <p className="text-xs text-muted-foreground mt-2">
                  {tpl.fields.length} {tpl.fields.length === 1 ? "campo" : "campos"}:{" "}
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
