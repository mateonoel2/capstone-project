"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getAvailableModels, ModelInfo } from "@/lib/api";

interface StepIdentityProps {
  name: string;
  description: string;
  model: string;
  onChange: (field: string, value: string) => void;
}

export function StepIdentity({ name, description, model, onChange }: StepIdentityProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);

  useEffect(() => {
    getAvailableModels().then(setModels).catch((err) => console.error("Error cargando modelos:", err));
  }, []);

  return (
    <div className="max-w-lg space-y-6">
      <div className="space-y-2">
        <Label htmlFor="wizard-name">Nombre *</Label>
        <Input
          id="wizard-name"
          value={name}
          onChange={(e) => onChange("name", e.target.value)}
          placeholder="Ej: Extractor de facturas CFDI"
        />
        <p className="text-xs text-muted-foreground">
          Un nombre descriptivo para identificar este extractor
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="wizard-description">Descripción</Label>
        <Input
          id="wizard-description"
          value={description}
          onChange={(e) => onChange("description", e.target.value)}
          placeholder="Ej: Extrae RFC, total y fecha de facturas mexicanas"
        />
        <p className="text-xs text-muted-foreground">
          Describe brevemente qué hace este extractor y para qué documentos se usa
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="wizard-model">Modelo</Label>
        <Select value={model} onValueChange={(v) => onChange("model", v)}>
          <SelectTrigger id="wizard-model">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {models.map((m) => (
              <SelectItem key={m.id} value={m.id} disabled={!m.is_available}>
                {m.name} ({m.tier}) - {m.cost_hint}
                {!m.is_available && " — Pronto"}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-xs text-muted-foreground">
          El modelo de IA que procesará los documentos
        </p>
      </div>
    </div>
  );
}
