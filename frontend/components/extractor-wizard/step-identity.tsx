"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAvailableModels } from "@/lib/hooks";
import { useT } from "@/lib/i18n";

interface StepIdentityProps {
  name: string;
  description: string;
  model: string;
  onChange: (field: string, value: string) => void;
}

export function StepIdentity({ name, description, model, onChange }: StepIdentityProps) {
  const { data: models = [] } = useAvailableModels();
  const t = useT();

  return (
    <div className="max-w-lg space-y-6">
      <div className="space-y-2">
        <Label htmlFor="wizard-name">{t("stepIdentity.name")}</Label>
        <Input
          id="wizard-name"
          value={name}
          onChange={(e) => onChange("name", e.target.value)}
          placeholder={t("stepIdentity.namePlaceholder")}
        />
        <p className="text-xs text-muted-foreground">
          {t("stepIdentity.nameHelp")}
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="wizard-description">{t("stepIdentity.description")}</Label>
        <Input
          id="wizard-description"
          value={description}
          onChange={(e) => onChange("description", e.target.value)}
          placeholder={t("stepIdentity.descriptionPlaceholder")}
        />
        <p className="text-xs text-muted-foreground">
          {t("stepIdentity.descriptionHelp")}
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="wizard-model">{t("stepIdentity.model")}</Label>
        <Select value={model} onValueChange={(v) => onChange("model", v)}>
          <SelectTrigger id="wizard-model">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {models.map((m) => (
              <SelectItem key={m.id} value={m.id} disabled={!m.is_available}>
                {m.name} ({m.tier}) - {m.cost_hint}
                {!m.is_available && ` — ${t("stepIdentity.comingSoon")}`}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-xs text-muted-foreground">
          {t("stepIdentity.modelHelp")}
        </p>
      </div>
    </div>
  );
}
