import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Lock, ToggleLeft } from "lucide-react";
import { VALIDATION_FIELD } from "./types";

interface ValidationFieldCardProps {
  description: string;
  onDescriptionChange: (desc: string) => void;
}

export function ValidationFieldCard({
  description,
  onDescriptionChange,
}: ValidationFieldCardProps) {
  return (
    <Card className="border-dashed">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Lock className="h-3.5 w-3.5" />
            Validación del documento
          </div>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <ToggleLeft className="h-3.5 w-3.5" />
            Sí/No
          </div>
        </div>
        <div className="grid gap-2">
          <div className="flex items-center gap-2">
            <Label className="text-xs text-muted-foreground shrink-0">
              Campo:
            </Label>
            <code className="text-xs bg-muted px-1.5 py-0.5 rounded">
              {VALIDATION_FIELD.name}
            </code>
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Instrucción para la IA
            </Label>
            <Input
              value={description}
              onChange={(e) => onDescriptionChange(e.target.value)}
              className="mt-1 text-sm"
              placeholder="Descripción de la validación..."
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
