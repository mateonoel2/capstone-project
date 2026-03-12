"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Lightbulb } from "lucide-react";

export function PromptTips() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border rounded-lg">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        <span className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-yellow-500" />
          Consejos para el prompt
        </span>
        {isOpen ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </button>
      {isOpen && (
        <div className="px-4 pb-3 text-sm text-gray-600 space-y-2">
          <ul className="list-disc list-inside space-y-1">
            <li>Se especifico sobre que tipo de documento se analizara</li>
            <li>Indica exactamente que campos extraer y donde suelen ubicarse</li>
            <li>Especifica el formato esperado (ej: &quot;18 digitos numericos&quot;)</li>
            <li>Incluye instrucciones para cuando un campo no se encuentre</li>
            <li>Usa &quot;No inventes informacion&quot; para evitar alucinaciones</li>
            <li>Menciona el idioma del documento si es relevante</li>
            <li>Describe variantes comunes del documento si las hay</li>
          </ul>
        </div>
      )}
    </div>
  );
}
