"use client";

import { useUsageQuota } from "@/lib/hooks";
import { useExtractionStore } from "@/lib/store";
import { useT } from "@/lib/i18n";

export function QuotaBanner() {
  const backendUser = useExtractionStore((s) => s.backendUser);
  const { data: quota } = useUsageQuota();
  const t = useT();

  if (!backendUser || backendUser.role !== "guest" || !quota || quota.unlimited) {
    return null;
  }

  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-xs text-amber-800 flex items-center gap-3">
      <span className="font-medium">{t("quota.guest")}</span>
      <span>
        {quota.extractions?.used}/{quota.extractions?.limit} {t("quota.extractions")}
      </span>
      <span className="text-amber-300">|</span>
      <span>
        {quota.extractors?.used}/{quota.extractors?.limit} {t("quota.extractors")}
      </span>
      <span className="text-amber-300">|</span>
      <span>
        {quota.ai_prompts?.used}/{quota.ai_prompts?.limit} {t("quota.aiPrompts")}
      </span>
    </div>
  );
}
