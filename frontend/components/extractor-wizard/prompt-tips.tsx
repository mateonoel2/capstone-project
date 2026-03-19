"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Lightbulb } from "lucide-react";
import { useT } from "@/lib/i18n";

export function PromptTips() {
  const [isOpen, setIsOpen] = useState(false);
  const t = useT();

  return (
    <div className="border rounded-lg">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        <span className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-yellow-500" />
          {t("promptTips.title")}
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
            {[0, 1, 2, 3, 4, 5, 6].map((i) => (
              <li key={i}>{t(`promptTips.tips.${i}`)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
